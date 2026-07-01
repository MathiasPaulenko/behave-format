# Settings

`Settings` is an immutable dataclass that controls the formatting behavior. It can be constructed directly, loaded from `pyproject.toml`, or created from a dictionary.

## Class Reference

::: behave_format.config.settings.Settings

## Configuration Options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `indent` | `int` | `2` | Number of spaces for indentation. |
| `sort_tags` | `bool` | `True` | Sort tags alphabetically. |
| `sort_features` | `bool` | `False` | Sort features by name. |
| `sort_scenarios` | `bool` | `False` | Sort scenarios by name. |
| `line_length` | `int` | `120` | Maximum line length for reference. |

## Loading from `pyproject.toml`

```python
from behave_format import Settings

settings = Settings.from_pyproject("pyproject.toml")
```

The `[tool.behave-format]` section in `pyproject.toml`:

```toml
[tool.behave-format]
indent = 4
sort_tags = true
sort_features = false
sort_scenarios = false
line_length = 120
```

## Creating from a Dictionary

```python
from behave_format import Settings

settings = Settings.from_dict({"indent": 4, "sort_tags": False})
```

## Immutability

`Settings` is a frozen dataclass. Once created, its attributes cannot be modified:

```python
settings = Settings()
settings.indent = 4  # raises AttributeError
```
