#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Run `ruff format` to make style and `ruff check --fix` to remove unused imports

Usage:
    ./scripts/format.py

"""

import os
import sys

TOOL = ("poetry", "pdm", "uv", "")[0]
PREPARE = "{0} run ruff --version || {0} install".format(TOOL)
CMD = "ruff format && ruff check --fix"

parent = os.path.abspath(os.path.dirname(__file__))
work_dir = os.path.dirname(parent)
if os.getcwd() != work_dir:
    os.chdir(work_dir)

# Ensure lint tools installed
for cmd in PREPARE.split("||"):
    if os.system(cmd.strip()) == 0:
        break

# Reformat files
prefix = TOOL and "{} run ".format(TOOL)
for cmd in CMD.split("&&"):
    if os.system(prefix + cmd.strip()) != 0:
        sys.exit(1)
