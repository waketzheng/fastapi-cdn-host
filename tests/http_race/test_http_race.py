# mypy: no-disallow-untyped-decorators
import time

import pytest
from httpx import AsyncClient
from main import app
from utils import UvicornServer

from fastapi_cdn_host.client import HttpSniff
from fastapi_cdn_host.utils import TestClient

try:
    from asynctor import timeit
except ImportError:

    def timeit(f):  # type:ignore
        return f


@pytest.fixture(scope="module")
async def client():
    async with TestClient(app) as c:
        yield c


@pytest.mark.anyio
async def test_fetch(client: AsyncClient):
    timestamp = time.time()
    results = [timestamp]
    await HttpSniff.fetch(client, "/error", results, 0)
    assert results[0] == timestamp
    await HttpSniff.fetch(client, "/sleep?seconds=0.1", results, 0)
    assert results[0] != timestamp
    timestamp2 = time.time()
    results = [timestamp2]
    async with AsyncClient(base_url=client.base_url, timeout=0.1) as c:
        await HttpSniff.fetch(c, "/sleep?seconds=0.2", results, 0)
    assert results[0] == timestamp2
    async with AsyncClient(base_url=client.base_url, timeout=0.1) as c:
        await HttpSniff.fetch(c, "/not-exist", results, 0)
    assert results[0] == timestamp2


@pytest.mark.anyio
async def test_find():
    waits = (0.4, 0.2, 0.5)
    paths = ("sleep?seconds={}", "wait/{}", "delay/{}")
    host = "http://127.0.0.1:8000/"
    with UvicornServer().run_in_thread():
        urls = [host + path.format(seconds) for seconds, path in zip(waits, paths)]
        fastest = await timeit(HttpSniff.find_fastest_host)(urls, total_seconds=0.1)
        assert fastest == urls[0]
        fastest = await timeit(HttpSniff.find_fastest_host)(urls, loop_interval=0.1)
        assert fastest == urls[waits.index(min(waits))]
