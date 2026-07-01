# API Reference

## Overview

behave-format provides a minimal, focused API for formatting Behave `.feature` files. It consumes a `behave-model` `Project` and produces deterministic, beautifully formatted output.

## Public API

The following functions and classes are exported from the top-level `behave_format` package:

| Name | Type | Description |
| --- | --- | --- |
| `Settings` | `dataclass` | Immutable formatter configuration. |
| `format_project` | `function` | Format a `Project` in place (normalize → sort → align). |
| `render_project` | `function` | Format and render a `Project` as `.feature` text. |
| `format_feature` | `function` | Format a single `Feature` in place. |
| `render_feature` | `function` | Format and render a single `Feature` as `.feature` text. |

## Usage

```python
from behave_format import Settings, format_project, render_project
from behave_model import load_project

project = load_project("features/")
format_project(project)  # mutates in place

# Or render to text without writing:
text = render_project(project, Settings(indent=4))
```

## Modules

- [Settings](settings.md) — Configuration dataclass
- [Formatter](formatter.md) — Main orchestrator functions
- [Printers](printers.md) — Gherkin text generation
- [Pipeline](pipeline.md) — Normalize, sort, align, rules
