# behave-format

> The opinionated formatter for Behave `.feature` files.

**behave-format** is the equivalent of [Black](https://github.com/psf/black) for Gherkin `.feature` files.

It consumes the canonical domain model from [behave-model](https://github.com/MathiasPaulenko/behave-model) and produces deterministic, beautifully formatted output.

## Key Principle

behave-format does NOT parse Gherkin. It does NOT lint. It does NOT validate.
It ONLY transforms a `behave-model.Project` into formatted `.feature` files.

```text
.feature files → behave-model → behave-format → formatted .feature files
```

## Features

- **Opinionated** — minimal configuration, sensible defaults
- **Deterministic** — same input always produces same output
- **Idempotent** — `format(format(x)) == format(x)`
- **Fast** — handles thousands of feature files efficiently
- **CI-friendly** — `--check` mode with exit code 1 when formatting is needed
- **Safe** — never changes semantics
