import calendar
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

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


def weekday_lock(request: Request, name="day") -> None:
    """A simple docs lock function.

    Usage::
        >>> import fastapi_cdn_host
        >>> from fastapi import FastAPI
        >>> app = FastAPI(openapi_url='/v1/api.json')
        >>> fastapi_cdn_host.patch_docs(app, lock=fastapi_cdn_host.weekday_lock)
    """
    if (
        not (d := request.query_params.get(name))
        or (weekday := getattr(calendar, d.upper(), None)) is None
        or (weekday != datetime.now().weekday())
    ):
        status_code = (
            status.HTTP_418_IM_A_TEAPOT
            if sys.version_info >= (3, 9)
            else status.HTTP_417_EXPECTATION_FAILED
        )
        raise HTTPException(status_code=status_code)
