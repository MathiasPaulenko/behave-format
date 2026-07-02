# Formatting Rules

behave-format applies a set of opinionated formatting rules to your `.feature` files.
All rules are designed to be **safe** — they never change the semantics of your tests.

## Tags

Tags are sorted alphabetically by default (`sort_tags = true`).

### Before

```gherkin
@smoke @auth @regression
Feature: Login
```

### After

```gherkin
@auth @regression @smoke
Feature: Login
```

!!! note "Disabling tag sorting"

    Set `sort_tags = false` in `pyproject.toml` to preserve tag order.

## Features

- One blank line before each `Feature` keyword
- Clean title formatting (single space after `Feature:`)
- Description text preserved as-is (only whitespace normalized)

### Before

```gherkin
Feature:Login
As a user
I want to log in
```

### After

```gherkin
Feature: Login
  As a user
  I want to log in
```

## Scenarios

- One blank line before each `Scenario`, `Scenario Outline`, `Background`, and `Rule`
- Two-space indentation for steps (configurable via `indent`)
- Scenario tags sorted alphabetically

### Before

```gherkin
@happy @slow
Scenario: Successful login
Given the user is on the login page
When the user enters "admin" and "password"
Then the user should be logged in
```

### After

```gherkin
  @happy @slow
  Scenario: Successful login
    Given the user is on the login page
    When the user enters "admin" and "password"
    Then the user should be logged in
```

## Tables

Tables are always aligned with consistent padding. Column widths are computed from
the widest cell in each column (header or data).

### Before

```gherkin
|user|password|
|john|123|
|alice|secure_pass_123|
```

### After

```gherkin
    | user  | password         |
    | john  | 123              |
    | alice | secure_pass_123  |
```

!!! info "Alignment is automatic"

    You never need to manually align table columns. The formatter computes
    optimal widths and pads all cells consistently.

## Blank Lines

- No trailing blank lines at end of file
- No multiple consecutive empty lines (collapsed to one)
- Consistent single blank line between blocks (Feature → Background, Scenario → Scenario, etc.)
- Exactly one blank line between Feature description and first block
- Exactly one blank line between Scenarios

### Before

```gherkin
Feature: Login


  Background:
    Given a database connection



  Scenario: Login
    When the user logs in

```

### After

```gherkin
Feature: Login

  Background:
    Given a database connection

  Scenario: Login
    When the user logs in
```

## Indentation

- Spaces only (no tabs) — consistent with [Black's philosophy](https://github.com/psf/black)
- Default: 2 spaces (configurable via `indent`)
- Steps indented under their parent (Scenario, Background, Rule)
- Examples tables indented under Scenario Outline
- DocStrings preserved as-is (content not re-indented)

### Indentation levels

| Element | Indentation |
|---------|-------------|
| `Feature:` | 0 (column 0) |
| Feature description | 2 spaces |
| `Background:` / `Scenario:` / `Rule:` | 2 spaces |
| Steps (`Given`, `When`, `Then`, `And`, `But`) | 4 spaces |
| Tags on scenarios | 2 spaces |
| Examples table | 4 spaces |
| Table cells | 6 spaces |

## Comments

- Comments are preserved in the output
- Comment content is never modified
- `# language:` directives are preserved for non-English features
- Trailing whitespace on comment lines is stripped

## DocStrings

- DocString content is preserved exactly as-is
- Delimiters (`"""` or `'''`) are preserved
- Indentation of the DocString block is normalized to the step's indentation level

## What the formatter does NOT change

!!! warning "Semantic safety"

    The formatter never changes:

    - Feature names
    - Scenario names
    - Step text (only surrounding whitespace normalized)
    - DocString content
    - Table cell values (only alignment/padding changes)
    - Comment content
    - Tag names (only order changes when `sort_tags = true`)
