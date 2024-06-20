# mypy: no-disallow-untyped-decorators
import sys
from datetime import datetime

import httpx
import pytest
from main import app, app_change_lock_param, app_sync_lock

from fastapi_cdn_host.utils import TestClient


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
async def client_sync_lock():
    async with TestClient(
        app_sync_lock,
        base_url="http://sync.test.com",
    ) as c:
        yield c


@pytest.fixture(scope="module")
async def client_change_param_name():
    async with TestClient(
        app_change_lock_param,
        base_url="http://lock.test.com",
    ) as c:
        yield c


class TestLock:
    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    @pytest.mark.anyio
    async def test_lock(self, client: httpx.AsyncClient):
        await self.request_locked(client)

    async def request_locked(self, client, param_name="day"):
        status_code = 418 if sys.version_info >= (3, 9) else 417
        response = await client.get("/")
        assert response.status_code == 200
        assert response.text == '"homepage"'
        response = await client.get("/docs")
        assert response.status_code == status_code
        assert response.json()["detail"] in ("I'm a Teapot", "Expectation Failed")
        response = await client.get("/redoc")
        assert response.status_code == status_code
        assert response.json()["detail"] in ("I'm a Teapot", "Expectation Failed")
        day = self.weekdays[datetime.now().weekday()]
        response = await client.get(f"/docs?{param_name}={day}")
        assert response.status_code == 200
        response = await client.get(f"/redoc?{param_name}={day}")
        assert response.status_code == 200
        response = await client.get("/")
        assert response.status_code == 200
        assert response.text == '"homepage"'

    @pytest.mark.anyio
    async def test_sync_lock(self, client_sync_lock: httpx.AsyncClient):
        await self.request_locked(client_sync_lock)

    @pytest.mark.anyio
    async def test_change_lock_param_name(
        self, client_change_param_name: httpx.AsyncClient
    ):
        await self.request_locked(client_change_param_name, "weekday")
