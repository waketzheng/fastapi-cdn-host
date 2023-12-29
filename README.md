# FastAPI CDN host Selector for docs ui
![Python Versions](https://img.shields.io/pypi/pyversions/fastapi-cdn-host)
[![LatestVersionInPypi](https://img.shields.io/pypi/v/fastapi-cdn-host.svg?style=flat)](https://pypi.python.org/pypi/fastapi-cdn-host)
[![GithubActionResult](https://github.com/waketzheng/fastapi-cdn-host/workflows/ci/badge.svg)](https://github.com/waketzheng/fastapi-cdn-host/actions?query=workflow:ci)
[![Coverage Status](https://coveralls.io/repos/github/waketzheng/fastapi-cdn-host/badge.svg?branch=main)](https://coveralls.io/github/waketzheng/fastapi-cdn-host?branch=main)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

Auto find swagger-ui in local files, if exist use them.
Otherwise make concurrent http requests by httpx to find out which third part cdn host is the fastest one.

**English** | [中文](./README.zh-hans.md)

## Install

```bash
pip install fastapi-cdn-host
```

## Usage
1. Let's say that the default docs CDN host https://cdn.jsdelivr.net is too slow in your network, while unpkg.com is much faster.
```py
from fastapi import FastAPI
from fastapi_cdn_host import monkey_patch_for_docs_ui

app = FastAPI()
# include_routes ...

monkey_patch_for_docs_ui(app)  # Will use `unpkg.com` to replace the `cdn.jsdelivr.net/npm`
```
2. In case of there are swagger-ui asset files in local directory named `static`
```py
# Will auto mount static, then use `/static/swagger-ui-bundle.js` and `/static/swagger-ui.css` as docs assets
monkey_patch_for_docs_ui(app)
```
This line is almost equal to the following code:
https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/?h=static#self-hosting-javascript-and-css-for-docs
```py
from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

app = FastAPI(docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )
```
3. If asset files are ready in private cdn
```py
# Will render /docs with the following asset urls:
#   http://my-cdn.com/swagger-ui@latest/swagger-ui-bundle.js
#   http://my-cdn.com/swagger-ui@latest/swagger-ui.css
# render /redoc with: `http://my-cdn.com/redoc/next/redoc.standalone.js`
monkey_patch_for_docs_ui(app, docs_cdn_host=('http://my-cdn.com', ('/swagger-ui@latest/', '/redoc/next/')))
```

## License

[MIT](./LICENSE)
