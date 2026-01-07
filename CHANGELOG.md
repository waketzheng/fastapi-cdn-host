# ChangeLog

## 0.10

*(Unreleased)*

### [0.10.0]

#### Changed

- feat: drop support for Python3.9

## 0.9


### [0.9.3](../../releases/tag/v0.9.3) - 2025-12-01

#### Added
- feat: add fastly.jsdelivr.net as new cdn host (#38)

#### Changed
- Official support python3.14 (#35)
- Use uv instead of pdm to install deps (#36)
- refactor: use typer.echo instead of print in cli (#37)

#### Fixed
- Fix mount app error when missing `all_directories` attribution (#30)
- Fix offline example download static files error

### [0.9.1](../../releases/tag/v0.9.1) - 2025-04-16

#### Added
- Support `fastcdn cache`
