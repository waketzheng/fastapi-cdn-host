# mypy: no-disallow-untyped-decorators
import pytest
from httpx import AsyncClient
from main import app

from fastapi_cdn_host.client import NORMAL_ASSET_PATH, CdnHostBuilder, CdnHostEnum


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


async def _get_cdn_host():
    return await CdnHostBuilder.sniff_the_fastest(
        choices=CdnHostEnum.extend(
            ("https://lf9-cdn-tos.bytecdntp.com/cdn/expire-1-M", NORMAL_ASSET_PATH),
            (
                "https://raw.githubusercontent.com/swagger-api/swagger-ui",
                ("/v{version}/dist/", ""),
            ),
        )
    )


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    urls = await _get_cdn_host()
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    if urls.js not in text:
        # Sometimes there are several cdn hosts that have good response speed.
        for _ in range(3):
            new_urls = await _get_cdn_host()
            if new_urls.js != urls.js:
                urls = new_urls
                break
    assert urls.js in text
    assert urls.css in text
    response2 = await client.get("/redoc")
    text2 = response2.text
    assert response2.status_code == 200, text2
    assert urls.redoc in text2
    response = await client.get("/app")
    assert response.status_code == 200
