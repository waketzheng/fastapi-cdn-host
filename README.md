# FastAPI CDN host Selector for docs ui
![Python Versions](https://img.shields.io/pypi/pyversions/fastapi-cdn-host)
[![LatestVersionInPypi](https://img.shields.io/pypi/v/fastapi-cdn-host.svg?style=flat)](https://pypi.python.org/pypi/fastapi-cdn-host)
[![GithubActionResult](https://github.com/waketzheng/fastapi-cdn-host/workflows/ci/badge.svg)](https://github.com/waketzheng/fastapi-cdn-host/actions?query=workflow:ci)
[![Coverage Status](https://coveralls.io/repos/github/waketzheng/fastapi-cdn-host/badge.svg?branch=main)](https://coveralls.io/github/waketzheng/fastapi-cdn-host?branch=main)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

Auto find swagger-ui in local files, if exist use them.
Otherwise make concurrent http requests by httpx to find out which third part cdn host(cdn.jsdelivr.net/unpkg.com/cdnjs.cloudflare.com/cdn.staticfile.org) is the fastest one.


**English** | [中文](./README.zh.md)

## Install

```bash
pip install fastapi-cdn-host
```

## Usage
```py
import fastapi_cdn_host
from fastapi import FastAPI

app = FastAPI()
# include_routes ...

fastapi_cdn_host.patch_docs(app)
```
See more at:
- [examples/](https://github.com/waketzheng/fastapi-cdn-host/tree/main/examples)
- [tests/](https://github.com/waketzheng/fastapi-cdn-host/tree/main/tests)

## Detail
1. Let's say that the default docs CDN host https://cdn.jsdelivr.net is too slow in your network, while unpkg.com is much faster.
```py
import fastapi_cdn_host
from fastapi import FastAPI

app = FastAPI()
fastapi_cdn_host.patch_docs(app)  # Will use `unpkg.com`(or other faster host) to replace the `cdn.jsdelivr.net/npm`
```
2. To support offline docs/, put swagger-ui asset files into local directory named `static`
```py
from pathlib import Path

fastapi_cdn_host.patch_docs(app, Path(__file__).parent.joinpath('static'))
```
This get the same result of the example in official document:
https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/?h=static#self-hosting-javascript-and-css-for-docs

3. If asset files are ready in private cdn
```py
from fastapi_cdn_host import AssetUrl

fastapi_cdn_host.patch_docs(
    app,
    cdn_host=AssetUrl(
        js='http://my-cdn.com/swagger-ui.js',
        css='http://my-cdn.com/swagger-ui.css',
        redoc='http://my-cdn.com/redoc.standalone.js',
        favicon='http://my-cdn.com/favicon.ico',
    )
)
```

## License

[MIT](./LICENSE)
