# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.2] - 2026-11-17

### Fixed

- Comments at end of file now stay at the end instead of moving before
  the last element
- Comments before `Background:` and `Examples:` blocks keep their
  position instead of being pulled inside the block
- Comments inside step tables and Examples tables are emitted after the
  table instead of drifting to the following element
- Inline comments on tag lines (`@tag # note`) are preserved as comments
- `'''` docstrings keep their delimiter and content type; `#` lines
  inside them are no longer duplicated as comments
- Empty docstrings (`"""\n"""`) are no longer dropped
- Docstring-like `"""`/`'''` text inside descriptions no longer
  desynchronizes comment restoration
- `Background:` descriptions and empty `Background:` blocks are preserved
- Headers-only step tables are no longer dropped (falsy `Table.__len__`)
- behave's phantom default Rule background is no longer printed as an
  empty `Background:`
- Non-breaking and other Unicode spaces inside step/element names are
  preserved instead of collapsing to ASCII spaces
- Escaped quotes inside step literals keep their interior whitespace
- UTF-8 BOM input parses and is normalized away
- `render_feature`/`render_project` with `settings=None` now produce the
  same output as the default `Settings()`
- `Settings.from_pyproject` no longer crashes on non-table
  `[tool.behave-format]` sections; `from_dict` validates its input
- `--config` with a missing file now exits with code 2 instead of
  silently using defaults
- Empty or feature-less `.feature` files report a clear
  "no feature found" error instead of an `AttributeError`
- stdin/stdout/stderr I/O is UTF-8 regardless of the console encoding
- Atomic writes fsync before replace and preserve file permissions
- Directory scans that hit `OSError` (e.g. permissions) report an error
  instead of crashing
- `Examples:` headers without a table no longer crash the loader
- Formatting a symlinked file now writes the real file instead of
  replacing the link itself
- Non-boolean `sort_*`/`line_length` values and boolean `indent` in
  `pyproject.toml` are rejected instead of silently coerced
- A broken stdout pipe (`| head`) exits cleanly without a traceback

## [1.2.1] - 2026-10-16

### Fixed

- Shortened `action.yml` description to meet Marketplace limits

## [1.2.0] - 2026-10-16

### Added

- GitHub Action (`action.yml`) for `--check` / `--diff` / format modes in CI

## [1.1.0] - 2026-10-02

### Added

- `load_feature_text()` and `load_feature_file()` in `behave_format.loader`:
  parse feature text while restoring what `behave`'s parser discards —
  comments, original Gherkin keywords, and docstring content types
- `line_length` now wraps long tag lines onto continuation lines
- Config auto-discovery walks upward from each target path (and from the
  current directory for `--stdin`); `--config` still overrides
- `--check` mode now reports each file that would be reformatted
- `--stdin` supports `--diff`

### Fixed

- Table cells containing `\|` are re-escaped on output; previously the
  formatter emitted invalid Gherkin that could not be re-parsed
- Comments are no longer deleted from formatted files
- Non-English features keep their original keywords (`Característica`,
  `Escenario`, `Regla`, ...) instead of being rewritten with English
  keywords under a `# language:` directive that made output unparseable
- Docstring content types (`"""json`, `"""text/plain`, ...) are preserved
- Step text whitespace is no longer collapsed inside `"..."`, `'...'`
  and `<placeholder>` literals (changed the arguments step definitions
  would match)
- Feature/scenario/rule descriptions keep their interior spacing
- Directory mode parse errors now exit with code 2 (previously swallowed)
- Files are written with LF endings deterministically (previously followed
  `os.linesep`, producing CRLF on Windows) and atomically
- `format_feature` now honors `sort_scenarios` like `format_project`
- `sort_tags = false` no longer sorts `project.global_tags` anyway
- Ragged tables pad missing cells instead of truncating extra ones
- Duplicate tags are removed
- Empty lines inside docstrings no longer emit trailing whitespace
- `--indent` rejects values below 1; invalid config values exit with
  code 2 instead of a traceback
- `.venv`, `node_modules` and other tooling directories are skipped when
  formatting a directory recursively
- Removed dead `pipeline/rules.py` rule registry

### Changed

- Table column widths are computed on escaped cell text and use display
  width for CJK/emoji characters

## [1.0.2] - 2026-07-29

### Added

- `.pre-commit-hooks.yaml` — drop-in pre-commit integration
- Expanded documentation site (guides, API reference, examples, architecture)

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
