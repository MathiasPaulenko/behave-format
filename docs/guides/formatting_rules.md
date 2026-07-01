# Formatting Rules

## Tags

Tags are sorted alphabetically by default:

```gherkin
@api @smoke
```

## Features

- One blank line before each Feature
- Clean title formatting

## Scenarios

- One blank line before each Scenario
- Two-space indentation for steps

```gherkin
  Given user exists
  When user logs in
  Then dashboard is shown
```

## Tables

Tables are always aligned:

Before:

```gherkin
|user|password|
|john|123|
```

After:

```gherkin
| user | password |
| john | 123      |
```

## Blank Lines

- No trailing blank lines
- No multiple consecutive empty lines
- Consistent spacing between blocks

## Indentation

- Spaces only (no tabs)
- Default: 2 spaces
