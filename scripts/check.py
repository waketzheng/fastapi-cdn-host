#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Check style by `ruff` and verify type hints by `mypy`,
then run `bandit -r <package>` to find security issue.


Usage::
    ./scripts/check.py

"""

import os
import sys

TOOL = ("poetry", "pdm", "uv", "")[2]
PREPARE = "{0} run ruff --version || {0} install".format(TOOL)
CMD = "ruff format --check && ruff check && mypy . && bandit -c pyproject.toml -r ."

parent = os.path.abspath(os.path.dirname(__file__))
work_dir = os.path.dirname(parent)
if os.getcwd() != work_dir:
    os.chdir(work_dir)


def run_and_echo(cmd):
    # type: (str) -> int
    print("--> {}".format(cmd))
    return os.system(cmd)


# Ensure lint tools installed
for cmd in PREPARE.split("||"):
    if run_and_echo(cmd.strip()) == 0:
        break

# Run lints
prefix = TOOL and "{} run ".format(TOOL)
for cmd in CMD.split("&&"):
    if run_and_echo(prefix + cmd.strip()) == 0:
        continue
    if "ruff" in cmd:
        print(
            "\033[1m Please run './scripts/format.py' to auto-fix style issues \033[0m"
        )
    sys.exit(1)

print("Done. ✨ 🍰 ✨")
