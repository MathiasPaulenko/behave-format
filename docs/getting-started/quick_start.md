# Quick Start

## CLI

### Format files in place

```bash
behave-format features/
```

Rewrites `.feature` files in place with formatted output. Prints which files were reformatted.

### Check mode (CI)

```bash
behave-format --check features/
```

Exits with code `1` if any file would be reformatted. Does **not** write files. Perfect for CI pipelines:

```yaml
# .github/workflows/ci.yml
- name: Check formatting
  run: behave-format --check features/
```

### Diff mode

```bash
behave-format --diff features/
```

Shows unified diffs without writing files. Exits with code `0`. Useful for reviewing what would change before committing.

### Stdin mode

```bash
cat features/login.feature | behave-format --stdin
```

Reads from stdin, writes formatted output to stdout. Works with any editor or pipeline:

```bash
# Pipe from another tool
echo '@smoke Feature: Test' | behave-format --stdin
```

### Custom indentation

```bash
behave-format --indent 4 features/
```

Overrides the indentation setting from `pyproject.toml` without modifying any config files.

## Python API

### Format a project

```python
from behave_model import load_project
from behave_format import format_project, Settings

project = load_project("features/")
format_project(project, Settings())
```

`format_project` mutates the `Project` in place and returns it.

### Render to text

```python
from behave_model import load_project
from behave_format import render_project, Settings

project = load_project("features/")
text = render_project(project, Settings(indent=4))
print(text)
```

`render_project` formats and returns the entire project as `.feature` text.

### Format a single feature

```python
from behave_model import load_feature
from behave_format import format_feature, render_feature, Settings

feature = load_feature("features/login.feature")
format_feature(feature, Settings())

# Or render to text
text = render_feature(feature, Settings())
```

### Custom settings

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

# From pyproject.toml
settings = Settings.from_pyproject("pyproject.toml")

# From dict
settings = Settings.from_dict({"indent": 4, "sort_tags": False})
```

## Next steps

- [Formatting Rules](../guides/formatting_rules.md) — understand exactly what the formatter changes
- [Configuration](../guides/configuration.md) — all configuration options
- [CLI Usage](../guides/cli_usage.md) — full CLI reference
- [Python API](../guides/python_api.md) — complete API guide
