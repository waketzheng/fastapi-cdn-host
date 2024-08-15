#!/usr/bin/env python
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

import fastapi_cdn_host
from fastapi_cdn_host.client import NORMAL_ASSET_PATH

app = FastAPI(title="FastAPI CDN host test")
SWAGGER_VERSION = "5.17.14"


@app.get("/", include_in_schema=False)
async def to_docs():
    return RedirectResponse("/docs")


@app.get("/app")
async def get_app(request: Request) -> dict:
    return {"routes": str(request.app.routes)}


fastapi_cdn_host.patch_docs(
    app,
    docs_cdn_host=fastapi_cdn_host.CdnHostEnum.extend(
        fastapi_cdn_host.CdnHostItem(
            f"https://raw.githubusercontent.com/swagger-api/swagger-ui/v{SWAGGER_VERSION}/dist/swagger-ui.css"
        ),
        ("https://cdn.waketzheng.top/ajax/libs", NORMAL_ASSET_PATH),
    ),
)
