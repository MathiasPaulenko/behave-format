# behave-format

> The opinionated formatter for Behave `.feature` files.

[Black](https://github.com/psf/black) is for Python. [gofmt](https://go.dev/blog/gofmt) is for Go. **behave-format** is for Gherkin.

---

## Overview

`behave-format` is a deterministic, opinionated formatter for Behave `.feature` files. It consumes the canonical domain model from [behave-model](https://github.com/MathiasPaulenko/behave-model) and produces clean, consistent, beautifully formatted output.

**Key principle:** behave-format does NOT parse Gherkin. It does NOT lint. It does NOT validate. It ONLY transforms a `behave-model.Project` into formatted `.feature` files.

```text
.feature files → behave-model (domain model) → behave-format → formatted .feature files
```

## Features

- **Opinionated** — minimal configuration, sensible defaults
- **Deterministic** — same input always produces same output
- **Idempotent** — `format(format(x)) == format(x)`
- **Fast** — handles thousands of feature files efficiently
- **CI-friendly** — `--check` mode with exit code 1 when formatting is needed
- **Safe** — never changes semantics (names, step text, table values, docstrings)

## Installation

```bash
pip install behave-format
```

## Quick Start

### CLI

```bash
# Format files in place (default)
behave-format features/

# Check mode (CI) — exit 1 if formatting is needed
behave-format --check features/

# Diff mode — show differences without writing
behave-format --diff features/
```

### Python API

```python
from behave_model import load_project
from behave_format import format_project, render_project, Settings

project = load_project("features/")

# Format the project model in place
format_project(project)

# Or render to text
text = render_project(project, Settings())
```

## Formatting Rules

### Tags

Tags are sorted alphabetically by default:

```gherkin
@api @smoke
```

### Features

- One blank line before each Feature
- Clean title formatting

### Scenarios

- One blank line before each Scenario
- Two-space indentation for steps

```gherkin
  Given user exists
  When user logs in
  Then dashboard is shown
```

### Tables

Tables are always aligned:

Before:

```gherkin
|user|password|
|john|123|
```

After:

```gherkin
| user | password |
| john | 123      |
```

### Blank Lines

- No trailing blank lines
- No multiple consecutive empty lines
- Consistent spacing between blocks

### Indentation

- Spaces only (no tabs)
- Default: 2 spaces

## Configuration

Minimal configuration via `pyproject.toml`:

```toml
[tool.behave-format]
indent = 2
sort_tags = true
sort_features = false
sort_scenarios = false
line_length = 120
```

| Option | Default | Description |
|--------|---------|-------------|
| `indent` | `2` | Number of spaces for indentation |
| `sort_tags` | `true` | Sort tags alphabetically |
| `sort_features` | `false` | Sort features by name |
| `sort_scenarios` | `false` | Sort scenarios by name |
| `line_length` | `120` | Maximum line length (reference) |

## Before / After

### Before

```gherkin
@smoke @auth
Feature: Login
  As a user
  I want to log in

  Background:
    Given a database connection

  @happy
  Scenario: Successful login
    Given the user is on the login page
    When the user enters "admin" and "password"
    Then the user should be logged in
```

### After

```gherkin
@auth @smoke
Feature: Login
  As a user
  I want to log in

  Background:
    Given a database connection

  @happy
  Scenario: Successful login
    Given the user is on the login page
    When the user enters "admin" and "password"
    Then the user should be logged in
```

## Architecture

```text
behave_format/
├── config/
│   └── settings.py        # Settings dataclass + pyproject.toml loader
├── pipeline/
│   ├── normalize.py       # Whitespace, indentation, tag normalization
│   ├── sort.py            # Sort tags, features, scenarios
│   ├── align.py           # Table alignment, trailing whitespace
│   ├── rules.py           # Formatting rules registry
│   └── formatter.py       # Main orchestrator (format_project)
├── printer/
│   ├── feature_printer.py
│   ├── scenario_printer.py
│   ├── step_printer.py
│   ├── table_printer.py
│   └── tag_printer.py
└── cli/
    └── main.py            # CLI entry point
```

## Pipeline

1. **Normalize** — clean whitespace, standardize indentation, normalize tags
2. **Sort** — order tags (alphabetically by default), optionally features and scenarios
3. **Align** — align table columns, remove trailing spaces
4. **Print** — convert `behave-model` → `.feature` text (deterministic)

## Safety

The formatter NEVER changes semantics:

- Feature names: preserved
- Scenario names: preserved
- Step text: preserved (only whitespace normalized)
- DocString content: preserved
- Table values: preserved (only alignment changes)
- Comments content: preserved

## Integration

`behave-format` integrates naturally with the Behave ecosystem:

- [behave-model](https://github.com/MathiasPaulenko/behave-model) — single source of truth
- [behave-lint](https://github.com/MathiasPaulenko/behave-lint) — linting
- [behave-modern-json-report](https://github.com/MathiasPaulenko/behave-modern-json-report)
- [behave-modern-report](https://github.com/MathiasPaulenko/behave-modern-report)
- [behave-markdown-report](https://github.com/MathiasPaulenko/behave-markdown-report)

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check .
ruff format --check .
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Run `ruff check .` and `pytest tests/` before submitting
4. Open a Pull Request

## License

MIT