#!/usr/bin/env python
import subprocess
from contextlib import contextmanager
from datetime import datetime
from logging import getLogger
from pathlib import Path
from typing import Generator, Union

import typer
from typing_extensions import Annotated

app = typer.Typer()
logger = getLogger(__name__)


def run_shell(cmd: str) -> None:
    logger.info(f"--> {cmd}")
    subprocess.run(cmd, shell=True)


TEMPLATE = """
import fastapi_cdn_host
from {} import app

fastapi_cdn_host.patch_docs(app)
"""


def write_app(dest: Path, from_path: str) -> None:
    module = Path(from_path).stem
    size = dest.write_text(TEMPLATE.format(module).strip())
    logger.info(f"Create {dest} with {size=}")


@contextmanager
def patch_app(path: str, remove=True) -> Generator[Path, None, None]:
    ident = f"{datetime.now():%Y%m%d%H%M%S}"
    app_file = Path(f"app_{ident}.py")
    write_app(app_file, path)
    try:
        yield app_file
    finally:
        if remove:
            app_file.unlink()
            logger.info(f"Auto remove temp file: {app_file}")


@app.command()
def dev(
    path: Annotated[
        Path,
        typer.Argument(
            help="A path to a Python file or package directory (with [blue]__init__.py[/blue] files) containing a [bold]FastAPI[/bold] app. If not provided, a default set of paths will be tried."
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
    with patch_app(str(path), remove) as file:
        mode = "run" if prod else "dev"
        cmd = f"PYTHONPATH=. fastapi {mode} {file}"
        if port:
            cmd += f" --{port=}"
        run_shell(cmd)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
