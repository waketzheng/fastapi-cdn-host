# mypy: no-disallow-untyped-decorators
import pytest
from httpx import AsyncClient

from fastapi_cdn_host.client import CdnHostBuilder


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
    assert js_url in text
    assert css_url in text
    response = await client.get("/redoc")
    text = response.text
    assert response.status_code == 200, text
    assert "/static/redoc" in text
    response = await client.get("/app")
    assert response.status_code == 200
