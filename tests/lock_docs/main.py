import calendar
import sys
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status

import fastapi_cdn_host

app = FastAPI()
app_sync_lock = FastAPI()


def sync_lock(request: Request) -> None:
    if (
        not (d := request.query_params.get("day"))
        or (weekday := getattr(calendar, d.upper(), None)) is None
        or (weekday != datetime.now().weekday())
    ):
        status_code = (
            status.HTTP_418_IM_A_TEAPOT
            if sys.version_info >= (3, 9)
            else status.HTTP_417_EXPECTATION_FAILED
        )
        raise HTTPException(status_code=status_code)


async def lock(request: Request) -> None:
    sync_lock(request)


fastapi_cdn_host.patch_docs(app, lock=lock)
fastapi_cdn_host.patch_docs(app_sync_lock, lock=sync_lock)


@app.get("/")
@app_sync_lock.get("/")
async def index():
    return "homepage"
