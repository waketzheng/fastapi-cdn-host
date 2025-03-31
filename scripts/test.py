#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

TOOL = ("poetry", "pdm", "uv", "")[2]
work_dir = Path(__file__).parent.resolve().parent
if Path.cwd() != work_dir:
    os.chdir(str(work_dir))

PREPARE = "python tests/prepare_media.py"
CMD = "python scripts/parallel_test.py"
COMBINE = "coverage combine examples/*/.coverage tests/*/.coverage"
REPORT = 'coverage report --omit="tests/*" -m'


def get_result_files():
    for folder in ("examples", "tests"):
        for file in work_dir.joinpath(folder).rglob(".coverage"):
            yield file


def remove_outdate_files(start_time: float) -> None:
    for file in get_result_files():
        if file.stat().st_mtime < start_time:
            file.unlink()
            print(f"Removed outdate file: {file}")


def chdir(path: Path) -> None:
    os.chdir(str(path))
    print("--> cd", path)


def run_command(cmd: str, shell=False, tool=TOOL, env=None) -> None:
    prefix = tool + " run "
    if tool and not cmd.startswith(prefix):
        cmd = prefix + cmd
    print("-->", cmd, flush=True)
    if env is not None:
        env = dict(os.environ, **env)
    r = subprocess.run(cmd if shell else shlex.split(cmd), shell=shell, env=None)
    r.returncode and sys.exit(1)


def combine_result_files(shell=COMBINE) -> None:
    to_be_combine = [i.name for i in get_result_files()]
    if to_be_combine:
        if sys.platform == "win32":
            shell = "coverage combine "
            if work_dir.joinpath(".coverage").exists():
                shell += ".coverage "
            shell += " ".join(to_be_combine)
        run_command(shell, True)


started_at = time.time()
run_command(PREPARE)
if "--no-parallel" in sys.argv:
    for folder in work_dir.joinpath("tests").glob("*"):
        if not folder.is_dir():
            continue
        chdir(folder)
        run_command("coverage run -m pytest -s")
else:
    run_command(CMD)
for eg in ("normal", "offline"):
    chdir(work_dir / "examples" / eg)
    run_command("coverage run -m pytest -s")
os.chdir(str(work_dir))
remove_outdate_files(started_at)
combine_result_files()
run_command(REPORT)
