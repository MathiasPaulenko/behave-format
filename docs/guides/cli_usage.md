# CLI Usage

## Synopsis

```text
behave-format [OPTIONS] [PATH...]
behave-format --stdin [OPTIONS] < file.feature
```

## Commands

### Format files (default)

```bash
behave-format features/
```

Rewrites `.feature` files in place with formatted output. Prints which files were reformatted.

```bash
# Single file
behave-format features/login.feature

# Multiple paths
behave-format features/login.feature features/checkout.feature

# Directory (recursive)
behave-format features/
```

### Check mode (CI)

```bash
behave-format --check features/
```

Exits with code `1` if any file would be reformatted. Does **not** write files.

**GitHub Actions example:**

```yaml
name: Check Formatting
on: [push, pull_request]
jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install behave-format
      - run: behave-format --check features/
```

**GitLab CI example:**

```yaml
format:
  script:
    - pip install behave-format
    - behave-format --check features/
```

### Diff mode

```bash
behave-format --diff features/
```

Shows unified diffs without writing files. Exits with code `0`. Useful for reviewing what would change before committing.

```bash
# Show diff for a single file
behave-format --diff features/login.feature

# Combine with check mode for CI with visible diffs
behave-format --check --diff features/
```

### Stdin mode

```bash
behave-format --stdin < features/login.feature
```

Reads from stdin, writes formatted output to stdout. Does not write any files.

```bash
# Pipe from cat
cat features/login.feature | behave-format --stdin

# Use as a filter in vim
:%!behave-format --stdin

# Check stdin (exit 1 if would change)
echo '@smoke Feature: Test' | behave-format --stdin --check
```

### Quiet mode

```bash
behave-format --quiet features/
```

Suppresses all output except errors. Useful in scripts where you only care about the exit code.

### Custom config

```bash
behave-format --config path/to/pyproject.toml features/
```

Use a specific `pyproject.toml` instead of auto-discovering one in the current directory.

### Custom indentation

```bash
behave-format --indent 4 features/
```

Overrides the `indent` setting from `pyproject.toml`. Useful for one-off formatting without changing project config.

## All flags

| Flag | Type | Description |
|------|------|-------------|
| `--check` | flag | Check mode: exit 1 if formatting needed, don't write |
| `--diff` | flag | Show unified diffs without writing |
| `--stdin` | flag | Read from stdin, write to stdout |
| `--indent N` | int | Override indentation (number of spaces) |
| `--config PATH` | str | Path to pyproject.toml (default: auto-discover) |
| `--quiet` | flag | Suppress output except errors |
| `--version` | flag | Show version and exit |
| `--help` | flag | Show help message and exit |

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success — all files formatted or no changes needed |
| `1` | Formatting needed (`--check` mode) |
| `2` | Error — file not found, parse error, or other failure |

## Common patterns

### Pre-commit workflow

```bash
# Stage your changes
git add features/

# Run formatter
behave-format features/

# Stage formatted files
git add features/

# Commit
git commit -m "feat: add new scenarios"
```

### CI pipeline with diff output

```bash
# In CI: show what would change, then fail
behave-format --check --diff features/
# Output:
#   --- features/login.feature
#   +++ features/login.feature
#   @@ -1,3 +1,3 @@
#   -@smoke @auth
#   +@auth @smoke
#   Files would be reformatted
# Exit code: 1
```

### Format only changed files

```bash
# Format only files changed in the last commit
git diff --name-only HEAD~1 -- '*.feature' | xargs behave-format
```

### Python module mode

```bash
# Instead of the behave-format command, use python -m
python -m behave_format features/
python -m behave_format --check features/
python -m behave_format --stdin < file.feature
```
