# Configuration

Minimal configuration via `pyproject.toml`:

```toml
[tool.behave-format]
indent = 2
sort_tags = true
sort_features = false
sort_scenarios = false
line_length = 120
```

## Options

| Option           | Default | Description                        |
| ---------------- | ------- | ---------------------------------- |
| `indent`         | `2`     | Number of spaces for indentation   |
| `sort_tags`      | `true`  | Sort tags alphabetically           |
| `sort_features`  | `false` | Sort features by name              |
| `sort_scenarios` | `false` | Sort scenarios by name             |
| `line_length`    | `120`   | Maximum line length (reference)    |

## Programmatic Configuration

```python
from behave_format import Settings

settings = Settings(
    indent=4,
    sort_tags=True,
    sort_features=False,
    sort_scenarios=True,
    line_length=100,
)

# Or from a dict
settings = Settings.from_dict({"indent": 4, "sort_tags": False})

# Or from pyproject.toml
settings = Settings.from_pyproject("pyproject.toml")
```
