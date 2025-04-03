from pathlib import Path

from fastapi import FastAPI

import fastapi_cdn_host

app = FastAPI(title="FastAPI CDN host test")
fastapi_cdn_host.mount_static(app, "static")
fastapi_cdn_host.mount_static(app, Path("pictures"), uri_path="images")
fastapi_cdn_host.mount_static(app, "assets/js", uri_path="javascripts")
fastapi_cdn_host.mount_static(app, "media", auto_mkdir=True)
fastapi_cdn_host.mount_static(app, "not_exists_dir", auto_mkdir=False)
