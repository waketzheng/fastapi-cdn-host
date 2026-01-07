#!/usr/bin/env python
import sys

import fastapi_cdn_host
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

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


def runserver() -> None:  # pragma: no cover
    from fastapi_cli.cli import main

    if args := sys.argv[1:]:
        if (a := args[0]).isdigit():  # python main.py 8080
            port = int(a)
            sys.argv[1] = f"--{port=}"
        elif ":" in a:  # python main.py 0:9000
            host, p = a.split(":", 1)
            port = int(p)
            if host == "0":
                host = "0.0.0.0"
            sys.argv[1] = f"--{port=}"
            sys.argv.insert(1, f"--host={host}")
    sys.argv.insert(0, "fastapi")
    sys.argv.insert(1, "dev")
    main()


if __name__ == "__main__":  # pragma: no cover
    runserver()
