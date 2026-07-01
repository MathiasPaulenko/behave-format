.PHONY: install dev test test-verbose lint format coverage build clean docs docs-serve

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -q

test-verbose:
	pytest tests/ -v --tb=short

lint:
	ruff check behave_format/ tests/
	ruff format --check behave_format/ tests/

format:
	ruff format behave_format/ tests/
	ruff check --fix behave_format/ tests/

coverage:
	pytest tests/ --cov=behave_format --cov-report=term-missing --cov-report=html

build:
	python -m build

docs:
	mkdocs build

docs-serve:
	mkdocs serve

clean:
	rm -rf build/ dist/ *.egg-info/ .coverage .pytest_cache/ htmlcov/ .tox/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
