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
    swagger_ui = CdnHostBuilder.swagger_files
    js_url = "/api/v1/static/" + swagger_ui["js"]
    css_url = "/api/v1/static/" + swagger_ui["css"]
    response = await client.get(css_url)
    assert response.status_code == 404, f"{response.url=};{response.text=}"
    response = await client.get(js_url)
    assert response.status_code == 404, response.text
    response = await client.get(css_url.replace("/api/v1", ""))
    assert response.status_code == 200, f"{response.url=};{response.text=}"
    response = await client.get(js_url.replace("/api/v1", ""))
    assert response.status_code == 200, response.text
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert default_favicon_url in text
    assert f'"{js_url}"' in text
    assert f'"{css_url}"' in text
    response = await client.get("/redoc")
    text = response.text
    assert response.status_code == 200, text
    assert '"/api/v1/static/redoc' in text
    response = await client.get("/app")
    assert response.status_code == 200
