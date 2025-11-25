import random
from collections.abc import AsyncGenerator, Generator
from multiprocessing import Process

import httpx
import pytest
from asynctor.utils import Shell

PORT = random.randint(9000, 9999)


@pytest.fixture(scope="session", autouse=True)
def runserver() -> Generator[None]:
    cmd = f"fastcdn main.py --port={PORT}"
    p = Process(target=Shell(cmd).run)
    p.start()
    try:
        yield
    finally:
        p.terminate()


@pytest.fixture(scope="module")
async def client() -> AsyncGenerator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=f"http://localhost:{PORT}") as c:
        yield c
