import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import anyio
import httpx
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute, Mount
from fastapi.staticfiles import StaticFiles
from typing_extensions import Annotated  # type: ignore [attr-defined]

logger = logging.getLogger("fastapi-cdn-host")

DEFAULT_ASSET_PATH = ("/swagger-ui-dist@{version}/", "/redoc@next/bundles/")
CdnPathInfoType = Tuple[
    Annotated[str, "swagger-ui module path info"],
    Annotated[str, "redoc path or url info"],
]
CdnDomainType = Annotated[str, "Host for swagger-ui/redoc"]
CdnHostInfoType = Union[
    Annotated[CdnDomainType, f"Will use DEFAULT_ASSET_PATH: {DEFAULT_ASSET_PATH}"],
    Tuple[CdnDomainType, CdnPathInfoType],
    Tuple[CdnDomainType, Annotated[str, "In case of swagger/redoc has the same path"]],
]


async def fetch(client, url, results, index) -> None:
    try:
        r = await client.get(url)
    except (httpx.ConnectError, httpx.ReadError):
        ...
    else:
        if r.status_code < 300:
            results[index] = r.content


async def find_fastest_host(urls: List[str], total_seconds=5, loop_interval=0.1) -> str:
    results = [None] * len(urls)
    async with anyio.create_task_group() as tg:
        async with httpx.AsyncClient(timeout=total_seconds) as client:
            for i, url in enumerate(urls):
                tg.start_soon(fetch, client, url, results, i)
            for _ in range(int(total_seconds / loop_interval) + 1):
                if any(r is not None for r in results):
                    tg.cancel_scope.cancel()
                    break
                await anyio.sleep(loop_interval)
    for url, res in zip(urls, results):
        if res is not None:
            return url
    return urls[0]


def run_async(async_func, *args) -> Any:
    result = [None]

    async def runner():
        result[0] = await async_func(*args)

    with anyio.from_thread.start_blocking_portal() as portal:
        portal.call(runner)

    return result[0]


class CdnHostEnum(Enum):
    jsdelivr: CdnHostInfoType = "https://cdn.jsdelivr.net/npm"
    unpkg: CdnHostInfoType = "https://unpkg.com"
    cdnjs: CdnHostInfoType = "https://cdnjs.cloudflare.com/ajax/libs", (
        "/swagger-ui/{version}/" "https://cdn.redoc.ly/redoc/latest/bundles/"
    )


@dataclass
class AssetUrl:
    css: Annotated[str, "URL of swagger-ui.css"]
    js: Annotated[str, "URL of swagger-ui-bundle.js"]
    redoc: Annotated[str, "URL of redoc.standalone.js"]
    favicon: Annotated[Optional[str], "URL of favicon.png/favicon.ico"] = None


class CdnHostBuilder:
    swagger_ui_version = "5.9.0"  # to be optimize: auto get version from fastapi
    swagger_files = {"css": "swagger-ui.css", "js": "swagger-ui-bundle.js"}
    redoc_file = "redoc.standalone.js"

    def __init__(self, app=None, docs_cdn_host=None, favicon_url=None) -> None:
        self.app = app
        self.docs_cdn_host = docs_cdn_host
        self.favicon_url = favicon_url

    def run(self) -> AssetUrl:
        if urls := local_file(self.app, favicon_url=self.favicon_url):
            if root := self.app.request.scope.get("root_path"):
                urls.js = root + urls.js
                urls.css = root + urls.css
                urls.redoc = root + urls.redoc
                urls.favicon = urls.favicon and (root + urls.favicon)
            return urls
        return run_async(self.sniff_the_fastest, self.favicon_url)

    @classmethod
    async def sniff_the_fastest(cls, favicon_url=None) -> AssetUrl:
        css_urls: List[str] = []
        they: List[tuple] = []
        for cdn_host in CdnHostEnum:
            host = cdn_host.value
            path = DEFAULT_ASSET_PATH[0]
            if isinstance(host, tuple):
                they.append((host, path))
                path = host[1][0]
                host = host[0]
            else:
                they.append((host, DEFAULT_ASSET_PATH))
            path = path.format(version=cls.swagger_ui_version)
            url = host + path + cls.swagger_files["css"]
            css_urls.append(url)
        fast_one = await find_fastest_host(css_urls)
        index = css_urls.index(fast_one)  # to be optimized
        fast_host = they[index]
        css = fast_one
        swagger_ui_path = fast_host[1][0].format(version=cls.swagger_ui_version)
        js = fast_host[0] + swagger_ui_path + cls.swagger_files["js"]
        redoc_path = fast_host[1][1]
        if not redoc_path.startswith("http"):
            redoc_path = fast_host[0] + redoc_path
        redoc = redoc_path + cls.redoc_file
        logger.info(f"Select cdn: {fast_host[0]} to serve swagger css/js")
        return AssetUrl(css=css, js=js, redoc=redoc, favicon=favicon_url)


def new_docs_url(index: int, urls: AssetUrl, self: FastAPI, docs_url: str) -> None:
    swagger_js_url = urls.js
    swagger_css_url = urls.css

    async def swagger_ui_html(req: Request) -> HTMLResponse:
        root_path = req.scope.get("root_path", "").rstrip("/")
        openapi_url = root_path + self.openapi_url
        oauth2_redirect_url = self.swagger_ui_oauth2_redirect_url
        if oauth2_redirect_url:
            oauth2_redirect_url = root_path + oauth2_redirect_url
        kw: Dict[str, str] = {}
        if urls.favicon:
            kw["swagger_favicon_url"] = urls.favicon
        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=self.title + " - Swagger UI",
            swagger_js_url=swagger_js_url,
            swagger_css_url=swagger_css_url,
            oauth2_redirect_url=oauth2_redirect_url,
            init_oauth=self.swagger_ui_init_oauth,
            swagger_ui_parameters=self.swagger_ui_parameters,
            **kw,
        )

    self.routes[index] = APIRoute(docs_url, swagger_ui_html, include_in_schema=False)


def new_redoc_url(index: int, urls: AssetUrl, self: FastAPI, redoc_url: str) -> None:
    async def redoc_html(req: Request) -> HTMLResponse:
        root_path = req.scope.get("root_path", "").rstrip("/")
        openapi_url = root_path + self.openapi_url
        return get_redoc_html(
            openapi_url=openapi_url,
            redoc_js_url=urls.redoc,
            title=self.title + " - ReDoc",
        )

    self.routes[index] = APIRoute(redoc_url, redoc_html, include_in_schema=False)


def _maybe(static_root: Path, mount=None, app=None, favicon=None) -> Optional[AssetUrl]:
    if gs := list(static_root.rglob("swagger-ui*.css")):
        logger.info(f"Using local files in {static_root} to serve docs assets.")
        return _next_it(gs, mount, app, static_root, favicon)
    return None


def get_latest_one(gs: List[Path]) -> Path:
    if len(gs) > 1:
        gs = sorted(gs, key=lambda x: x.stat().st_mtime, reverse=True)
    return gs[0]


def file_to_uri(p: Path, static_root: Path, uri_path: str) -> str:
    return uri_path.rstrip("/") + "/" + p.relative_to(static_root).as_posix()


def _next_it(gs, mount=None, app=None, static_root=None, favicon=None) -> AssetUrl:
    if mount:
        uri_path = mount.path
    else:
        uri_path = "/static"
        if all(r.path != uri_path for r in app.routes):
            app.mount(uri_path, StaticFiles(directory=static_root), name="static")
            logger.info(f"Auto mount static files to {uri_path} from {static_root}")
    css_file = get_latest_one(gs)
    if _js := list(static_root.rglob("swagger-ui*.js")):
        js_file = get_latest_one(_js)
    else:
        js_file = css_file.with_name(CdnHostBuilder.swagger_files["js"])
    redoc_name = CdnHostBuilder.redoc_file
    if _redoc := list(static_root.rglob(redoc_name)):
        redoc_file = get_latest_one(_redoc)
    else:
        redoc_file = css_file.with_name(redoc_name)

    css = file_to_uri(css_file, static_root, uri_path)
    js = file_to_uri(js_file, static_root, uri_path)
    redoc = file_to_uri(redoc_file, static_root, uri_path)
    if favicon is None:
        favicon = favicon_file = None
        if _favicon := (
            list(
                static_root.rglob("favicon.png")
                or list(static_root.rglob("favicon.ico"))
            )
        ):
            favicon_file = get_latest_one(_favicon)
        if favicon_file is not None:
            favicon = file_to_uri(favicon_file, static_root, uri_path)
    return AssetUrl(css=css, js=js, redoc=redoc, favicon=favicon)


def local_file(
    app, static_root: Union[Path, None] = None, favicon_url: Union[str, None] = None
):
    if static_root is not None:
        return _maybe(static_root, app=app)
    if mounts := [r for r in app.routes if isinstance(r, Mount)]:
        for m in mounts:
            for d in m.app.all_directories:  # type: ignore[attr-defined]
                if r := _maybe(d, mount=m, app=app, favicon=favicon_url):
                    return r
    else:
        if (static_root := Path("static")).exists():
            return _maybe(static_root, app=app, favicon=favicon_url)


def monkey_patch_for_docs_ui(
    app: FastAPI,
    docs_cdn_host: Union[CdnHostEnum, CdnHostInfoType, Path, None] = None,
    favicon_url: Union[str, None] = None,
) -> None:
    """Use local static files or the faster CDN host for docs asset(swagger-ui)

    :param app: the FastAPI object
    :param docs_cdn_host: static root path or CDN host info
    :param favicon_url: docs page logo
    """
    openapi_url = getattr(app, "openapi_url", "")
    docs_url, redoc_url = getattr(app, "docs_url", ""), getattr(app, "redoc_url", "")
    if not openapi_url or (not docs_url and not redoc_url):
        logger.info("API docs not activated, skip monkey patch.")
        return
    urls = CdnHostBuilder(app, docs_cdn_host, favicon_url).run()
    if docs_url:
        for i, route in enumerate(app.routes):
            if getattr(route, "path", "") == docs_url:
                new_docs_url(i, urls, app, docs_url)
    if redoc_url:
        for i, route in enumerate(app.routes):
            if getattr(route, "path", "") == redoc_url:
                new_redoc_url(i, urls, app, redoc_url)
