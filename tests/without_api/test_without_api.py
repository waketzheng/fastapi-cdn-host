# mypy: no-disallow-untyped-decorators
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import cast

import pytest

from fastapi_cdn_host.cli import (
    TEMPLATE,
    PercentBar,
    Progress,
    TaskID,
    load_bool,
    patch_app,
    percentbar,
    run_shell,
    write_app,
)


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
    from_path = Path("main.py")
    dest = Path("app_20251127110500.py")
    mock_echo = mocker.patch("typer.echo")
    write_app(dest, from_path)
    content = dest.read_bytes()
    assert content.decode() == TEMPLATE.format(from_path.stem).strip()
    size = len(content)
    mock_echo.assert_called_once_with(f"Create {dest} with {size=}")
    write_app(dest, "main_2.py")
    assert "main_2" in dest.read_text()


def test_patch_app(mocker, tmp_workdir):
    mock_echo = mocker.patch("typer.echo")
    fmt = "%Y%m%d%H%M%S"
    path = "main.py"
    start = datetime.now()
    with patch_app(path, remove=False) as app_file:
        assert app_file.suffix == ".py"
        stem = app_file.stem
        assert stem.startswith("app_")
        time_str = stem.replace("app_", "")
        dt = datetime.strptime(time_str, fmt)
        assert start.strftime(fmt) <= time_str
        assert dt < datetime.now()
    assert app_file.exists()
    time.sleep(1)
    with patch_app(path) as app_file_2:
        assert app_file_2.stem >= app_file.stem
        assert app_file_2.read_bytes() == app_file.read_bytes()
    mock_echo.assert_called_with(f"Auto remove temp file: {app_file_2}")
    assert not app_file_2.exists()
    app_file.unlink()


class TestPercentBar:
    def test_init(self):
        # msg with empty color
        bar = PercentBar("foo", seconds=10, color="")
        assert bar.seconds == 10
        assert bar.prompt == "foo:"

        # msg with color
        bar2 = PercentBar("well", seconds=0, color="cyan")
        assert bar2.seconds == 5
        assert bar2.prompt == "[cyan]well:"

        bar3 = PercentBar("Hello")
        assert bar3.seconds == 5
        assert bar3.prompt == "Hello:"

        assert PercentBar("", None).seconds == bar3.seconds

    def test_build_prompt(self):
        assert PercentBar.build_prompt("good", "", suffix="...") == "good..."
        assert PercentBar.build_prompt("bad", "red", suffix="!") == "[red]bad!"

    @pytest.mark.anyio
    async def test_percent_play(self, mocker):
        class Foo:
            @staticmethod
            def do() -> None:
                pass

        mock_sleep = mocker.patch("anyio.sleep")
        mock_forwark = mocker.patch.object(Foo, "do")
        cost, percent = 0.2, 5
        await PercentBar.percent_play(cost, percent, forward=mock_forwark)
        assert mock_sleep.call_count == percent
        mock_sleep.assert_called_with(cost / percent)
        assert mock_forwark.call_count == percent

    @pytest.mark.anyio
    async def test_play(self, mocker):
        progress = Progress()
        task = cast(TaskID, 111)
        bar = PercentBar("", 1)

        mock_sleep = mocker.patch("anyio.sleep")
        mock_advance = mocker.patch.object(progress, "advance")
        await bar.play(progress, task)
        assert mock_sleep.call_count == 100
        mock_sleep.assert_called_with(1 / 2 / 20)
        assert mock_advance.call_count == 100
        mock_advance.assert_called_with(task)

        await bar.play(progress, task, 20)
        mock_sleep.assert_called_with(1 / 2 / 80)

    @pytest.mark.anyio
    async def test_async_with(self, mocker):
        progress = Progress()
        task = cast(TaskID, 111)

        mock_start = mocker.patch.object(progress, "start")
        mock_update = mocker.patch.object(progress, "update")
        mock_exit = mocker.patch.object(progress, "__exit__")
        mock_task = mocker.patch.object(progress, "add_task", return_value=task)

        bar = PercentBar("", 1)
        bar.progress = progress
        mock_play = mocker.patch.object(bar, "play")
        async with bar as bar2:
            assert bar2 is bar
            assert bar.seconds == 1
            mock_start.assert_called_once()
            mock_task.assert_called_once_with(bar.prompt, total=100)
            mock_play.assert_called_once_with(bar.progress, task)
        mock_update.assert_called_once_with(task, completed=100)
        mock_exit.assert_called_once()

    @pytest.mark.anyio
    async def test_percentbar(self, mocker):
        class Bar:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args, **kw) -> None:
                pass

        bar = Bar()
        mock_percentbar = mocker.patch(
            "fastapi_cdn_host.cli.PercentBar", return_value=bar
        )
        # mock_aenter = mocker.patch.object(bar, "__aenter__")
        # mock_aexit = mocker.patch.object(bar, "__aexit__")
        async with percentbar("", seconds=1):
            mock_percentbar.assert_called_once_with("", seconds=1)
            # mock_aenter.assert_called_once()
        # mock_aexit.assert_called_once()
