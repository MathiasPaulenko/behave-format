# CLI Usage

## Commands

### Format files (default)

```bash
behave-format features/
```

Rewrites `.feature` files in place with formatted output.

### Check mode (CI)

```bash
behave-format --check features/
```

Exits with code `1` if any file would be reformatted. Does not write files.

### Diff mode

```bash
behave-format --diff features/
```

Shows unified diffs without writing files. Exits with code `0`.

### Quiet mode

```bash
behave-format --quiet features/
```

Suppresses all output except errors.

### Custom config

```bash
behave-format --config path/to/pyproject.toml features/
```

## Exit Codes

| Code | Meaning                          |
| ---- | -------------------------------- |
| `0`  | Success / no changes needed      |
| `1`  | Formatting needed (`--check`)    |
