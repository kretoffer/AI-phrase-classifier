source .venv/bin/activate
ruff format .
ruff check --select I --fix