#!/usr/bin/env python
import os
import subprocess
import sys

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

import fastapi_cdn_host

app = FastAPI(title="HTTP redirect center")
fastapi_cdn_host.patch_docs(app)


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
    return {"data": data, "headers": dict(headers), "path": request.url.path}


def runserver() -> int:  # pragma: no cover
    cmd = f"fastapi dev {sys.argv[0]}"
    port = 8000
    if args := sys.argv[1:]:
        if (a := args[0]).isdigit():
            port = int(a)
            args[0] = f"--{port=}"
        cmd += " " + " ".join(args)
    if (rc := os.system(cmd)) == 0:
        host = "127.0.0.1"
        # Auto open browser
        subprocess.run(f"open http://{host}:{port}".split())
    return rc


if __name__ == "__main__":  # pragma: no cover
    sys.exit(runserver())
