# Formatting Pipeline

The formatting process follows a strict 4-stage pipeline:

```text
Input (behave-model Project)
    │
    ▼
1. Normalize
    │  - Clean whitespace
    │  - Standardize indentation
    │  - Normalize tags structure
    │  - Ensure internal consistency
    │
    ▼
2. Sort
    │  - Tags sorted alphabetically (default)
    │  - Features sorted optionally
    │  - Scenarios sorted optionally
    │
    ▼
3. Align
    │  - Align tables
    │  - Normalize columns spacing
    │  - Remove trailing spaces
    │  - Ensure consistent indentation
    │
    ▼
4. Print
    │  - Convert behave-model → .feature text
    │  - Deterministic output
    │
    ▼
Formatted .feature files
```

## Idempotency

A critical requirement:

```text
format(format(project)) == format(project)
```

Running the formatter twice always produces identical output.
