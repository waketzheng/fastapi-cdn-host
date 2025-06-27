from pathlib import Path

import uvicorn
from a2wsgi import WSGIMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from flask import Flask, request
from markupsafe import escape

import fastapi_cdn_host

app = FastAPI(title="FastAPI CDN host test")


@app.get("/app")
def read_main():
    return {"message": "Hello World from main app"}


subapi = FastAPI()


@subapi.get("/sub")
def read_sub():
    return {"message": "Hello World from sub API"}


flask_app = Flask(__name__)


@flask_app.route("/")
def flask_main():
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)} from Flask!"


app.mount("/v1", WSGIMiddleware(flask_app))  # type:ignore
app.mount("/subapi", subapi)
if not (_p := Path(__file__).parent.joinpath("static")).exists():
    _p.mkdir()
    _p.joinpath("a.txt").touch()
app.mount("/static", StaticFiles(directory="static"), name="static")

fastapi_cdn_host.patch_docs(app)

if __name__ == "__main__":
    uvicorn.run(app)
