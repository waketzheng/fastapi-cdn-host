#!/usr/bin/env python
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import fastapi_cdn_host
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

app = FastAPI(title="HTTP redirect center")
BASE_DIR = Path(__file__).parent.resolve()
STATIC_ROOT = BASE_DIR / "static"
# Uncomment the following the lines to auto download assets:
# if not STATIC_ROOT.exists():
#     import anyio
#     from fastapi_cdn_host.cli import download_offline_assets
#     anyio.run(download_offline_assets, STATIC_ROOT)
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


class ResponseModel(PostData):
    time: Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]


@app.post("/test", response_model=ResponseModel)
async def post_sth(data: PostData) -> dict:
    return data.model_dump()


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app)
