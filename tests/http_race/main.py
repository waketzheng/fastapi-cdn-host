from datetime import datetime
from typing import Union

import anyio
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/sleep")
async def sleep(seconds: Union[int, float]):
    return await wait_for(seconds)


@app.get("/wait/{seconds}")
async def wait(seconds: Union[int, float]):
    return await wait_for(seconds)


@app.get("/delay/{seconds}")
async def delay(seconds: Union[int, float]):
    return await wait_for(seconds)


async def wait_for(seconds) -> dict:
    start = datetime.now()
    await anyio.sleep(seconds)
    end = datetime.now()
    return {"seconds": seconds, "start": start, "end": end}


@app.get("/error")
async def raise_exp():
    raise HTTPException(detail="foo", status_code=400)
