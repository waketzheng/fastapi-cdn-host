# mypy: no-disallow-untyped-decorators
import logging

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from main import app

from fastapi_cdn_host.client import StaticBuilder, monkey_patch_for_docs_ui

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
