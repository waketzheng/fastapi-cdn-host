# mypy: no-disallow-untyped-decorators
import pytest
from httpx import AsyncClient
from main import app

from fastapi_cdn_host.client import CdnHostBuilder


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert '"https://ubuntu.com/favicon.ico"' in text
    urls = await CdnHostBuilder.sniff_the_fastest()
    assert urls.js in text
    assert urls.css in text
    response2 = await client.get("/redoc")
    text2 = response2.text
    assert response2.status_code == 200, text2
    assert urls.redoc in text2
