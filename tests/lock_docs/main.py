from functools import partial

from fastapi import FastAPI, Request

import fastapi_cdn_host
from fastapi_cdn_host.utils import (
    ParamLock,
    TodayLock,
    WeekdayLock,
    today_lock,
    weekday_lock,
)

app = FastAPI()
app_weekday = FastAPI()
app_weekday_class = FastAPI()
app_sync_lock = FastAPI()
app_change_lock_param = FastAPI()

app_today_lock = FastAPI()
app_today = FastAPI()
app_today_class = FastAPI()
app_today_param = FastAPI()
app_param_lock = FastAPI()


def sync_lock(request: Request) -> None:
    return weekday_lock(request, exclude_localhost=False)


async def lock(request: Request) -> None:
    sync_lock(request)


try:
    fastapi_cdn_host.patch_docs(app, lock=lock)
except FileNotFoundError:
    # Sometimes cache file was removed by unittest of `fastcdn offline`
    fastapi_cdn_host.patch_docs(app, lock=lock, cache=False)
fastapi_cdn_host.patch_docs(app_weekday, lock=weekday_lock)
fastapi_cdn_host.patch_docs(app_weekday_class, lock=WeekdayLock())
fastapi_cdn_host.patch_docs(app_sync_lock, lock=sync_lock)
fastapi_cdn_host.patch_docs(
    app_change_lock_param,
    lock=partial(
        fastapi_cdn_host.weekday_lock, name="weekday", exclude_localhost=False
    ),
)

fastapi_cdn_host.patch_docs(app_today_lock, lock=fastapi_cdn_host.today_lock)
fastapi_cdn_host.patch_docs(
    app_today, lock=partial(fastapi_cdn_host.today_lock, exclude_localhost=False)
)
fastapi_cdn_host.patch_docs(
    app_today_param, lock=partial(today_lock, name="date", exclude_localhost=False)
)
fastapi_cdn_host.patch_docs(app_today_class, lock=TodayLock(exclude_localhost=False))
fastapi_cdn_host.patch_docs(app_param_lock, lock=ParamLock(exclude_localhost=False))


@app.get("/")
@app_sync_lock.get("/")
@app_change_lock_param.get("/")
@app_today.get("/")
@app_today_param.get("/")
@app_today_class.get("/")
@app_param_lock.get("/")
async def index():
    return "homepage"


@app_today_lock.get("/")
@app_weekday.get("/")
async def homepage():
    return "foo"
