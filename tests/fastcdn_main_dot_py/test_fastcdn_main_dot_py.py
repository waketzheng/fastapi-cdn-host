# mypy: no-disallow-untyped-decorators
import contextlib
import os
import uuid
from datetime import datetime
from pathlib import Path

import anyio
import pytest
from asynctor.timing import Timer
from httpx import AsyncClient, ConnectError

from fastapi_cdn_host.cli import TEMPLATE, load_bool, run_shell, write_app
from fastapi_cdn_host.client import CdnHostBuilder


async def wait_for_app_startup(client: AsyncClient, timeout=5) -> None:
    interval = 0.5
    verbose = load_bool("FASTCDN_VERBOSE")
    timer = Timer("Testing api reachable", decimal_places=3, verbose=verbose)
    start = timer._start

    def past_time() -> float:
        return round(datetime.now().timestamp() - start, timer._decimal_places)

    for loop in range(1, int(timeout // interval)):
        with contextlib.suppress(ConnectError), timer as t:
            r = await client.get("/app", timeout=1)
            if r.status_code == 200:
                if verbose:
                    print(f"API ready within loop {loop}, Cost: {past_time()} seconds")
                return
        if (delta := interval - t.cost) > 0:
            await anyio.sleep(delta)
        if past_time() > timeout:
            break


@pytest.mark.anyio
async def test_docs(client: AsyncClient):  # nosec
    await wait_for_app_startup(client)
    swagger_ui = CdnHostBuilder.swagger_files
    js_url = "/static/" + swagger_ui["js"]
    css_url = "/static/" + swagger_ui["css"]
    response = await client.get(css_url)
    assert response.status_code == 200, f"{response.url=};{response.text=}"
    response = await client.get(js_url)
    assert response.status_code == 200, response.text
    response = await client.get("/docs")
    text = response.text
    assert response.status_code == 200, text
    assert js_url in text
    assert css_url in text
    response = await client.get("/redoc")
    text = response.text
    assert response.status_code == 200, text
    assert "/static/redoc" in text
    response = await client.get("/app")
    assert response.status_code == 200


def test_load_bool(monkeypatch):
    uid = uuid.uuid4().hex
    assert load_bool(f"NOT_EXIST_ENV_{uid}") is False
    name = "FASTCDN_TEST_" + uuid.uuid4().hex
    monkeypatch.setenv(name, "1")
    assert load_bool(name) is True
    monkeypatch.setenv(name, "0")
    assert load_bool(name) is False
    monkeypatch.setenv(name, "true")
    assert load_bool(name) is True
    monkeypatch.setenv(name, "false")
    assert load_bool(name) is False
    monkeypatch.setenv(name, "True")
    assert load_bool(name) is True
    monkeypatch.setenv(name, "False")
    assert load_bool(name) is False
    monkeypatch.setenv(name, "on")
    assert load_bool(name) is True
    monkeypatch.setenv(name, "off")
    assert load_bool(name) is False
    monkeypatch.setenv(name, "yes")
    assert load_bool(name) is True
    monkeypatch.setenv(name, "no")
    assert load_bool(name) is False
    monkeypatch.setenv(name, "y")
    assert load_bool(name) is True
    monkeypatch.setenv(name, "n")
    assert load_bool(name) is False


class TestRunShell:
    def test_run_shell_single(self, mocker):
        mock_echo = mocker.patch("typer.echo")
        mock_run = mocker.patch("subprocess.run")
        run_shell("ls")
        mock_echo.assert_called_once_with("--> ls")
        mock_run.assert_called_once_with(["ls"], env=None)

    def test_run_shell(self, mocker):
        mock_echo = mocker.patch("typer.echo")
        mock_run = mocker.patch("subprocess.run")
        run_shell("ls tests")
        mock_echo.assert_called_once_with("--> ls tests")
        mock_run.assert_called_once_with(["ls", "tests"], env=None)

    def test_env(self, mocker):
        mock_echo = mocker.patch("typer.echo")
        mock_run = mocker.patch("subprocess.run")
        mocker.patch.object(os, "environ", {})
        run_shell("AA=1 ls")
        mock_echo.assert_called_once_with("--> AA=1 ls")
        mock_run.assert_called_once_with(["ls"], env={"AA": "1"})

    def test_env_multi(self, mocker):
        mock_echo = mocker.patch("typer.echo")
        mock_run = mocker.patch("subprocess.run")
        mocker.patch.object(os, "environ", {"CC": "3"})
        run_shell("AA=1 BB=2 ls -a .")
        mock_echo.assert_called_once_with("--> AA=1 BB=2 ls -a .")
        mock_run.assert_called_once_with(
            ["ls", "-a", "."], env={"AA": "1", "BB": "2", "CC": "3"}
        )


def test_write_app(mocker, tmp_workdir):
    dest = Path("main.py")
    src = Path("app_1.py")
    mock_echo = mocker.patch("typer.echo")
    write_app(dest, src)
    content = dest.read_bytes()
    assert content.decode() == TEMPLATE.format(src.stem).strip()
    size = len(content)
    mock_echo.assert_called_once_with(f"Create {dest} with {size=}")
