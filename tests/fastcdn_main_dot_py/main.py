from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

app = FastAPI(title="FastAPI CDN Host test")


@app.get("/", include_in_schema=False)
async def to_docs():
    return RedirectResponse("/docs")


@app.get("/app")
async def get_app(request: Request) -> dict:
    return {"routes": str(request.app.routes)}
