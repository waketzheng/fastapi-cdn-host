#!/usr/bin/env -S just --justfile
set allow-duplicate-recipes

import? '.common-just/justfile'

system-info:
    @bash -c 'target=".common-just"; if [ -d "$target" ] || git submodule | grep -q "$target"; then just _just_up; else just init; fi'
    @echo "This is an {{ arch() }} machine running on {{ os_family() }}"
    just --list

init:
    git submodule add https://github.com/waketzheng/python-backend-justfile .common-just

_just_up *args:
    git submodule update --init --recursive --merge --remote --force {{ args }}
