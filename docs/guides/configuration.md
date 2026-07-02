# Configuration

behave-format is **opinionated** — it works out of the box with zero configuration.
But when you need to customize, all settings live in `pyproject.toml` under `[tool.behave-format]`.

## Quick reference

```toml
[tool.behave-format]
indent = 2
sort_tags = true
sort_features = false
sort_scenarios = false
line_length = 120
```

## Options

### `indent`

| | |
|---|---|
| **Type** | `int` |
| **Default** | `2` |
| **CLI flag** | `--indent N` |

Number of spaces for indentation. Must be a positive integer.

```toml
[tool.behave-format]
indent = 4
```

```bash
# Override from CLI
behave-format --indent 4 features/
```

### `sort_tags`

| | |
|---|---|
| **Type** | `bool` |
| **Default** | `true` |

Sort tags alphabetically within each tag group (Feature-level and Scenario-level).

```toml
[tool.behave-format]
sort_tags = false  # preserve original tag order
```

### `sort_features`

| | |
|---|---|
| **Type** | `bool` |
| **Default** | `false` |

Sort features alphabetically by name within a project.

!!! warning "Use with caution"

    Sorting features changes the order of files in your project.
    This may affect test execution order.

### `sort_scenarios`

| | |
|---|---|
| **Type** | `bool` |
| **Default** | `false` |

Sort scenarios alphabetically by name within each feature.

### `line_length`

| | |
|---|---|
| **Type** | `int` |
| **Default** | `120` |

Maximum line length for reference. Currently used as a guideline — the formatter
does not hard-wrap long lines, but future versions may use this for smart wrapping.

## Configuration precedence

Settings are resolved in the following order (highest to lowest):

1. **CLI flags** (`--indent`) — override everything
2. **`pyproject.toml`** (`[tool.behave-format]`) — project-level defaults
3. **Built-in defaults** — sensible fallbacks

```bash
# pyproject.toml says indent=2, but CLI overrides to 4
behave-format --indent 4 features/
```

## Custom config file

By default, behave-format auto-discovers `pyproject.toml` in the current directory.
You can specify a custom path:

```bash
behave-format --config path/to/custom-pyproject.toml features/
```

## Programmatic configuration

```python
from behave_format import Settings

# Default settings
settings = Settings()

# Custom settings
settings = Settings(
    indent=4,
    sort_tags=True,
    sort_features=False,
    sort_scenarios=True,
    line_length=100,
)

# From a dict
settings = Settings.from_dict({"indent": 4, "sort_tags": False})

# From pyproject.toml
settings = Settings.from_pyproject("pyproject.toml")

# Immutable override
settings = Settings(indent=2)
settings = settings.with_indent(4)  # returns new Settings with indent=4
```

!!! info "Settings are immutable"

    `Settings` is a frozen dataclass. Once created, you cannot modify its
    attributes directly. Use `with_indent()` or create a new instance.

## Environment-specific configs

You can maintain multiple config files for different environments:

```bash
# Development (2-space indent)
behave-format --config pyproject.dev.toml features/

# Production (4-space indent)
behave-format --config pyproject.prod.toml features/
```

## Example configurations

=== "Minimal (defaults)"

    ```toml
    # pyproject.toml — no [tool.behave-format] section needed
    # All defaults apply: indent=2, sort_tags=true, etc.
    ```

=== "Standard"

    ```toml
    [tool.behave-format]
    indent = 2
    sort_tags = true
    sort_features = false
    sort_scenarios = false
    line_length = 120
    ```

=== "Strict"

    ```toml
    [tool.behave-format]
    indent = 4
    sort_tags = true
    sort_features = true
    sort_scenarios = true
    line_length = 100
    ```

=== "Preserve order"

    ```toml
    [tool.behave-format]
    indent = 2
    sort_tags = false
    sort_features = false
    sort_scenarios = false
    line_length = 120
    ```
