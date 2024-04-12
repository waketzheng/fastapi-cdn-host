import contextlib

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@contextlib.asynccontextmanager
async def TestClient(app, base_url="http://test", **kw):
    async with AsyncClient(transport=ASGITransport(app), base_url=base_url, **kw) as c:
        yield c


@pytest.fixture(scope="session")
async def client():
    async with TestClient(app) as c:
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
    response = await client.post("/test", json={"a": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == {"a": 1}
    assert "headers" in data and "path" in data
