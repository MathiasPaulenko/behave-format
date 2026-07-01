# Quick Start

## CLI

```bash
# Format files in place (default)
behave-format features/

# Check mode (CI) — exit 1 if formatting is needed
behave-format --check features/

# Diff mode — show differences without writing
behave-format --diff features/
```

## Python API

```python
from behave_model import load_project
from behave_format import format_project, render_project, Settings

project = load_project("features/")

# Format the project model in place
format_project(project)

# Or render to text
text = render_project(project, Settings())
```
