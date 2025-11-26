import subprocess
from contextlib import contextmanager
from multiprocessing import Process

import pytest
from config import MY_CDN, PORT
from httpx import AsyncClient
from main import app, app2

from fastapi_cdn_host.utils import TestClient


def http_server(port: int):
    subprocess.run(["pdm", "run", "python", "-m", "http.server", str(port)])


@contextmanager
def media_server(port=PORT):
    p = Process(target=http_server, args=(port,))
    p.start()
    yield
    p.terminate()


@pytest.fixture(scope="session", autouse=True)
def start_media_server():
    with media_server():
        yield


@pytest.fixture(scope="module")
async def client():
    async with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
async def client2():
    async with TestClient(app2) as c:
        yield c


class Expected:
    css_url = MY_CDN + "/swagger-ui.css"
    js_url = MY_CDN + "/swagger-ui-bundle.js"
    redoc_url = MY_CDN + "/redoc.standalone.js"
    favicon_url = MY_CDN + "/fast-dev-cli.ico"


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    await _run_tests(client)


@pytest.mark.anyio
async def test_docs2(client2: AsyncClient):  # nosec
    await _run_tests(client2)


async def _run_tests(client):
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert f'"{Expected.favicon_url}"' in text
    assert f'"{Expected.css_url}"' in text
    assert f'"{Expected.js_url}"' in text
    response = await client.get("/redoc")
    text = response.text
    assert response.status_code == 200, text
    assert f'"{Expected.redoc_url}"' in text
    response = await client.get("/app")
    assert response.status_code == 200
