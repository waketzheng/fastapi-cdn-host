# mypy: no-disallow-untyped-decorators
import pytest
from httpx import ASGITransport, AsyncClient
from main import app

from fastapi_cdn_host.client import CdnHostBuilder, CdnHostEnum, HttpSpider

default_favicon_url = "https://fastapi.tiangolo.com/img/favicon.png"


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    urls = await CdnHostBuilder.sniff_the_fastest()
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert default_favicon_url in text
    if urls.js not in text:
        # Sometimes there are several cdn hosts that have good response speed.
        url_list = await HttpSpider.get_fast_hosts(
            CdnHostBuilder.build_race_data(list(CdnHostEnum))[0]
        )
        assert urls.css in url_list
        assert any(i in text for i in url_list)
    else:
        assert urls.js in text
        assert urls.css in text
    response2 = await client.get("/redoc")
    text2 = response2.text
    assert response2.status_code == 200, text2
    assert urls.redoc in text2
    response = await client.get("/app")
    assert response.status_code == 200
