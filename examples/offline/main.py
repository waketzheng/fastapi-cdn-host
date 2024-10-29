#!/usr/bin/env python
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

import fastapi_cdn_host

app = FastAPI(title="HTTP redirect center")
BASE_DIR = Path(__file__).parent.resolve()
STATIC_ROOT = BASE_DIR / "static"
# Uncomment the following the lines to auto download assets:
# if not STATIC_ROOT.exists():
#     subprocess.run(["fastcdn", "offline"])
fastapi_cdn_host.patch_docs(app, STATIC_ROOT)


@app.get("/", include_in_schema=False)
async def to_docs():
    return RedirectResponse("/docs")


@app.get("/app")
async def get_app(request: Request) -> dict:
    return {"routes": str(request.app.routes)}


class PostData(BaseModel):
    a: str
    b: int


@app.post("/test")
async def post_sth(data: PostData) -> dict:
    return data.model_dump()


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app)
