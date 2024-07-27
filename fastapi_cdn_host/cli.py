#!/usr/bin/env python
import os
import shlex
import subprocess  # nosec:B404
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Generator, Union

import anyio
import typer
from rich import print
from rich.progress import Progress, SpinnerColumn
from typing_extensions import Annotated

from .client import CdnHostBuilder, HttpSniff

app = typer.Typer()


def run_shell(cmd: str) -> None:
    print(f"--> {cmd}")
    command = shlex.split(cmd)
    cmd_env = None
    for i, c in enumerate(command):
        if "=" not in c:
            break
        name, value = c.split("=")
        if cmd_env is None:
            cmd_env = os.environ.copy()
        cmd_env[name] = value
    if i != 0:
        command = command[i:]
    subprocess.run(command, env=cmd_env)  # nosec:B603


TEMPLATE = """
#!/usr/bin/env python
'''This file is auto generated by fastapi_cdn_host.
Feel free to change or remove it.
'''
import fastapi_cdn_host
from {} import app

fastapi_cdn_host.patch_docs(app)

def _runserver() -> int:
    r = subprocess.run(['fastapi', 'dev', __file__])
    return r.returncode

if __name__ == '__main__':
    sys.exit(_runserver())
"""


def write_app(dest: Path, from_path: Union[str, Path]) -> None:
    module = Path(from_path).stem
    size = dest.write_text(TEMPLATE.format(module).strip())
    print(f"Create {dest} with {size=}")


@contextmanager
def patch_app(path: Union[str, Path], remove=True) -> Generator[Path, None, None]:
    ident = f"{datetime.now():%Y%m%d%H%M%S}"
    app_file = Path(f"app_{ident}.py")
    write_app(app_file, path)
    try:
        yield app_file
    finally:
        if remove:
            app_file.unlink()
            print(f"Auto remove temp file: {app_file}")


@asynccontextmanager
async def percentbar(
    msg: str, seconds=5, color: str = "cyan", transient=False
) -> AsyncGenerator[None, None]:
    """Progressbar with custom font color

    :param msg: prompt message.
    :param seconds: max seconds of tasks.
    :param color: font color，e.g.: 'blue'.
    :param transient: whether clean progressbar after finished.
    """
    total = seconds * 100

    async def play(progress, task, expected=1 / 2, thod=0.8) -> None:
        cost = seconds * expected
        quick = int(total * thod)
        delay = cost / quick
        for i in range(quick):
            await anyio.sleep(delay)
            progress.advance(task)
        cost = seconds - cost
        slow = total - quick
        delay = cost / slow
        for i in range(slow):
            await anyio.sleep(delay)
            progress.advance(task)

    with Progress(transient=transient) as progress:
        task = progress.add_task(f"[{color}]{msg}:", total=total)
        async with anyio.create_task_group() as tg:
            tg.start_soon(play, progress, task)
            yield
            tg.cancel_scope.cancel()
            progress.update(task, completed=total)


@contextmanager
def spinnerbar(msg, color="yellow", transient=True) -> Generator[None, None, None]:
    with Progress(
        SpinnerColumn(), *Progress.get_default_columns(), transient=transient
    ) as progress:
        progress.add_task(f"[{color}]{msg}...", total=None)
        yield


async def download_offline_assets(dirname="static") -> None:
    cwd = await anyio.Path.cwd()
    static_root = cwd / dirname
    if not await static_root.exists():
        await static_root.mkdir(parents=True)
        print(f"Directory {static_root} created.")
    else:
        async for p in static_root.glob("swagger-ui*.js"):
            relative_path = p.relative_to(cwd)
            print(f"{relative_path} already exists. abort!")
            return
    async with percentbar("Comparing cdn hosts response speed"):
        urls = await CdnHostBuilder.sniff_the_fastest()
    print("Result:", urls)
    with spinnerbar("Fetching files from cdn"):
        url_list = [urls.js, urls.css, urls.redoc]
        contents = await HttpSniff.bulk_fetch(url_list, get_content=True)
        for url, content in zip(url_list, contents):
            if not content:
                print(f"Failed to fetch content from {url}")
            else:
                path = static_root / Path(url).name
                size = await path.write_bytes(content)
                print(f"Write to {path} with {size=}")
    print("Done.")


@app.command()
def dev(
    path: Annotated[
        Path,
        typer.Argument(
            help="A path to a Python file or package directory (with [blue]__init__.py[/blue] file) containing a [bold]FastAPI[/bold] app. If not provided, a default set of paths will be tried."
        ),
    ],
    port: Annotated[
        Union[int, None],
        typer.Option(
            help="The port to serve on. You would normally have a termination proxy on top (another program) handling HTTPS on port [blue]443[/blue] and HTTP on port [blue]80[/blue], transferring the communication to your app."
        ),
    ] = None,
    remove: Annotated[
        bool,
        typer.Option(
            help="Whether remove the temp app_<time>.py file after server stopped."
        ),
    ] = True,
    prod: Annotated[
        bool,
        typer.Option(help="Whether enable production mode."),
    ] = False,
):
    if str(path) == "offline":
        # TODO: download assets to local
        anyio.run(download_offline_assets)
        return
    with patch_app(path, remove) as file:
        mode = "run" if prod else "dev"
        cmd = f"PYTHONPATH=. fastapi {mode} {file}"
        if port:
            cmd += f" --{port=}"
        run_shell(cmd)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
