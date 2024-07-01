import calendar
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator, Optional

from fastapi import HTTPException, Request, status
from httpx import ASGITransport, AsyncClient


@asynccontextmanager
async def TestClient(
    app, base_url="http://test", **kw
) -> AsyncGenerator[AsyncClient, None]:
    """Async test client

    Usage::
        >>> from main import app
        >>> @pytest.fixture(scope='session')
        ... async def client() -> AsyncClient:
        ...     async with TestClient(app) as c:
        ...         yield c
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=base_url, **kw) as c:
        yield c


class ParamLock:
    param_name: str = "a"

    @staticmethod
    def validate(value: str) -> bool:
        return True

    @classmethod
    def check_param(cls, request: Request, name: str) -> None:
        if not (d := request.query_params.get(name)) or not cls.validate(d):
            status_code = (
                status.HTTP_418_IM_A_TEAPOT
                if sys.version_info >= (3, 9)
                else status.HTTP_417_EXPECTATION_FAILED
            )
            raise HTTPException(status_code=status_code)

    def __init__(self, name: Optional[str] = None) -> None:
        if name is None:
            name = self.param_name
        self.name = name

    def __call__(self, request: Request) -> None:
        self.check_param(request, self.name)


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


def weekday_lock(request: Request, name="day") -> None:
    """Check docs/ query contains `day` param with value of today's weekday, e.g.: Monday.

    Usage::
        >>> import fastapi_cdn_host
        >>> from fastapi import FastAPI
        >>> app = FastAPI(openapi_url='/v1/api.json')
        >>> fastapi_cdn_host.patch_docs(app, lock=fastapi_cdn_host.weekday_lock)
    """
    WeekdayLock(name)(request)


def today_lock(request: Request, name="day") -> None:
    """Check docs query param contains `day` and its value is today.

    Usage::
        >>> import fastapi_cdn_host
        >>> from fastapi import FastAPI
        >>> app = FastAPI(openapi_url='/v1/api.json')
        >>> fastapi_cdn_host.patch_docs(app, lock=fastapi_cdn_host.today_lock)
    """
    TodayLock(name)(request)
