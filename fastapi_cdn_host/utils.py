import calendar
import contextlib
import sys
from datetime import datetime
from typing import AsyncGenerator

from fastapi import HTTPException, Request, status
from httpx import ASGITransport, AsyncClient


@contextlib.asynccontextmanager
async def TestClient(
    app, base_url="http://test", **kw
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=base_url, **kw
    ) as c:
        yield c


def weekday_lock(request: Request, name="day") -> None:
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
