import os
import random
import time
from collections.abc import AsyncGenerator, Generator
from multiprocessing import Process
from pathlib import Path

import httpx
import pytest
import typer
from asynctor.utils import Shell

PORT = random.randint(9000, 9999)


@pytest.fixture(scope="session", autouse=True)
def runserver() -> Generator[None]:
    if not Path("static").exists():
        Shell("fastcdn offline").run()
    cmd = f"fastcdn main.py --port={PORT}"
    env = {"FASTCDN_UVICORN": "1", "FASTCDN_NORELOAD": "1", **os.environ}
    p = Process(target=Shell(cmd, env=env).run)
    p.start()
    time.sleep(3)  # Wait for app to startup
    try:
        yield
    finally:
        p.terminate()
        leftover = f"ps aux|grep fastapi-cdn-host|grep 'port={PORT}'|grep -v grep"
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
    async with httpx.AsyncClient(base_url=f"http://localhost:{PORT}") as c:
        yield c
