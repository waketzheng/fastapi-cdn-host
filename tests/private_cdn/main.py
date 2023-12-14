#!/usr/bin/env python
from config import MY_CDN
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from fastapi_cdn_host import monkey_patch_for_docs_ui

app = FastAPI(title="FastAPI CDN host test")


@app.get("/", include_in_schema=False)
async def to_docs():
    return RedirectResponse("/docs")


@app.get("/app")
async def get_app(request: Request) -> dict:
    return {"routes": str(request.app.routes)}


monkey_patch_for_docs_ui(
    app,
    docs_cdn_host=(MY_CDN, ("/swagger-ui@latest/", "/redoc/next/")),
    favicon_url=MY_CDN + "/favicon.ico",
)
