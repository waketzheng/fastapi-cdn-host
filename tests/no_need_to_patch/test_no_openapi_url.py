# mypy: no-disallow-untyped-decorators
import logging
from contextlib import contextmanager, redirect_stdout
from io import StringIO

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from main import app

from fastapi_cdn_host.client import StaticBuilder, monkey_patch_for_docs_ui

default_favicon_url = "https://fastapi.tiangolo.com/img/favicon.png"


@contextmanager
def capture_stdout():
    """Redirect sys.stdout to a new StringIO

    Example::
    ```py
        with capture_stdout() as stream:
            GitTag(message="", dry=True).run()
        assert "git tag -a" in stream.getvalue()
    ```
    """
    stream = StringIO()
    with redirect_stdout(stream):
        yield stream


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_api(client: AsyncClient):  # nosec
    response = await client.get("/app")
    assert response.status_code == 200


def test_log(caplog):
    caplog.set_level(logging.INFO)
    info = "API docs not activated, skip monkey patch."
    monkey_patch_for_docs_ui(FastAPI(docs_url=None, redoc_url=None))
    log_messages = [record.message for record in caplog.records]
    assert info in log_messages


def test_get_latest_one(tmp_path):
    (a := tmp_path / "a.txt").touch()
    (b := tmp_path / "b.txt").touch()
    StaticBuilder.get_latest_one([a, b]) == b
