# mypy: no-disallow-untyped-decorators
import re

import pytest
from httpx import AsyncClient
from main import app

from fastapi_cdn_host.client import CdnHostBuilder
from fastapi_cdn_host.utils import TestClient

default_favicon_url = "https://fastapi.tiangolo.com/img/favicon.png"


@pytest.fixture(scope="module")
async def client():
    async with TestClient(app) as c:
        yield c


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert default_favicon_url in text
    swagger_ui = CdnHostBuilder.swagger_files
    css = re.search(rf'href="(.*?/static/{swagger_ui["css"]})"', text)
    js = re.search(rf'src="(.*?/static/{swagger_ui["js"]})"', text)
    assert css and js
    css_url = css.group(1)
    js_url = css.group(1)
    response = await client.get(css_url)
    assert response.status_code == 200, f"{response.url=};{response.text=}"
    response = await client.get(js_url)
    assert response.status_code == 200, response.text
    response = await client.get("/redoc")
    assert '"/api/v1/static/redoc' in response.text
    assert response.status_code == 200
    response = await client.get("/app")
    assert response.status_code == 200
