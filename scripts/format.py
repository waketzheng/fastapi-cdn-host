#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Run `ruff format` to make style and `ruff check --fix` to remove unused imports

Usage:
    ./scripts/format.py

"""

import os
import sys

TOOL = ("poetry", "pdm", "uv", "")[2]
PREPARE = "{0} run ruff --version || {0} install".format(TOOL)
CMD = "ruff format && ruff check --fix"

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

# Reformat files
prefix = TOOL and "{} run ".format(TOOL)
for cmd in CMD.split("&&"):
    if run_and_echo(prefix + cmd.strip()) != 0:
        sys.exit(1)
