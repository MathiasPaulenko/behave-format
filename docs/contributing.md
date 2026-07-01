# Contributing

Contributions are welcome!

## Development Setup

```bash
git clone https://github.com/MathiasPaulenko/behave-format.git
cd behave-format
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
```

## Linting

```bash
ruff check behave_format/ tests/
ruff format --check behave_format/ tests/
```

## Before Submitting a PR

1. Fork the repository
2. Create a feature branch
3. Run `ruff check .` and `pytest tests/`
4. Open a Pull Request

## Adding Formatting Rules

1. Add the normalization logic to `pipeline/normalize.py`
2. Add sorting logic to `pipeline/sort.py` if needed
3. Update the appropriate printer in `printer/`
4. Add golden file tests in `tests/`
5. Add idempotency tests
6. Verify `format(format(x)) == format(x)`
