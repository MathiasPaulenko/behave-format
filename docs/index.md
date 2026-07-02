# behave-format

> The opinionated formatter for Behave `.feature` files.

[Black](https://github.com/psf/black) is for Python. [gofmt](https://go.dev/blog/gofmt) is for Go.
**behave-format** is for Gherkin.

---

## What it does

`behave-format` takes your Behave `.feature` files and produces clean, consistent,
deterministically formatted output — every time.

It consumes the canonical domain model from
[behave-model](https://github.com/MathiasPaulenko/behave-model) and transforms it
into beautifully formatted `.feature` files.

```text
.feature files → behave-model (domain model) → behave-format → formatted .feature files
```

## Key principle

!!! info "Separation of concerns"

    behave-format does **NOT** parse Gherkin. It does **NOT** lint. It does **NOT** validate.
    It **ONLY** transforms a `behave-model.Project` into formatted `.feature` files.

    - **Parsing** → [behave-model](https://github.com/MathiasPaulenko/behave-model)
    - **Linting** → [behave-lint](https://github.com/MathiasPaulenko/behave-lint)
    - **Formatting** → behave-format

## Features

- **:octicons-settings-16: Opinionated** — minimal configuration, sensible defaults that just work
- **:octicons-repeat-16: Deterministic** — same input always produces the same output
- **:octicons-check-circle-16: Idempotent** — `format(format(x)) == format(x)`
- **:octicons-zap-16: Fast** — handles thousands of feature files efficiently
- **:octicons-terminal-16: CI-friendly** — `--check` mode with exit code 1 when formatting is needed
- **:octicons-shield-check-16: Safe** — never changes semantics (names, step text, table values, docstrings)
- **:octicons-tools-16: Pre-commit ready** — drop-in hook for your pre-commit configuration
- **:octicons-keyboard-16: Stdin support** — integrate with any editor via `--stdin`

## Quick start

=== "CLI"

    ```bash
    # Install
    pip install behave-format

    # Format files in place
    behave-format features/

    # Check mode (CI) — exit 1 if formatting is needed
    behave-format --check features/

    # Diff mode — show differences without writing
    behave-format --diff features/
    ```

=== "Python API"

    ```python
    from behave_model import load_project
    from behave_format import format_project, render_project, Settings

    project = load_project("features/")

    # Format the project model in place
    format_project(project)

    # Or render to text
    text = render_project(project, Settings())
    ```

=== "Pre-commit"

    ```yaml
    # .pre-commit-config.yaml
    repos:
      - repo: https://github.com/MathiasPaulenko/behave-format
        rev: v1.0.1
        hooks:
          - id: behave-format
    ```

## Before / After

=== "Before"

    ```gherkin
    @smoke @auth
    Feature: Login
      As a user
      I want to log in

      Background:
        Given a database connection

      @happy
      Scenario: Successful login
        Given the user is on the login page
        When the user enters "admin" and "password"
        Then the user should be logged in
    ```

=== "After"

    ```gherkin
    @auth @smoke
    Feature: Login
      As a user
      I want to log in

      Background:
        Given a database connection

      @happy
      Scenario: Successful login
        Given the user is on the login page
        When the user enters "admin" and "password"
        Then the user should be logged in
    ```

## Ecosystem

`behave-format` is part of the Behave tooling ecosystem:

| Tool | Purpose |
|------|---------|
| [behave-model](https://github.com/MathiasPaulenko/behave-model) | Canonical domain model & Gherkin parser |
| **behave-format** | **Opinionated formatter for `.feature` files** |
| [behave-lint](https://github.com/MathiasPaulenko/behave-lint) | Linter for Gherkin `.feature` files |

## Next steps

- [Installation](getting-started/installation.md) — get up and running
- [Quick Start](getting-started/quick_start.md) — format your first files
- [Formatting Rules](guides/formatting_rules.md) — understand what the formatter does
- [Configuration](guides/configuration.md) — customize behavior via `pyproject.toml`
- [CLI Usage](guides/cli_usage.md) — full CLI reference
