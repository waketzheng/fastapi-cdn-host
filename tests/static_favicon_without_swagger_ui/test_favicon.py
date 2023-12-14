# mypy: no-disallow-untyped-decorators
import pytest
from httpx import AsyncClient
from main import app

from fastapi_cdn_host.client import CdnHostBuilder

default_favicon_url = "https://fastapi.tiangolo.com/img/favicon.png"


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
    assert default_favicon_url not in text
    assert '"/static/favicon.ico"' in text
    urls = await CdnHostBuilder.sniff_the_fastest()
    assert f'"{urls.js}"' in text
    assert f'"{urls.css}"' in text
    response2 = await client.get("/redoc")
    text2 = response2.text
    assert response2.status_code == 200, text2
    assert f'"{urls.redoc}"' in text2
    response = await client.get("/static/favicon.ico")
    assert response.status_code == 200
    response = await client.get("/app")
    assert response.status_code == 200
