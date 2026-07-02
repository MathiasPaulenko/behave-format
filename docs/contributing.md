# Contributing

Contributions are welcome! This guide covers everything you need to get started.

## Development setup

```bash
# Clone the repository
git clone https://github.com/MathiasPaulenko/behave-format.git
cd behave-format

# Install in development mode with all dev dependencies
pip install -e ".[dev]"

# Verify installation
behave-format --version
pytest tests/ -v
```

## Project structure

```text
behave-format/
├── behave_format/          # Source code
│   ├── config/             # Settings
│   ├── pipeline/           # Formatting pipeline
│   ├── printer/            # Text generation
│   └── cli/                # CLI
├── tests/                  # Test suite
│   ├── golden/             # Golden file tests
│   ├── unit/               # Unit tests
│   └── performance/        # Performance tests
├── docs/                   # Documentation
├── pyproject.toml          # Project config
└── mkdocs.yml              # Docs config
```

## Running tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=behave_format --cov-report=term-missing

# Run only unit tests
pytest tests/unit/ -v

# Run only golden file tests
pytest tests/golden/ -v

# Run performance tests
pytest tests/performance/ -v
```

## Linting and formatting

```bash
# Check linting
ruff check behave_format/ tests/

# Check formatting
ruff format --check behave_format/ tests/

# Auto-fix linting issues
ruff check --fix behave_format/ tests/

# Auto-format
ruff format behave_format/ tests/
```

## Type checking

```bash
mypy behave_format/
```

## Building documentation

```bash
# Serve docs locally with live reload
mkdocs serve

# Build docs
mkdocs build --strict
```

## Before submitting a PR

1. **Fork** the repository and create a feature branch
2. **Run all checks:**

    ```bash
    ruff check behave_format/ tests/
    ruff format --check behave_format/ tests/
    mypy behave_format/
    pytest tests/ -v
    ```

3. **Add tests** for any new functionality
4. **Update documentation** if needed
5. **Ensure idempotency** — `format(format(x)) == format(x)` must always hold
6. **Open a Pull Request** with a clear description

## Adding formatting rules

1. **Add normalization logic** to `pipeline/normalize.py`
2. **Add sorting logic** to `pipeline/sort.py` if needed
3. **Update the appropriate printer** in `printer/`
4. **Add golden file tests** in `tests/golden/`
5. **Add idempotency tests** — verify `format(format(x)) == format(x)`
6. **Update docs** in `guides/formatting_rules.md`

### Golden file test pattern

```python
def test_my_rule():
    input_text = """@smoke @auth
Feature: Test
"""
    expected = """@auth @smoke
Feature: Test
"""
    feature = load_feature_from_text(input_text)
    format_feature(feature, Settings())
    result = print_feature(feature, indent=2)
    assert result == expected.strip()
```

## Release process

Releases are automated via GitHub Actions:

1. Update `__version__` in `behave_format/__init__.py`
2. Update `CHANGELOG.md`
3. Commit and push to `main`
4. Create and push a tag: `git tag v1.0.2 && git push origin v1.0.2`
5. The release workflow builds, tests, and publishes to PyPI automatically

## Code style

- Follow PEP 8 (enforced by Ruff)
- Use type hints on all public functions
- Write docstrings in Google or NumPy format
- Keep functions small and focused
- Prefer composition over inheritance
- Use `pathlib.Path` for file operations

## Reporting bugs

When reporting a bug, please include:

1. The `.feature` file that triggers the bug (or a minimal reproduction)
2. The expected output
3. The actual output
4. The behave-format version (`behave-format --version`)
5. The Python version (`python --version`)
