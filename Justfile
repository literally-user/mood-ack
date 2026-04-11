lint:
    ruff format
    ruff check --fix
    mypy . --strict

run:
    prodik api run