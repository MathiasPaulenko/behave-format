# Architecture

## Design

behave-format is intentionally minimal:

- **No parsing** — relies entirely on behave-model
- **No linting** — that's behave-lint's job
- **No validation** — that's behave-model's job
- **Only formatting** — deterministic transformation of model → text

## Module Structure

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

## Data Flow

```text
.feature files
      │
      ▼
behave-model (domain model)
      │
      ▼
behave-format (transformation layer)
      │
      ▼
formatted .feature files
```
