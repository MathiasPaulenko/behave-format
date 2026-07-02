# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2025-07-02

### Added

- `python -m behave_format` support via `__main__.py`
- `--stdin` flag: read from stdin, write formatted output to stdout (editor integration)
- `--indent` flag: override indentation from CLI without editing pyproject.toml
- `--version` flag showing `behave-format <version>`
- `Settings.with_indent()` method for immutable indent override
- behave-format as a local pre-commit hook in `.pre-commit-config.yaml`
- CI, Docs, PyPI, Python versions, and License badges in README

### Fixed

- Comments now preserved in output for features, rules, scenarios, scenario outlines, and steps
- `# language:` directive preserved for non-English features
- CLI error handling: file-not-found and parse errors now exit with code 2 instead of crashing
- `format_feature` now applies align stage for pipeline consistency with `format_project`
- `_align_table` signature bug fixed (examples_table kwarg mismatch)
- `render_feature` and `render_project` now include trailing newline for consistency with CLI output

## [1.0.0] - 2025-07-02

### Added

- Initial release of behave-format
- Opinionated, deterministic formatter for Behave `.feature` files
- Consumes `behave-model.Project` as input (no direct Gherkin parsing)
- Formatting pipeline: normalize → sort → align → print
- Tags sorted alphabetically by default
- Table column alignment
- Whitespace normalization (trailing spaces, indentation)
- CLI with `--check` (CI mode), `--diff`, and write modes
- Configuration via `pyproject.toml` under `[tool.behave-format]`
- Golden file tests, idempotency tests, CLI tests, performance tests
- GitHub Actions CI workflow (lint, test, coverage, packaging)
