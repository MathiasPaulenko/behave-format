# Printers

Printer modules convert `behave-model` objects into formatted Gherkin text. Each printer handles a specific model element and is responsible for indentation, alignment, and spacing.

## Feature Printer

Formats a complete `Feature` — including tags, description, background, scenarios, scenario outlines, and rules — into a full `.feature` file string.

::: behave_format.printer.feature_printer

## Scenario Printer

Formats `Background`, `Scenario`, and `ScenarioOutline` blocks, including their tags, descriptions, steps, and examples tables.

::: behave_format.printer.scenario_printer

## Step Printer

Formats a `Step` with proper indentation, including attached `DocString` and data `Table`.

::: behave_format.printer.step_printer

## Table Printer

Formats a `Table` with aligned columns. Computes column widths from headers and all rows to produce a rectangular, padded table.

::: behave_format.printer.table_printer

## Tag Printer

Formats a list of `Tag` objects as space-separated lines, wrapping onto
continuation lines when `line_length` is exceeded.

::: behave_format.printer.tag_printer

## Keywords

Resolves the Gherkin keyword to print for each element — the original
keyword when the element was parsed from a file, or the canonical i18n
alias for the feature's language.

::: behave_format.printer.keywords
