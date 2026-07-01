# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
