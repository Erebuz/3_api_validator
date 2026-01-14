VENV = .venv
BIN = $(VENV)/Scripts
PYTHON = $(BIN)/python

PROJECT_NAME = 3_api_validator

.PHONY: run lint

run:
	$(PYTHON) ./run.py

lint:
	pre-commit run --all-files --color=never

test:
	uv run pytest --cov=. --cov-report=html
