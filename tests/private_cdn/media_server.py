from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
STATIC_ROOT = Path(__file__).parent / "cdn"
app.mount("/cdn", StaticFiles(directory=STATIC_ROOT), name=STATIC_ROOT.name)
