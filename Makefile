help:
	@echo  "Fastapi CDN Host development makefile"
	@echo
	@echo  "Usage: make <target>"
	@echo  "Targets:"
	@echo  "    up      Updates dev/test dependencies"
	@echo  "    deps    Ensure dev/test dependencies are installed"
	@echo  "    check   Checks that build is sane"
	@echo  "    test    Runs all tests"
	@echo  "    style   Auto-formats the code"
	@echo  "    lint    Auto-formats the code and check type hints"
	@echo  "    build   Build wheel and tar file to dist/"

up:
	uv lock --upgrade --verbose

deps:
	uv sync --all-extras --all-groups --frozen

_check:
	./scripts/check.py
check: deps _build _check

_lint:
	uv run fast lint
lint: deps _build _lint

_test:
	./scripts/test.py
test: deps _test

_style:
	./scripts/format.py
style: deps _style

_build:
	rm -fR dist/
	uv build --no-python-downloads --verbose
build: deps _build

venv:
ifeq ($(wildcard .venv),)
	uv venv --python=python3.12 --prompt=fastapi-cdn-host-py3.12
	$(MAKE) deps
else
	@echo './.venv' exists, skip virtual environment creating.
	uv run python -V
endif
