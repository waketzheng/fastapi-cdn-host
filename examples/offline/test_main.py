import sys
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from main import app

if sys.version_info >= (3, 10):
    from asynctor.utils import client_manager
else:
    from contextlib import asynccontextmanager

    from httpx import ASGITransport

    @asynccontextmanager
    async def client_manager(app, base_url="http://test", **kw):
        kw.pop("mount_lifespan", None)
        kw.update(transport=ASGITransport(app), base_url=base_url)
        async with AsyncClient(**kw) as c:
            yield c


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with client_manager(app, mount_lifespan=False) as c:
        yield c


@pytest.mark.anyio
async def test_home(client: AsyncClient):
    response = await client.get("/")
    response2 = await client.get("")
    assert response.status_code == 307
    assert response.has_redirect_location
    req = response.next_request
    assert req and req.url.path == "/docs"
    assert response2.status_code == 307
    assert response2.has_redirect_location
    req = response2.next_request
    assert req and req.url.path == "/docs"


@pytest.mark.anyio
async def test_get(client: AsyncClient):
    response = await client.get("/app")
    assert response.status_code == 200
    assert isinstance(response.json()["routes"], str)


@pytest.mark.anyio
async def test_post(client: AsyncClient):
    response = await client.post("/test", json={"a": "1", "b": 2})
    assert response.status_code == 200
    data = response.json()
    assert data == {"a": "1", "b": 2}
