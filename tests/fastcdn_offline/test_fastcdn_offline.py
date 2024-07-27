# mypy: no-disallow-untyped-decorators
import pytest
from httpx import AsyncClient

from fastapi_cdn_host.client import CdnHostBuilder, HttpSniff
from fastapi_cdn_host.utils import TestClient

default_favicon_url = "https://fastapi.tiangolo.com/img/favicon.png"


@pytest.fixture(scope="module")
async def client():
    from main import app

    async with TestClient(app) as c:
        yield c


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    swagger_ui = CdnHostBuilder.swagger_files
    js_url = "/static/" + swagger_ui["js"]
    css_url = "/static/" + swagger_ui["css"]
    response = await client.get(css_url)
    assert response.status_code == 200, f"{response.url=};{response.text=}"
    response = await client.get(js_url)
    assert response.status_code == 200, response.text
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert default_favicon_url in text
    assert js_url in text
    assert css_url in text
    response = await client.get("/redoc")
    text = response.text
    assert response.status_code == 200, text
    assert "/static/redoc" in text
    response = await client.get("/app")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_try_cache():
    url = "http://not.exist.url.foo"
    results = [None]
    async with AsyncClient(timeout=0.3) as c:
        await HttpSniff.fetch(c, url, results, 0)
        assert results[0] is None
        HttpSniff.cached[url] = b"content"
        await HttpSniff.fetch(c, url, results, 0, try_cache=True)
        assert results[0] == b"content"
        rs = await HttpSniff.bulk_fetch([url], get_content=True)
        assert rs == results
