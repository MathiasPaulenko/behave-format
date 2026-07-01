# Python API

## Main functions

### `format_project`

```python
from behave_model import Project
from behave_format import format_project, Settings

project = load_project("features/")
format_project(project, Settings())
```

Formats a `Project` in place. Returns the same project.

### `render_project`

```python
from behave_format import render_project

text = render_project(project, Settings())
```

Formats and renders the entire project as `.feature` text.

### `render_feature`

```python
from behave_format import render_feature

text = render_feature(feature, Settings())
```

Formats and renders a single `Feature` as `.feature` text.

### `format_feature`

```python
from behave_format import format_feature

format_feature(feature, Settings())
```

Formats a single `Feature` in place.

## Settings

```python
from behave_format import Settings

# Defaults
settings = Settings()

# Custom
settings = Settings(indent=4, sort_tags=True, sort_scenarios=True)

# From pyproject.toml
settings = Settings.from_pyproject("pyproject.toml")

# From dict
settings = Settings.from_dict({"indent": 4})
```
