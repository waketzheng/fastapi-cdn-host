help:
	@echo  "FastDevCli development makefile"
	@echo
	@echo  "Usage: make <target>"
	@echo  "Targets:"
	@echo  "    up      Updates dev/test dependencies"
	@echo  "    deps    Ensure dev/test dependencies are installed"
	@echo  "    check   Checks that build is sane"
	@echo  "    test    Runs all tests"
	@echo  "    style   Auto-formats the code"
	@echo  "    lint    Auto-formats the code and check type hints"

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
