import os
import random
from collections.abc import AsyncGenerator, Generator
from multiprocessing import Process
from pathlib import Path

import httpx
import pytest
import typer
from asynctor.utils import Shell


class Option:
    _port: int = 0

    @classmethod
    def get_port(cls) -> int:
        if not cls._port:
            cls._port = random.randint(9000, 9999)
        return cls._port


@pytest.fixture(scope="session", autouse=True)
def runserver() -> Generator[None]:
    if not Path("static").exists():
        Shell("fastcdn offline").run()
    port = Option.get_port()
    cmd = f"fastcdn main.py --port={port}"
    env = {"FASTCDN_UVICORN": "1", "FASTCDN_NORELOAD": "1", **os.environ}
    p = Process(target=Shell(cmd, env=env).run)
    p.start()
    try:
        yield
    finally:
        p.terminate()
        leftover = f"ps aux|grep fastapi-cdn-host|grep 'port={port}'|grep -v grep"
        kill_ps = leftover + "| awk '{print $2}' |xargs -I {} kill -9 {}"
        if Shell(leftover).capture_output().strip():
            Shell(kill_ps).run()
        else:
            typer.secho("You may want to clean subprocess by:", fg=typer.colors.YELLOW)
            typer.secho(kill_ps, bold=True)
        for tmp_file in Path(__file__).parent.glob("app_*.py"):
            tmp_file.unlink()


@pytest.fixture(scope="module")
async def client() -> AsyncGenerator[httpx.AsyncClient]:
    port = Option.get_port()
    async with httpx.AsyncClient(base_url=f"http://localhost:{port}") as c:
        yield c
