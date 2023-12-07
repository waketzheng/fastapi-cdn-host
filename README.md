# FastAPI CDN host Selector for docs ui
![Python Versions](https://img.shields.io/pypi/pyversions/fastapi-cdn-host)
[![LatestVersionInPypi](https://img.shields.io/pypi/v/fastapi-cdn-host.svg?style=flat)](https://pypi.python.org/pypi/fastapi-cdn-host)
[![GithubActionResult](https://github.com/waketzheng/fastapi-cdn-host/workflows/ci/badge.svg)](https://github.com/waketzheng/fastapi-cdn-host/actions?query=workflow:ci)
![Mypy coverage](https://img.shields.io/badge/mypy-100%25-green.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Auto find swagger-ui in local files, if exist use them.
Otherwise make concurrent http requests by httpx to find out which third part cdn host is the fastest one.

**English** | [中文](./README.zh-hans.md)

## Install

```bash
pip install fastapi-cdn-host
```

## Usage
```py
from fastapi import FastAPI
from fastapi_cdn_host import monkey_patch_for_docs_ui

app = FastAPI()
# include_routes ...

monkey_patch_for_docs_ui(app)
```

## License

[MIT](./LICENSE)
