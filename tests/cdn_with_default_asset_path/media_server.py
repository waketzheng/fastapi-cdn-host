import shutil
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


def prepare_assets() -> None:
    parent = Path(__file__).parent
    asset_dir = parent.parent / "static_with_favicon/static"
    ui_dir = parent / "cdn/swagger-ui-dist@5.9.0"
    if not ui_dir.exists():
        ui_dir.mkdir(parents=True)
        for src in asset_dir.glob("swagger-ui*"):
            shutil.copyfile(src, ui_dir / src.name)
    redoc = ui_dir.parent / "redoc@next/bundles/redoc.standalone.js"
    if not redoc.exists():
        redoc.parent.mkdir(parents=True)
        shutil.copyfile(asset_dir / redoc.name, redoc)


app = FastAPI()
STATIC_ROOT = Path(__file__).parent / "cdn"
if not STATIC_ROOT.exists():
    prepare_assets()
app.mount("/cdn", StaticFiles(directory=STATIC_ROOT), name="cdn")
