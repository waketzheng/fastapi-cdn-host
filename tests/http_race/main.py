from __future__ import annotations

import anyio
from asynctor import Timer
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/sleep")
async def sleep(seconds: float):
    return await wait_for(seconds)


@app.get("/wait/{seconds}")
async def wait(seconds: float):
    return await wait_for(seconds)


@app.get("/delay/{seconds}")
async def delay(seconds: float):
    return await wait_for(seconds)


async def wait_for(seconds) -> dict:
    start = Timer.now()
    await anyio.sleep(seconds)
    end = Timer.now()
    return {"seconds": seconds, "start": start, "end": end}


@app.get("/error")
async def raise_exp():
    raise HTTPException(detail="foo", status_code=400)
