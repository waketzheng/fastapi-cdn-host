# mypy: no-disallow-untyped-decorators
import sys
from pathlib import Path

import pytest
from config import MY_CDN, PORT
from httpx import AsyncClient
from main import app

try:
    from tests.http_race.utils import UvicornServer
except ImportError:
    _path = Path(__file__).parent.parent / "http_race"
    sys.path.append(_path.as_posix())
    from utils import UvicornServer  # type: ignore[no-redef]


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    css_url = MY_CDN + "/swagger-ui.css"
    js_url = MY_CDN + "/swagger-ui-bundle.js"
    redoc_url = MY_CDN + "/redoc.standalone.js"
    favicon_url = MY_CDN + "/favicon.ico"
    with UvicornServer("media_server:app", port=PORT).run_in_thread():
        response = await client.get("/docs")
        text = response.text
        assert response.status_code == 200, text
        assert f'"{favicon_url}"' in text
        assert f'"{css_url}"' in text
        assert f'"{js_url}"' in text
        response = await client.get("/redoc")
        text = response.text
        assert response.status_code == 200, text
        assert f'"{redoc_url}"' in text
        response = await client.get("/app")
        assert response.status_code == 200
