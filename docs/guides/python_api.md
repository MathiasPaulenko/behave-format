# Python API

The Python API provides full control over the formatting process. You can format
projects or individual features, render to text, and customize all aspects via `Settings`.

## Importing

```python
from behave_format import (
    Settings,
    format_project,
    render_project,
    format_feature,
    render_feature,
)
```

## Main functions

### `format_project`

```python
def format_project(project: Project, settings: Settings | None = None) -> Project
```

Applies the full pipeline (normalize → sort → align) to a `behave-model` `Project`.
The project is mutated **in place** and returned.

```python
from behave_model import load_project
from behave_format import format_project, Settings

project = load_project("features/")
format_project(project, Settings(indent=4))

# project is now formatted in place
```

### `render_project`

```python
def render_project(project: Project, settings: Settings | None = None) -> str
```

Formats the project and returns the formatted `.feature` text for all features,
joined by blank lines.

```python
from behave_model import load_project
from behave_format import render_project

project = load_project("features/")
text = render_project(project)
print(text)
```

### `format_feature`

```python
def format_feature(feature: Feature, settings: Settings | None = None) -> Feature
```

Formats a single `Feature` in place. Applies normalization, sorting, and alignment.

```python
from behave_model import load_feature
from behave_format import format_feature, Settings

feature = load_feature("features/login.feature")
format_feature(feature, Settings(indent=2))
```

### `render_feature`

```python
def render_feature(feature: Feature, settings: Settings | None = None) -> str
```

Formats a single feature and returns the formatted `.feature` file content as a string.

```python
from behave_model import load_feature
from behave_format import render_feature, Settings

feature = load_feature("features/login.feature")
text = render_feature(feature, Settings(indent=2))
print(text)
```

## Settings

`Settings` is an immutable (frozen) dataclass that controls formatting behavior.

### Creating settings

```python
from behave_format import Settings

# Default settings (indent=2, sort_tags=True, etc.)
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
```

### Immutable override

```python
settings = Settings(indent=2)
settings = settings.with_indent(4)  # Returns new Settings with indent=4

# Original is unchanged
assert settings.indent == 4
```

### Inspecting settings

```python
settings = Settings()
print(settings.indent)          # 2
print(settings.sort_tags)       # True
print(settings.sort_features)   # False
print(settings.sort_scenarios)  # False
print(settings.line_length)     # 120
```

## Advanced usage

### Format without writing

```python
from behave_model import load_project
from behave_format import render_project, Settings

project = load_project("features/")
formatted_text = render_project(project, Settings())

# Compare with original
for feature in project.features:
    original = feature.source_file.read_text()
    formatted = render_feature(feature, Settings())
    if original != formatted:
        print(f"Would reformat: {feature.source_file}")
```

### Custom pipeline

```python
from behave_model import load_project
from behave_format import Settings
from behave_format.pipeline.normalize import normalize_project
from behave_format.pipeline.sort import sort_project
from behave_format.pipeline.align import align_project
from behave_format.pipeline.rules import apply_rules

project = load_project("features/")
settings = Settings(indent=4)

# Run only specific stages
normalize_project(project, settings)
sort_project(project, settings)
# Skip align if you want
```

### Batch processing

```python
from pathlib import Path
from behave_model import load_feature
from behave_format import format_feature, render_feature, Settings

settings = Settings(indent=2)

for fpath in Path("features/").rglob("*.feature"):
    feature = load_feature(fpath)
    format_feature(feature, settings)
    formatted = render_feature(feature, settings)

    if formatted + "\n" != fpath.read_text():
        fpath.write_text(formatted + "\n")
        print(f"Formatted: {fpath}")
```

### Integration with behave-model

```python
from behave_model import load_project, load_feature
from behave_format import format_project, render_project, Settings

# Load and format an entire project
project = load_project("features/")
format_project(project, Settings())
text = render_project(project, Settings())

# Or work with individual features
feature = load_feature("features/login.feature")
format_feature(feature, Settings())
text = render_feature(feature, Settings())
```

## Type hints

All public API functions are fully type-annotated:

```python
from behave_format import Settings, format_project, render_project
from behave_model import Project, Feature

# Type signatures
# format_project(project: Project, settings: Settings | None = None) -> Project
# render_project(project: Project, settings: Settings | None = None) -> str
# format_feature(feature: Feature, settings: Settings | None = None) -> Feature
# render_feature(feature: Feature, settings: Settings | None = None) -> str
```

## Error handling

The API does not raise exceptions on malformed input — that's behave-model's job.
If `load_project` or `load_feature` succeeds, formatting will always succeed.

```python
from behave_model import load_feature
from behave_format import format_feature, Settings

try:
    feature = load_feature("features/broken.feature")
    format_feature(feature, Settings())
except Exception as e:
    print(f"Error: {e}")
```
