# mypy: no-disallow-untyped-decorators
import pytest
from httpx import AsyncClient
from main import app

from fastapi_cdn_host.client import CdnHostBuilder, CdnHostEnum


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    urls = await CdnHostBuilder.sniff_the_fastest(
        choices=CdnHostEnum.extend(
            (
                "https://cdn.bootcdn.net/ajax/libs",
                ("/swagger-ui/{version}/", ""),
            ),
            ("https://cdn.staticfile.org", ("/swagger-ui/{version}/", "")),
            (
                "https://lf9-cdn-tos.bytecdntp.com/cdn/expire-1-M",
                ("/swagger-ui/{version}/", ""),
            ),
        )
    )
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert urls.js in text
    assert urls.css in text
    response2 = await client.get("/redoc")
    text2 = response2.text
    assert response2.status_code == 200, text2
    assert urls.redoc in text2
    response = await client.get("/app")
    assert response.status_code == 200
