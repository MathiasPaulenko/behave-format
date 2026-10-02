# Pipeline

The formatting pipeline consists of four stages applied in order: **normalize → sort → align → print**. Each stage operates on the `behave-model` `Project` in place.

## Normalize

Cleans whitespace, standardizes indentation, normalizes tag names (ensures `@` prefix), strips trailing whitespace from comments, and ensures table cells are stripped. This stage never changes semantics.

::: behave_format.pipeline.normalize

## Sort

Orders tags, features, and scenarios. By default only tags are sorted alphabetically. Feature and scenario sorting are opt-in via `Settings`.

::: behave_format.pipeline.sort

## Align

Ensures tables are rectangular (pads short rows, extends headers when a row has extra cells) and removes trailing whitespace. This stage operates on the model before printing and never drops cell values.

::: behave_format.pipeline.align
