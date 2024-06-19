from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

import fastapi_cdn_host

app = FastAPI(title="FastAPI CDN host test")
STATIC_ROOT = Path(__file__).parent.parent / "static_auto" / "static"
app.mount(
    "/static", StaticFiles(directory=STATIC_ROOT, follow_symlink=True), name="static"
)
app.mount(
    "/media", StaticFiles(directory=STATIC_ROOT, follow_symlink=True), name="media"
)
fastapi_cdn_host.patch_docs(app)  # Note: Can't put it before static/media mount


@app.get("/", include_in_schema=False)
async def to_docs():
    return RedirectResponse("/docs")


@app.get("/app")
async def get_app(request: Request) -> dict:
    return {"routes": str(request.app.routes)}
