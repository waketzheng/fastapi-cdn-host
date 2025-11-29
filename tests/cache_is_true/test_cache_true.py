# mypy: no-disallow-untyped-decorators
import importlib
import os
import re
import shutil
import sys
from pathlib import Path

import main
import pytest
from httpx import AsyncClient
from main import app

from fastapi_cdn_host.client import AssetUrl, CdnHostBuilder, CdnHostEnum, HttpSniff
from fastapi_cdn_host.utils import TestClient

default_favicon_url = "https://fastapi.tiangolo.com/img/favicon.png"


@pytest.fixture(scope="module")
async def client():
    async with TestClient(app) as c:
        yield c


async def _run_test(cache_file, urls, client, cache_already_exists=False):
    response = await client.get("/app")
    assert response.status_code == 200
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert default_favicon_url in text
    response2 = await client.get("/redoc")
    text2 = response2.text
    assert response2.status_code == 200, text2
    assert cache_file.exists()
    file_lines = cache_file.read_text("utf8").strip().splitlines()
    if cache_already_exists:
        if "jsdelivr.net" in file_lines[0]:
            css, js, redoc = (_slim_url(i) for i in file_lines)
        else:
            css, js, redoc = file_lines
        assert file_lines[1] in text
        assert file_lines[2] in text2
    else:
        await _run_test_2(cache_file, urls, client, file_lines, text, text2)


def _slim_url(s: str) -> str:  # TODO: remove this
    # Fix fastly.jsdelivr.net != cdn.jsdelivr.net
    return s.split("://", 1)[-1].split(".", 1)[-1]


async def _run_test_2(cache_file, urls, client, file_lines, text, text2):
    if urls.js not in text:
        # Sometimes there are several cdn hosts that have good response speed.
        url_list = await HttpSniff.get_fast_hosts(
            CdnHostBuilder.build_race_data(list(CdnHostEnum))[0]
        )
        assert urls.css in url_list
        assert any(i in text for i in url_list), text
        for url in url_list:
            host = url.split("://")[-1].split("/")[0]
            pattern = rf'src="(.*{host}[:\w/.-]+redoc.*)"'
            if m := re.search(pattern, text2):
                redoc_url = m.group(1)
                print(f"{m.group() = }; {redoc_url=}")
                if urls.redoc != redoc_url:
                    urls.redoc = redoc_url
                # TODO:
                # urls.css = url
                # urls.js = get_js_url_from_css(url)
                break
        else:
            src_urls = re.findall(r'src="[^"]*redoc[^"]*"', text2)
            print(f"{src_urls = }")
            print(f"{url_list = }")
    else:
        assert urls.js in text
        assert urls.css in text
        assert urls.redoc in text2
    if file_lines[1] == urls.js:  # TODO: remove this compare
        if "jsdelivr.net" in file_lines[0]:
            file_lines = [_slim_url(i) for i in file_lines]
        assert file_lines == [urls.css, urls.js, urls.redoc]


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    cache_file = Path.home() / ".cache" / "fastapi-cdn-host" / "urls.txt"
    if cache_already_exists := cache_file.exists():
        lines = cache_file.read_text("utf8").splitlines()
        urls = AssetUrl(css=lines[0], js=lines[1], redoc=lines[2])
    else:
        urls = await CdnHostBuilder.sniff_the_fastest()
    await _run_test(cache_file, urls, client, cache_already_exists)

    if cache_already_exists:
        shutil.rmtree(cache_file.parent)
        urls = await CdnHostBuilder.sniff_the_fastest()
    else:
        lines = cache_file.read_text("utf8").splitlines()
        urls = AssetUrl(css=lines[0], js=lines[1], redoc=lines[2])
    importlib.reload(main)
    await _run_test(cache_file, urls, client, not cache_already_exists)


def test_cache_file(mocker, tmp_path):
    file = tmp_path / "foo" / "a.txt"
    file.parent.mkdir()
    file.touch()
    assert os.path.exists(str(file))
    file.parent.chmod(0)
    with pytest.raises(PermissionError):
        file.read_text()
    mocker.patch("os.path.expanduser", return_value=str(file))
    _, cache_file = CdnHostBuilder().get_cache_file()
    file.parent.chmod(0o700)
    if sys.platform == "win32":
        temp_directory_env_name = "temp"
        temp_dir = Path(os.getenv(temp_directory_env_name, "."))
        assert cache_file == temp_dir / ".cache/fastapi-cdn-host/urls.txt"
    else:
        assert cache_file.as_posix() == "/tmp/.cache/fastapi-cdn-host/urls.txt"
