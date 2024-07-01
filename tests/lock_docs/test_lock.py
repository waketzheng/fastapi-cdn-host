# mypy: no-disallow-untyped-decorators
import random
import sys
from datetime import datetime

import httpx
import pytest
from main import (
    app,
    app_change_lock_param,
    app_param_lock,
    app_sync_lock,
    app_today,
    app_today_class,
    app_today_param,
)

from fastapi_cdn_host.utils import TestClient


@pytest.fixture(scope="module")
async def client_app():
    async with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
async def client_sync_lock():
    async with TestClient(app_sync_lock) as c:
        yield c


@pytest.fixture(scope="module")
async def client_change_param_name():
    async with TestClient(app_change_lock_param) as c:
        yield c


class LockTester:
    def get_day_value(self) -> str:
        return ""

    async def request_locked(self, client: httpx.AsyncClient, param_name="day"):
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
        day = self.get_day_value()
        response = await client.get(f"/docs?{param_name}={day}")
        assert response.status_code == 200
        response = await client.get(f"/redoc?{param_name}={day}")
        assert response.status_code == 200
        response = await client.get("/")
        assert response.status_code == 200
        assert response.text == '"homepage"'


class TestWeekdayLock(LockTester):
    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    def get_day_value(self) -> str:
        return self.weekdays[datetime.now().weekday()]

    @pytest.mark.anyio
    async def test_lock(self, client_app: httpx.AsyncClient):
        await self.request_locked(client_app)

    @pytest.mark.anyio
    async def test_sync_lock(self, client_sync_lock: httpx.AsyncClient):
        await self.request_locked(client_sync_lock)

    @pytest.mark.anyio
    async def test_change_lock_param_name(
        self, client_change_param_name: httpx.AsyncClient
    ):
        await self.request_locked(client_change_param_name, "weekday")


@pytest.fixture(scope="module")
async def client_today():
    async with TestClient(app_today) as c:
        yield c


@pytest.fixture(scope="module")
async def client_today_class():
    async with TestClient(app_today_class) as c:
        yield c


@pytest.fixture(scope="module")
async def client_today_param():
    async with TestClient(app_today_param) as c:
        yield c


@pytest.fixture(scope="module")
async def client_param_lock():
    async with TestClient(app_param_lock) as c:
        yield c


class TestTodayLock(LockTester):
    def get_day_value(self) -> str:
        return str(datetime.now().date())

    @pytest.mark.anyio
    async def test_today_lock(self, client_today: httpx.AsyncClient):
        await self.request_locked(client_today)

    @pytest.mark.anyio
    async def test_today_class(self, client_today_class: httpx.AsyncClient):
        await self.request_locked(client_today_class)

    @pytest.mark.anyio
    async def test_today_param(self, client_today_param: httpx.AsyncClient):
        await self.request_locked(client_today_param, "date")


class TestParamLock(LockTester):
    def get_day_value(self) -> str:
        return str(random.randint(1, 100))

    @pytest.mark.anyio
    async def test_param_lock(self, client_param_lock: httpx.AsyncClient):
        await self.request_locked(client_param_lock, "a")
        await self.request_locked(client_param_lock, "a")
        await self.request_locked(client_param_lock, "a")
