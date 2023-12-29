#!/usr/bin/env python
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from fastapi_cdn_host import CdnHostEnum, monkey_patch_for_docs_ui

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
        (
            "https://cdn.bootcdn.net/ajax/libs",
            ("/swagger-ui/{version}/", ""),
        ),  # BootCDN
        ("https://cdn.staticfile.org", ("/swagger-ui/{version}/", "")),  # 七牛云
        (
            "https://lf9-cdn-tos.bytecdntp.com/cdn/expire-1-M",
            ("/swagger-ui/{version}/", ""),
        ),  # 字节
    ),
)
