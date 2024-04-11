# mypy: no-disallow-untyped-decorators
import pytest
from httpx import ASGITransport, AsyncClient
from main import app

from fastapi_cdn_host.client import (
    DEFAULT_ASSET_PATH,
    NORMAL_ASSET_PATH,
    CdnHostBuilder,
    CdnHostEnum,
    CdnHostItem,
    HttpSpider,
)


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


def test_cdn_host_item():
    url = "https://raw.githubusercontent.com/swagger-api/swagger-ui/v5.9.0/dist/swagger-ui.css"
    assert CdnHostItem(url).export() == (
        "https://raw.githubusercontent.com/swagger-api",
        ("/swagger-ui/v{version}/dist/", ""),
    )
    assert CdnHostItem("http://pri.com/").export() == ("http://pri.com", ("/", ""))
    assert CdnHostItem("http://pri.com/", None).export() == (
        "http://pri.com",
        ("/", DEFAULT_ASSET_PATH[-1]),
    )
    assert CdnHostItem("http://pri.com/", "http://redoc.com/redoc.js").export() == (
        "http://pri.com",
        ("/", "http://redoc.com/"),
    )
    assert (
        CdnHostItem.remove_filename("http://localhost:8000/a/b/c.js")
        == "http://localhost:8000/a/b/"
    )
    assert (
        CdnHostItem.remove_filename("http://localhost:8000/a/b/")
        == "http://localhost:8000/a/b/"
    )
    assert (
        CdnHostItem.remove_filename("http://localhost:8000/a/b")
        == "http://localhost:8000/a/b/"
    )
    with pytest.raises(ValueError):
        CdnHostItem("").export()


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    choices = CdnHostEnum.extend(
        ("https://lf9-cdn-tos.bytecdntp.com/cdn/expire-1-M", NORMAL_ASSET_PATH),
        CdnHostItem(
            "https://raw.githubusercontent.com/swagger-api/swagger-ui/v5.9.0/dist/swagger-ui.css"
        ),
    )
    urls = await CdnHostBuilder.sniff_the_fastest(choices)
    url_list = await HttpSpider.get_fast_hosts(
        CdnHostBuilder.build_race_data(list(choices))[0]
    )
    assert urls.css in url_list
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    response2 = await client.get("/redoc")
    text2 = response2.text
    assert response2.status_code == 200, text2
    if urls.js not in text:
        # Sometimes there are several cdn hosts that have good response speed.
        assert any(i in text for i in url_list)
    else:
        assert urls.js in text
        assert urls.css in text
        assert urls.redoc in text2
    response = await client.get("/app")
    assert response.status_code == 200
