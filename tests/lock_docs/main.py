from functools import partial

from fastapi import FastAPI, Request

import fastapi_cdn_host
from fastapi_cdn_host.utils import weekday_lock

app = FastAPI()
app_sync_lock = FastAPI()
app_change_lock_param = FastAPI()


def sync_lock(request: Request) -> None:
    return weekday_lock(request)


async def lock(request: Request) -> None:
    sync_lock(request)


fastapi_cdn_host.patch_docs(app, lock=lock)
fastapi_cdn_host.patch_docs(app_sync_lock, lock=sync_lock)
fastapi_cdn_host.patch_docs(
    app_change_lock_param, lock=partial(fastapi_cdn_host.weekday_lock, name="weekday")
)


@app.get("/")
@app_sync_lock.get("/")
@app_change_lock_param.get("/")
async def index():
    return "homepage"
