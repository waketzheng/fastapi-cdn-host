#!/usr/bin/env python
import sys
from pathlib import Path

import uvicorn  # type:ignore
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from fastapi_cdn_host import monkey_patch_for_docs_ui

app = FastAPI(title="HTTP redirect center")


@app.get("/", include_in_schema=False)
async def to_docs():
    return RedirectResponse("/docs")


@app.get("/app")
async def get_app(request: Request) -> dict:
    return {"routes": str(request.app.routes)}


@app.post("/test")
async def only_for_test(request: Request) -> dict:
    data = await request.json()
    headers = request.headers
    return {"data": data, "headers": headers, "path": request.url.path}


monkey_patch_for_docs_ui(app)


def runserver() -> None:
    import os
    import subprocess

    root_app = Path(__file__).stem + ":app"
    auto_reload = "PYCHARM_HOSTED" not in os.environ
    host = "0.0.0.0"
    port = 9000
    if sys.argv[1:]:
        port = int(sys.argv[1])
        host = "127.0.0.1"
        subprocess.run(f"open http://{host}:{port}".split())
    uvicorn.run(root_app, host=host, port=port, reload=auto_reload)


if __name__ == "__main__":
    runserver()
