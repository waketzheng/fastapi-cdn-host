from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
STATIC_ROOT = Path(__file__).parent.parent / "static_auto" / "static"
app.mount("/cdn", StaticFiles(directory=STATIC_ROOT), name="cdn")
