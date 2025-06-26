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
	pdm self update --verbose
	pdm update

lock:
	pdm lock --group :all --strategy inherit_metadata

show:
	pdm list --tree $(options)

deps:
	pdm install --verbose --group :all --frozen

_check:
	./scripts/check.py
check: deps _build _check

_lint:
	pdm run fast lint
lint: deps _build _lint

_test:
	./scripts/test.py
test: deps _test

_style:
	./scripts/format.py
style: deps _style

_build:
	rm -fR dist/
	pdm build --verbose
build: deps _build

venv:
ifeq ($(wildcard .venv),)
	pdm venv create 3.12
	$(MAKE) deps
else
	@echo './.venv' exists, skip virtual environment creating.
	pdm run python -V
endif
