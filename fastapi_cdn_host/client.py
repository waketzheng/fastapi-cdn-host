import inspect
import logging
import math
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from ssl import SSLError
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    cast,
    overload,
)

import anyio
import httpx
from anyio import from_thread
from fastapi import FastAPI, Request
from fastapi.datastructures import URL
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute, Mount
from fastapi.staticfiles import StaticFiles
from typing_extensions import Annotated  # type: ignore[attr-defined]

logger = logging.getLogger("fastapi-cdn-host")

OFFICIAL_REDOC = "https://cdn.redoc.ly/redoc/latest/bundles/"
DEFAULT_ASSET_PATH = ("/swagger-ui-dist@{version}/", "/redoc@next/bundles/")
NORMAL_ASSET_PATH = ("/swagger-ui/{version}/", OFFICIAL_REDOC)
CdnPathInfoType = Tuple[
    Annotated[str, "swagger-ui module path info(must startswith '/')"],
    Annotated[str, "redoc path or url info(must startswith '/')"],
]
CdnDomainType = Annotated[str, "Host for swagger-ui/redoc"]
StrictCdnHostInfoType = Tuple[CdnDomainType, CdnPathInfoType]
CdnHostInfoType = Union[
    Annotated[CdnDomainType, f"Will use DEFAULT_ASSET_PATH: {DEFAULT_ASSET_PATH}"],
    Tuple[CdnDomainType, Annotated[str, "In case of swagger/redoc has the same path"]],
    StrictCdnHostInfoType,
]


class CdnHostItem:
    """For cdn host url parse

    Usage::
        >>> url = 'https://raw.githubusercontent.com/swagger-api/swagger-ui/v5.17.14/dist/swagger-ui.css'
        >>> CdnHostItem(url).export()
        ('https://raw.githubusercontent.com/swagger-api/swagger-ui', ("/v{version}/dist/", ""))
    """

    def __init__(self, swagger_ui: str, redoc: Union[str, None] = "") -> None:
        self.swagger_ui = swagger_ui
        self.redoc = redoc

    @staticmethod
    def remove_filename(url: str) -> str:
        """Remove last part of url if '.' in it

        Usage::
            >>> CdnHostItem.remove_filename('http://localhost:8000/a/b/c.js')
            'http://localhost:8000/a/b/'
            >>> CdnHostItem.remove_filename('http://localhost:8000/a/b')
            'http://localhost:8000/a/b/'
        """
        sep = "://"
        ps = url.split(sep)
        path = ps[-1]
        if not path.endswith("/"):
            parts = path.split("/")
            if "." in parts[-1]:
                parts[-1] = ""
            else:
                parts.append("")
            ps[-1] = "/".join(parts)
        return sep.join(ps)

    def export(self) -> StrictCdnHostInfoType:
        url = URL(self.remove_filename(self.swagger_ui))
        if not (scheme := url.scheme) or not (hostname := url.hostname):
            raise ValueError(f"Invalid ({url!r}) -- missing scheme or hostname")
        parts = url.path.split("/")
        for index, value in enumerate(parts):
            if re.match(r"swagger-ui\b", value):
                shared_path = "/".join(parts[:index])
                swagger_path = "/".join([""] + parts[index:])
                break
        else:
            shared_path = "/".join(parts[:-1])
            swagger_path = "/" + parts[-1]
        host = cast(str, scheme) + "://" + cast(str, hostname) + shared_path
        swagger_path = re.sub(r"\d+\.\d+\.\d+", "{version}", swagger_path)
        if self.redoc is None:
            redoc_path = DEFAULT_ASSET_PATH[-1]
        else:
            if (redoc_path := self.redoc) and not redoc_path.endswith("/"):
                redoc_path = self.remove_filename(redoc_path)
        return host, (swagger_path, redoc_path)


class CdnHostEnum(Enum):
    jsdelivr: CdnHostInfoType = "https://cdn.jsdelivr.net/npm"
    unpkg: CdnHostInfoType = "https://unpkg.com"
    cdnjs: CdnHostInfoType = "https://cdnjs.cloudflare.com/ajax/libs", NORMAL_ASSET_PATH
    bootcdn: CdnHostInfoType = "https://cdn.bootcdn.net/ajax/libs", NORMAL_ASSET_PATH
    qiniu: CdnHostInfoType = "https://cdn.staticfile.org", NORMAL_ASSET_PATH

    @classmethod
    def extend(
        cls, *host: Union[StrictCdnHostInfoType, CdnHostItem]
    ) -> List[CdnHostInfoType]:
        host_infos: List[StrictCdnHostInfoType] = []
        for i in host:
            if isinstance(i, CdnHostItem):
                j = i.export()
                host_infos.append(j)
            else:
                host_infos.append(i)
        return [*host_infos, *cls]


@dataclass
class AssetUrl:
    css: Annotated[str, "URL of swagger-ui.css"]
    js: Annotated[str, "URL of swagger-ui-bundle.js"]
    redoc: Annotated[str, "URL of redoc.standalone.js"]
    favicon: Annotated[Optional[str], "URL of favicon.png/favicon.ico"] = None


class HttpSniff:
    cached: Dict[str, bytes] = {}

    @classmethod
    async def fetch(
        cls,
        client: httpx.AsyncClient,
        url: str,
        results: list,
        index: int,
        try_cache=False,
    ) -> None:
        if try_cache and (content := cls.cached.get(url)):
            results[index] = content
            return
        try:
            r = await client.get(url)
        except (
            httpx.ConnectError,
            httpx.ReadError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            SSLError,
        ):
            ...
        else:
            if r.status_code < 300:
                results[index] = cls.cached[url] = r.content

    @classmethod
    async def find_fastest_host(
        cls, urls: List[str], total_seconds=5, loop_interval=0.1
    ) -> str:
        if us := await cls.bulk_fetch(
            urls, loop_interval, total_seconds, return_first_completed=True
        ):
            return us[0]
        return urls[0]

    @classmethod
    @overload
    async def bulk_fetch(
        cls,
        urls: List[str],
        wait_seconds: float = 0.8,
        total_seconds: float = 3,
        return_first_completed: bool = False,
        get_content: Literal[False] = False,
    ) -> List[str]: ...

    @classmethod
    @overload
    async def bulk_fetch(
        cls,
        urls: List[str],
        wait_seconds: float = 0.8,
        total_seconds: float = 3,
        return_first_completed: bool = False,
        get_content: Literal[True] = True,
    ) -> List[bytes]: ...

    @classmethod
    async def bulk_fetch(
        cls,
        urls: List[str],
        wait_seconds: float = 0.8,
        total_seconds: float = 3,
        return_first_completed: bool = False,
        get_content: bool = False,
    ) -> Union[List[str], List[bytes]]:
        total = len(urls)
        results = [None] * total
        async with httpx.AsyncClient(
            timeout=total_seconds, follow_redirects=True
        ) as client:
            async with anyio.create_task_group() as tg:
                for i, url in enumerate(urls):
                    tg.start_soon(cls.fetch, client, url, results, i, get_content)
                if not get_content:
                    threshold = 1 if return_first_completed else total - 1
                    for _ in range(math.ceil(total_seconds / wait_seconds)):
                        await anyio.sleep(wait_seconds)
                        if sum(r is not None for r in results) >= threshold:
                            tg.cancel_scope.cancel()
                            break
        if get_content:
            return [i or b"" for i in results]
        return [url for url, res in zip(urls, results) if res is not None]

    @classmethod
    async def get_fast_hosts(
        cls,
        urls: List[str],
        wait_seconds=0.8,
        total_seconds=3,
        return_first_completed=False,
    ) -> List[str]:
        return await cls.bulk_fetch(
            urls, wait_seconds, total_seconds, return_first_completed
        )


class CdnHostBuilder:
    swagger_ui_version = "5"
    swagger_ui_full_version = "5.17.14"
    swagger_files = {"css": "swagger-ui.css", "js": "swagger-ui-bundle.js"}
    redoc_file = "redoc.standalone.js"

    def __init__(self, app=None, docs_cdn_host=None, favicon_url=None) -> None:
        self.app = app
        self.docs_cdn_host = docs_cdn_host
        self.favicon_url = favicon_url

    @staticmethod
    def run_async(async_func, *args) -> Any:
        """Run async function in worker thread and get the result of it"""
        result = [None]

        async def runner():
            result[0] = await async_func(*args)

        with from_thread.start_blocking_portal() as portal:
            portal.call(runner)

        return result[0]

    def run(self) -> AssetUrl:
        if (favicon := self.favicon_url) is not None:
            favicon = self.mount_local_favicon(favicon)
        static_builder = StaticBuilder(self.app, favicon_url=favicon)
        if isinstance(cdn_host := self.docs_cdn_host, Path):
            static_builder.static_root = self.docs_cdn_host
        elif cdn_host is not None:
            if isinstance(cdn_host, CdnHostEnum):
                cdn_host = cdn_host.value
            if isinstance(cdn_host, str):
                return self.build_asset_url(cdn_host, favicon_url=favicon)
            if isinstance(cdn_host, list) and isinstance(cdn_host[0], tuple):
                return self.run_async(self.sniff_the_fastest, favicon, cdn_host)
            cdn_host, asset_path = cdn_host
            if isinstance(asset_path, str):
                asset_path = (asset_path, asset_path)
            return self.build_asset_url(cdn_host, asset_path, favicon_url=favicon)
        if urls := static_builder.find():
            return urls
        return self.run_async(self.sniff_the_fastest, favicon)

    @staticmethod
    def fill_root_path(urls, root):
        if root:
            for attr in ("js", "css", "redoc", "favicon"):
                if (
                    (v := getattr(urls, attr))
                    and v.startswith("/")
                    and not v.startswith(root)
                ):
                    setattr(urls, attr, root + v)
        return urls

    @classmethod
    def build_swagger_path(cls, asset_path: Union[str, Tuple[str, str]]) -> str:
        if isinstance(asset_path, str):
            path_fmt = asset_path
        else:
            path_fmt = asset_path[0]
        version = cls.swagger_ui_version  # unpkg/jsdelivr: 'swagger-ui@5/xxx'
        if "@" not in path_fmt:  # cdnjs/bootcdn/...: 'swagger-ui/5.17.14/xxx'
            version = cls.swagger_ui_full_version
        return path_fmt.format(version=version)

    @classmethod
    def build_race_data(
        cls,
        competitors: Iterable[Union[CdnHostInfoType, CdnHostEnum]],
    ) -> Tuple[List[str], List[tuple]]:
        css_urls: List[str] = []
        they: List[tuple] = []
        for cdn_host in competitors:
            if isinstance(cdn_host, CdnHostEnum):
                cdn_host = cdn_host.value
            if isinstance(cdn_host, str):
                host = cdn_host
                asset_path: Union[str, CdnPathInfoType] = DEFAULT_ASSET_PATH
            else:
                host, asset_path = cdn_host
            they.append((host, asset_path))
            path = cls.build_swagger_path(asset_path)
            url = host + path + cls.swagger_files["css"]
            css_urls.append(url)
        return css_urls, they

    @classmethod
    async def sniff_the_fastest(
        cls, favicon_url=None, choices=tuple(CdnHostEnum)
    ) -> AssetUrl:
        css_urls, they = cls.build_race_data(choices)
        fast_css_url = await HttpSniff.find_fastest_host(css_urls)
        fast_host, fast_asset_path = they[css_urls.index(fast_css_url)]
        logger.info(f"Select cdn: {fast_host[0]} to serve swagger css/js")
        return cls.build_asset_url(
            fast_host, fast_asset_path, fast_css_url, favicon_url
        )

    @classmethod
    def build_asset_url(
        cls,
        cdn_host: str,
        asset_path: Tuple[str, str] = DEFAULT_ASSET_PATH,
        css: Optional[str] = None,
        favicon_url: Optional[str] = None,
    ) -> AssetUrl:
        swagger_ui_path = cls.build_swagger_path(asset_path)
        js = cdn_host + swagger_ui_path + cls.swagger_files["js"]
        if css is None:
            css = cdn_host + swagger_ui_path + cls.swagger_files["css"]
        redoc_path = asset_path[1] or OFFICIAL_REDOC
        if not redoc_path.startswith("http"):
            redoc_path = cdn_host + redoc_path
        redoc = redoc_path + cls.redoc_file
        return AssetUrl(css=css, js=js, redoc=redoc, favicon=favicon_url)

    def mount_local_favicon(self, favicon_url) -> Union[str, None]:
        if favicon_url is not None and favicon_url.startswith("/"):
            filename = favicon_url.lstrip("/")
            favicon_file = Path(filename)
            if favicon_file.exists() and favicon_file.parent.is_dir():
                static_root = Path(filename.split("/")[0])
                uri_path = StaticBuilder.auto_mount_static(
                    self.app, static_root, "/" + static_root.name
                )
                favicon_url = StaticBuilder.file_to_uri(
                    favicon_file, static_root, uri_path
                )
        return favicon_url


class DocsBuilder:
    def __init__(self, index: int) -> None:
        self.index = index

    @staticmethod
    async def try_request_lock(req: Request, lock: Optional[Callable] = None) -> None:
        if lock is not None:
            if inspect.iscoroutinefunction(lock):
                await lock(req)
            else:
                lock(req)

    def update_entrypoint(self, func, app: FastAPI, url: str) -> None:
        app.routes[self.index] = APIRoute(url, func, include_in_schema=False)

    def update_docs_entrypoint(
        self, urls: AssetUrl, app: FastAPI, url: str, lock=None
    ) -> None:
        async def swagger_ui_html(req: Request) -> HTMLResponse:
            await self.try_request_lock(req, lock)
            root_path = req.scope.get("root_path", "").rstrip("/")
            asset_urls = CdnHostBuilder.fill_root_path(urls, root_path)
            openapi_url = root_path + getattr(app, "openapi_url", "")
            if oauth2_redirect_url := getattr(
                app, "swagger_ui_oauth2_redirect_url", ""
            ):
                oauth2_redirect_url = root_path + oauth2_redirect_url
            kw: Dict[str, str] = {}
            if urls.favicon:
                kw["swagger_favicon_url"] = urls.favicon
            return get_swagger_ui_html(
                openapi_url=openapi_url,
                title=f"{getattr(app, 'title', '')} - Swagger UI",
                swagger_js_url=asset_urls.js,
                swagger_css_url=asset_urls.css,
                oauth2_redirect_url=oauth2_redirect_url,
                init_oauth=getattr(app, "swagger_ui_init_oauth", None),
                swagger_ui_parameters=getattr(app, "swagger_ui_parameters", None),
                **kw,
            )

        self.update_entrypoint(swagger_ui_html, app, url)

    def update_redoc_entrypoint(
        self, urls: AssetUrl, app: FastAPI, url: str, lock=None
    ) -> None:
        async def redoc_html(req: Request) -> HTMLResponse:
            await self.try_request_lock(req, lock)
            root_path = req.scope.get("root_path", "").rstrip("/")
            asset_urls = CdnHostBuilder.fill_root_path(urls, root_path)
            openapi_url = root_path + getattr(app, "openapi_url", "")
            return get_redoc_html(
                openapi_url=openapi_url,
                redoc_js_url=asset_urls.redoc,
                title=f"{getattr(app, 'title', '')} - ReDoc",
            )

        self.update_entrypoint(redoc_html, app, url)


class StaticBuilder:
    def __init__(
        self,
        app,
        static_root: Union[Path, None] = None,
        favicon_url: Union[str, None] = None,
    ):
        self.app = app
        self.static_root = static_root
        self.favicon_url = favicon_url

    def find(self):
        return self.detect_local_file(self.app, self.static_root, self.favicon_url)

    def _maybe(
        self, static_root: Path, mount=None, app=None, favicon=None
    ) -> Optional[AssetUrl]:
        if gs := list(static_root.rglob("swagger-ui*.css")):
            logger.info(f"Using local files in {static_root} to serve docs assets.")
            return self._generate_asset_urls_from_local_files(
                gs, mount, app, static_root, favicon
            )
        return None

    @staticmethod
    def get_latest_one(gs: List[Path]) -> Path:
        if len(gs) > 1:
            gs = sorted(gs, key=lambda x: x.stat().st_mtime, reverse=True)
        return gs[0]

    @staticmethod
    def file_to_uri(p: Path, static_root: Path, uri_path: str) -> str:
        return uri_path.rstrip("/") + "/" + p.relative_to(static_root).as_posix()

    @staticmethod
    def auto_mount_static(
        app: FastAPI, static_root: Union[Path, str], uri_path=None
    ) -> str:
        if uri_path is None:
            uri_path = "/static"
        if all(getattr(r, "path", "") != uri_path for r in app.routes):
            name = uri_path.strip("/")
            app.mount(
                uri_path,
                StaticFiles(directory=static_root, follow_symlink=True),
                name=name,
            )
            logger.info(f"Auto mount static files to {uri_path} from {static_root}")
        return uri_path

    def _generate_asset_urls_from_local_files(
        self, gs, mount=None, app=None, static_root=None, favicon=None
    ) -> AssetUrl:
        if mount:
            uri_path = mount.path
        else:
            uri_path = self.auto_mount_static(app, static_root)
        css_file = self.get_latest_one(gs)
        if _js := list(static_root.rglob("swagger-ui*.js")):
            js_file = self.get_latest_one(_js)
        else:
            js_file = css_file.with_name(CdnHostBuilder.swagger_files["js"])
        redoc_name = CdnHostBuilder.redoc_file
        if _redoc := list(static_root.rglob(redoc_name)):
            redoc_file = self.get_latest_one(_redoc)
        else:
            redoc_file = css_file.with_name(redoc_name)

        css = self.file_to_uri(css_file, static_root, uri_path)
        js = self.file_to_uri(js_file, static_root, uri_path)
        redoc = self.file_to_uri(redoc_file, static_root, uri_path)
        if favicon is None:
            favicon = favicon_file = None
            if _favicon := (
                list(static_root.rglob("favicon.png"))
                or list(static_root.rglob("favicon.ico"))
            ):
                favicon_file = self.get_latest_one(_favicon)
            if favicon_file is not None:
                favicon = self.file_to_uri(favicon_file, static_root, uri_path)
        return AssetUrl(css=css, js=js, redoc=redoc, favicon=favicon)

    def detect_local_file(
        self,
        app,
        static_root: Union[Path, None] = None,
        favicon_url: Union[str, None] = None,
    ):
        if static_root is not None:
            return self._maybe(static_root, app=app)
        if mounts := [r for r in app.routes if isinstance(r, Mount)]:
            for m in mounts:
                for d in m.app.all_directories:  # type: ignore[attr-defined]
                    if r := self._maybe(d, mount=m, app=app, favicon=favicon_url):
                        return r
        else:
            if (static_root := Path("static")).exists():
                return self._maybe(static_root, app=app, favicon=favicon_url)


def monkey_patch_for_docs_ui(
    app: FastAPI,
    docs_cdn_host: Union[
        CdnHostEnum, List[CdnHostInfoType], CdnHostInfoType, Path, AssetUrl, None
    ] = None,
    favicon_url: Union[str, None] = None,
    lock: Union[Callable[[Request], Any], None] = None,
) -> None:
    """Use local static files or the faster CDN host for docs asset(swagger-ui)

    :param app: the FastAPI object
    :param docs_cdn_host: static root path or CDN host info
    :param favicon_url: docs page logo
    :param lock: function that receive a request argument to verify it
    """
    openapi_url = getattr(app, "openapi_url", "")
    docs_url, redoc_url = getattr(app, "docs_url", ""), getattr(app, "redoc_url", "")
    if not openapi_url or (not docs_url and not redoc_url):
        logger.info("API docs not activated, skip monkey patch.")
        return
    if isinstance(docs_cdn_host, AssetUrl):
        if favicon_url is not None and favicon_url != docs_cdn_host.favicon:
            docs_cdn_host.favicon = favicon_url
        urls = docs_cdn_host
    else:
        urls = CdnHostBuilder(app, docs_cdn_host, favicon_url).run()
    route_index: Dict[str, int] = {
        getattr(route, "path", ""): index for index, route in enumerate(app.routes)
    }
    if docs_url:
        if (index := route_index.get(docs_url)) is not None:
            DocsBuilder(index).update_docs_entrypoint(urls, app, docs_url, lock=lock)
    if redoc_url:
        if (index := route_index.get(redoc_url)) is not None:
            DocsBuilder(index).update_redoc_entrypoint(urls, app, redoc_url, lock=lock)
