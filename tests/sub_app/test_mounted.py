# mypy: no-disallow-untyped-decorators
import re

import pytest
from httpx import AsyncClient
from main import app

from fastapi_cdn_host.client import CdnHostBuilder, CdnHostEnum, HttpSniff
from fastapi_cdn_host.utils import TestClient

default_favicon_url = "https://fastapi.tiangolo.com/img/favicon.png"


@pytest.fixture(scope="module")
async def client():
    async with TestClient(app) as c:
        yield c


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    response = await client.get("/subapi/sub")
    text = response.text
    assert response.status_code == 200, text
    assert "Hello World from sub API" in text
    response = await client.get("/v1/")
    text = response.text
    assert response.status_code == 200, text
    assert text == "Hello, World from Flask!"
    response = await client.get("/static/a.txt")
    text = response.text
    assert response.status_code == 200, text
    urls = await CdnHostBuilder.sniff_the_fastest()
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert default_favicon_url in text
    response2 = await client.get("/redoc")
    text2 = response2.text
    assert response2.status_code == 200, text2
    if urls.js not in text:
        # Sometimes there are several cdn hosts that have good response speed.
        url_list = await HttpSniff.get_fast_hosts(
            CdnHostBuilder.build_race_data(list(CdnHostEnum))[0]
        )
        assert urls.css in url_list
        assert any(i in text for i in url_list)
        for url in url_list:
            host = url.split("://")[-1].split("/")[0]
            pattern = rf'src=".*{host}[\w/.-]+redoc.*"'
            if m := re.search(pattern, text2):
                print(f"{m.group() = }")
                break
        else:
            src_urls = re.findall(r'src="[^"]*redoc[^"]*"', text2)
            print(f"{src_urls = }")
            print(f"{url_list = }")
    else:
        assert urls.js in text
        assert urls.css in text
        assert urls.redoc in text2
    response = await client.get("/app")
    assert response.status_code == 200
