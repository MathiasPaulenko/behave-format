# API Reference

## Overview

behave-format provides a minimal, focused API for formatting Behave `.feature` files.
It consumes a `behave-model` `Project` and produces deterministic, beautifully formatted output.

## Public API

The following functions and classes are exported from the top-level `behave_format` package:

| Name | Type | Description |
|------|------|-------------|
| `Settings` | `dataclass` | Immutable formatter configuration. |
| `format_project` | `function` | Format a `Project` in place (normalize → sort → align). |
| `render_project` | `function` | Format and render a `Project` as `.feature` text. |
| `format_feature` | `function` | Format a single `Feature` in place. |
| `render_feature` | `function` | Format and render a single `Feature` as `.feature` text. |

## Quick usage

```python
from behave_format import Settings, format_project, render_project
from behave_model import load_project

project = load_project("features/")

# Format in place
format_project(project)

# Or render to text without writing
text = render_project(project, Settings(indent=4))
```

## Function signatures

```python
def format_project(project: Project, settings: Settings | None = None) -> Project
def render_project(project: Project, settings: Settings | None = None) -> str
def format_feature(feature: Feature, settings: Settings | None = None) -> Feature
def render_feature(feature: Feature, settings: Settings | None = None) -> str
```

## Module reference

- [Settings](settings.md) — Configuration dataclass with `from_pyproject`, `from_dict`, `with_indent`
- [Formatter](formatter.md) — Main orchestrator functions (`format_project`, `render_project`, etc.)
- [Printers](printers.md) — Gherkin text generation (`feature_printer`, `scenario_printer`, etc.)
- [Pipeline](pipeline.md) — Pipeline stages (`normalize`, `sort`, `align`, `rules`)
