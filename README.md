# FastAPI cdn host for docs ui

Auto find swagger-ui in local files, if exist use them.
Otherwise make concurrent http requests by httpx to find out which third part cdn host is the fastest one.

**English** | [中文](./README.zh-hans.md)

## Install

```bash
pip install fastapi-cdn-host
```

## Usage::
```py
from fastapi import FastAPI
from fastapi_cdn_host import monkey_patch_for_docs_ui

app = FastAPI()
# include_routes ...

monkey_patch_for_docs_ui(app)
```

## License

[MIT](./LICENSE)
