#!/usr/bin/env python
from pathlib import Path

import uvicorn
from config import MY_CDN
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

import fastapi_cdn_host

app = FastAPI(title="FastAPI CDN host test")


@app.get("/", include_in_schema=False)
async def to_docs():
    return RedirectResponse("/docs")


@app.get("/app")
async def get_app(request: Request) -> dict:
    return {"routes": str(request.app.routes)}


fastapi_cdn_host.patch_docs(
    app,
    docs_cdn_host=(MY_CDN, "/"),
    favicon_url=MY_CDN + "/favicon.ico",
)


if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app", reload=True)
