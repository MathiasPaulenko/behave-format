# Formatter

The formatter module is the main orchestrator for the formatting pipeline. It provides four public functions that cover the two main operations: **format** (mutate in place) and **render** (format + produce text).

## Module Reference

::: behave_format.pipeline.formatter

## Functions

### `format_project`

```python
def format_project(project: Project, settings: Settings | None = None) -> Project
```

Applies the full pipeline (normalize → sort → align) to a `behave-model` `Project`. The project is mutated and returned.

```python
from behave_format import format_project, Settings
from behave_model import load_project

project = load_project("features/")
format_project(project, Settings(indent=4))
```

### `render_project`

```python
def render_project(project: Project, settings: Settings | None = None) -> str
```

Formats the project and returns the formatted `.feature` text for all features, joined by blank lines.

```python
from behave_format import render_project
from behave_model import load_project

project = load_project("features/")
text = render_project(project)
print(text)
```

### `format_feature`

```python
def format_feature(feature: Feature, settings: Settings | None = None) -> Feature
```

Formats a single `Feature` in place. Applies normalization and tag sorting. Alignment is handled at print time.

### `render_feature`

```python
def render_feature(feature: Feature, settings: Settings | None = None) -> str
```

Formats a single feature and returns the formatted `.feature` file content as a string.

```python
from behave_format import render_feature, Settings
from behave_model import load_feature

feature = load_feature("features/login.feature")
text = render_feature(feature, Settings(indent=2))
```
