#!/usr/bin/env python
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from fastapi_cdn_host import monkey_patch_for_docs_ui

app = FastAPI(title="FastAPI CDN host test", root_path="/api/v1")
STATIC_ROOT = Path(__file__).parent.parent / "static_auto" / "static"


@app.get("/", include_in_schema=False)
async def to_docs():
    return RedirectResponse("/docs")


@app.get("/app")
async def get_app(request: Request) -> dict:
    return {"routes": str(request.app.routes)}


monkey_patch_for_docs_ui(app, STATIC_ROOT)
