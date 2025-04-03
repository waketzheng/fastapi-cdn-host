# mypy: no-disallow-untyped-decorators
from pathlib import Path

import pytest
from httpx import AsyncClient
from main import app

from fastapi_cdn_host import mount_static
from fastapi_cdn_host.utils import TestClient, TestClientType


@pytest.fixture(scope="module")
async def client() -> TestClientType:
    async with TestClient(app) as c:
        yield c


@pytest.mark.anyio
async def test_static(client: AsyncClient):  # nosec
    response = await client.get("/static")
    assert response.status_code == 307, response.text
    response = await client.get("/static/")
    assert response.status_code == 404, response.text
    assert Path("static").exists()
    Path("static/a.txt").write_text("hello")
    response = await client.get("/static/a.txt")
    assert response.status_code == 200, response.text
    assert response.text == "hello"


@pytest.mark.anyio
async def test_images(client: AsyncClient):  # nosec
    response = await client.get("/images")
    assert response.status_code == 307, response.text
    response = await client.get("/images/")
    assert response.status_code == 404, response.text
    assert not Path("images").exists()
    assert Path("pictures").exists()
    Path("pictures/avatar.jpg").write_bytes(b"")
    response = await client.get("/images/avatar.jpg")
    assert response.status_code == 200, response.text


@pytest.mark.anyio
async def test_mount_subdir(client: AsyncClient):  # nosec
    response = await client.get("/javascripts")
    assert response.status_code == 307, response.text
    response = await client.get("/javascripts/")
    assert response.status_code == 404, response.text
    assert Path("assets/js").exists()
    Path("assets/js/vue.js").write_text("var a=1;")
    response = await client.get("/javascripts/vue.js")
    assert response.status_code == 200, response.text
    assert response.text == "var a=1;"


@pytest.mark.anyio
async def test_media(client: AsyncClient):  # nosec
    response = await client.get("/media")
    assert response.status_code == 307, response.text
    response = await client.get("/media/")
    assert response.status_code == 404, response.text
    assert Path("media").exists()
    Path("media/b.txt").write_text("world")
    response = await client.get("/media/b.txt")
    assert response.status_code == 200, response.text
    assert response.text == "world"


@pytest.mark.anyio
async def test_mkdir_false(client: AsyncClient):  # nosec
    response = await client.get("/not_exists_dir")
    assert response.status_code == 307, response.text
    assert not Path("not_exists_dir").exists()
    with pytest.raises(RuntimeError):
        await client.get("/not_exists_dir/")
    with pytest.raises(RuntimeError):
        await client.get("/not_exists_dir/a.txt")


@pytest.mark.anyio
async def test_mkdir_false_but_check_dir(client: AsyncClient):  # nosec
    with pytest.raises(RuntimeError):
        mount_static(app, "not_exists", auto_mkdir=False, check_dir=True)
