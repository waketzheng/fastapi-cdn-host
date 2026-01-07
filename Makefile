version=3.12

help:
	@echo  "Fastapi CDN Host development makefile"
	@echo
	@echo  "Usage: make <target>"
	@echo  "Targets:"
	@echo  "    up      Updates dev/test dependencies"
	@echo  "    lock    Refresh lock file"
	@echo  "    show    Show dependencies in tree graph"
	@echo  "    deps    Ensure dev/test dependencies are installed"
	@echo  "    check   Checks that build is sane"
	@echo  "    test    Runs all tests"
	@echo  "    style   Auto-formats the code"
	@echo  "    lint    Auto-formats the code and check type hints"
	@echo  "    build   Build wheel and tar file to dist/"

up:
	uv lock --upgrade
	$(MAKE) deps options=--frozen
	pre-commit autoupdate
	pdm update -G :all --no-sync

lock:
	uv lock --verbose
	$(MAKE) deps options=--frozen
	pdm lock -G :all

show:
	pdm list --tree $(options)

deps:
	uv sync --all-extras --all-groups $(options)
	pdm run fast pypi --quiet

_check:
	./scripts/check.py
check: deps _build _check

_lint:
	./scripts/format.py
	pdm run ty check $(options)
lint: deps _build _lint

_test:
	./scripts/test.py
test: deps _test

_style:
	./scripts/format.py
style: deps _style

_build:
	uv build --clear --verbose
build: deps _build

publish: build
	# uv publish
	@echo Move to github action, just need to mark a tag!

venv:
ifeq ($(wildcard .venv),)
	pdm venv create $(version)
	$(MAKE) deps
else
	@echo './.venv' exists, skip virtual environment creating.
	pdm run python -V
endif

venv313:
	$(MAKE) venv version=3.13

_verify: up lock
	$(MAKE) venv options=--force
	$(MAKE) venv version=3.10 options=--force
	$(MAKE) venv313 options=--force
	$(MAKE) show
	$(MAKE) deps
	$(MAKE) check
	$(MAKE) _check
	$(MAKE) lint
	$(MAKE) _lint
	$(MAKE) test
	$(MAKE) _test
	$(MAKE) style
	$(MAKE) _style
	$(MAKE) build
	$(MAKE) _build
