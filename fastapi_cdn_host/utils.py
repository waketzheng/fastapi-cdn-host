from __future__ import annotations

import calendar
import sys
from collections.abc import AsyncGenerator
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status
from httpx import ASGITransport, AsyncClient
from typing_extensions import TypeAlias

TestClientType: TypeAlias = AsyncGenerator[AsyncClient, None]


class TestClient(AsyncClient):
    """Async test client

    Example::

    ```py
    from main import app

    assert isinstance(app, FastAPI)

    @pytest.fixture(scope='session')
    async def client() -> TestClientType:
        async with TestClient(app) as c:
            yield c
    ```
    """

    __test__ = False

    def __init__(self, app: FastAPI, base_url="http://test", **kw) -> None:
        transport = ASGITransport(app=app)
        super().__init__(transport=transport, base_url=base_url, **kw)


class ParamLock:
    param_name: str = "a"

    @staticmethod
    def validate(value: str) -> bool:
        return True

    @classmethod
    def check_param(cls, request: Request, name: str, exclude_localhost=True) -> None:
        if exclude_localhost and getattr(request.client, "host", "") == "127.0.0.1":
            return
        if not (d := request.query_params.get(name)) or not cls.validate(d):
            status_code = (
                status.HTTP_418_IM_A_TEAPOT
                if sys.version_info >= (3, 9)
                else status.HTTP_417_EXPECTATION_FAILED
            )
            raise HTTPException(status_code=status_code)

    def __init__(self, name: str | None = None, exclude_localhost=True) -> None:
        if name is None:
            name = self.param_name
        self.name = name
        self.exclude_localhost = exclude_localhost

    def __call__(self, request: Request) -> None:
        self.check_param(request, self.name, self.exclude_localhost)


class WeekdayLock(ParamLock):
    """Check whether docs query param.

    Usage::
        >>> import fastapi_cdn_host
        >>> from fastapi import FastAPI
        >>> app = FastAPI(openapi_url='/v1/api.json')
        >>> fastapi_cdn_host.patch_docs(app, lock=fastapi_cdn_host.utils.WeekdayLock())
    """

    param_name = "day"

    @staticmethod
    def validate(value: str) -> bool:
        return (weekday := getattr(calendar, value.upper(), None)) is not None and (
            weekday == datetime.now().weekday()
        )


class TodayLock(WeekdayLock):
    """Check whether docs query param.

    Usage::
        >>> import fastapi_cdn_host
        >>> from fastapi import FastAPI
        >>> app = FastAPI(openapi_url='/v1/api.json')
        >>> fastapi_cdn_host.patch_docs(app, lock=fastapi_cdn_host.utils.TodayLock())
    """

    @staticmethod
    def validate(value: str) -> bool:
        return value == str(datetime.now().date())


def weekday_lock(request: Request, name="day", exclude_localhost=True) -> None:
    """Check docs/ query contains `day` param with value of today's weekday, e.g.: Monday.

    Usage::
        >>> import fastapi_cdn_host
        >>> from fastapi import FastAPI
        >>> app = FastAPI(openapi_url="/v1/api.json")
        >>> fastapi_cdn_host.patch_docs(app, lock=fastapi_cdn_host.weekday_lock)
    """
    WeekdayLock(name, exclude_localhost)(request)


def today_lock(request: Request, name="day", exclude_localhost=True) -> None:
    """Check docs query param contains `day` and its value is today.

    Usage::
        >>> import fastapi_cdn_host
        >>> from fastapi import FastAPI
        >>> app = FastAPI(openapi_url='/v1/api.json')
        >>> fastapi_cdn_host.patch_docs(app, lock=fastapi_cdn_host.today_lock)
    """
    TodayLock(name, exclude_localhost)(request)
