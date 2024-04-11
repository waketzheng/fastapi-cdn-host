#!/usr/bin/env python
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from fastapi_cdn_host import CdnHostEnum, CdnHostItem, monkey_patch_for_docs_ui
from fastapi_cdn_host.client import NORMAL_ASSET_PATH

app = FastAPI(title="FastAPI CDN host test")


@app.get("/", include_in_schema=False)
async def to_docs():
    return RedirectResponse("/docs")


@app.get("/app")
async def get_app(request: Request) -> dict:
    return {"routes": str(request.app.routes)}


monkey_patch_for_docs_ui(
    app,
    docs_cdn_host=CdnHostEnum.extend(
        CdnHostItem(
            "https://raw.githubusercontent.com/swagger-api/swagger-ui/v5.9.0/dist/swagger-ui.css"
        ),
        ("https://lf9-cdn-tos.bytecdntp.com/cdn/expire-1-M", NORMAL_ASSET_PATH),
    ),
)
