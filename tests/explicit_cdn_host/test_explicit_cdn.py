# mypy: no-disallow-untyped-decorators
import pytest
from httpx import AsyncClient
from main import app

from fastapi_cdn_host import CdnHostEnum
from fastapi_cdn_host.utils import TestClient


@pytest.fixture(scope="module")
async def client():
    async with TestClient(app) as c:
        yield c


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    host = str(CdnHostEnum.unpkg.value)
    css_url = host + "/swagger-ui-dist@5.9.0/swagger-ui.css"
    js_url = host + "/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"
    redoc_url = host + "/redoc@next/bundles/redoc.standalone.js"
    favicon_url = host + "/favicon.ico"
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert f'"{favicon_url}"' not in text
    assert f'"{css_url}"' in text
    assert f'"{js_url}"' in text
    response = await client.get("/redoc")
    text = response.text
    assert response.status_code == 200, text
    assert f'"{redoc_url}"' in text
    response = await client.get("/app")
    assert response.status_code == 200
