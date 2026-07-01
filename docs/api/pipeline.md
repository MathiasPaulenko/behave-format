# Pipeline

The formatting pipeline consists of four stages applied in order: **normalize → sort → align → print**. Each stage operates on the `behave-model` `Project` in place.

## Normalize

Cleans whitespace, standardizes indentation, normalizes tag names (ensures `@` prefix), strips trailing whitespace from comments, and ensures table cells are stripped. This stage never changes semantics.

::: behave_format.pipeline.normalize

## Sort

Orders tags, features, and scenarios. By default only tags are sorted alphabetically. Feature and scenario sorting are opt-in via `Settings`.

::: behave_format.pipeline.sort

## Align

Ensures tables are rectangular (pads short rows, truncates long rows) and removes trailing whitespace. This stage operates on the model before printing.

::: behave_format.pipeline.align

## Rules

Defines a `Rule` type (callable that transforms a `Project` with `Settings`) and an `apply_rules` function for applying a sequence of rules in order.

::: behave_format.pipeline.rules
