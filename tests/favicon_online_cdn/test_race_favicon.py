# mypy: no-disallow-untyped-decorators
import pytest
from httpx import AsyncClient
from main import app

from fastapi_cdn_host.client import CdnHostBuilder, CdnHostEnum, HttpSniff

try:
    from asynctor import timeit
except ImportError:

    def timeit(f):  # type:ignore
        return f


from fastapi_cdn_host.utils import TestClient


@pytest.fixture(scope="module")
async def client():
    async with TestClient(app) as c:
        yield c


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    if timeit is None:
        urls = await CdnHostBuilder.sniff_the_fastest()
    else:
        urls = await timeit(CdnHostBuilder.sniff_the_fastest)()
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    response2 = await client.get("/redoc")
    text2 = response2.text
    assert response2.status_code == 200, text2
    assert '"https://ubuntu.com/favicon.ico"' in text
    if urls.js not in text:
        # Sometimes there are several cdn hosts that have good response speed.
        url_list = await HttpSniff.get_fast_hosts(
            CdnHostBuilder.build_race_data(list(CdnHostEnum))[0]
        )
        assert urls.css in url_list
        assert any(i in text for i in url_list)
    else:
        assert urls.js in text
        assert urls.css in text
        assert urls.redoc in text2
    response = await client.get("/app")
    assert response.status_code == 200
