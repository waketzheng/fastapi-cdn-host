#!/usr/bin/env python
from pathlib import Path

from config import MY_CDN
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

import fastapi_cdn_host
from fastapi_cdn_host import AssetUrl

app = FastAPI(title="FastAPI CDN host test")
app2 = FastAPI(title="FastAPI CDN host test2")


@app.get("/", include_in_schema=False)
@app2.get("/", include_in_schema=False)
async def to_docs():
    return RedirectResponse("/docs")


@app.get("/app")
@app2.get("/app")
async def get_app(request: Request) -> dict:
    return {"routes": str(request.app.routes)}


fastapi_cdn_host.patch_docs(
    app,
    AssetUrl(
        js=MY_CDN + "/swagger-ui-bundle.js",
        css=MY_CDN + "/swagger-ui.css",
        redoc=MY_CDN + "/redoc.standalone.js",
        favicon=MY_CDN + "/fast-dev-cli.ico",
    ),
)
fastapi_cdn_host.patch_docs(
    app2,
    AssetUrl(
        js=MY_CDN + "/swagger-ui-bundle.js",
        css=MY_CDN + "/swagger-ui.css",
        redoc=MY_CDN + "/redoc.standalone.js",
    ),
    favicon_url=MY_CDN + "/fast-dev-cli.ico",
)


def main():
    import uvicorn

    uvicorn.run(f"{Path(__file__).stem}:app", reload=True)


if __name__ == "__main__":
    main()
