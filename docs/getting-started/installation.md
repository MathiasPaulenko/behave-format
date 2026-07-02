# Installation

## Requirements

- Python >= 3.11
- [behave-model](https://github.com/MathiasPaulenko/behave-model) >= 0.1.0

## From PyPI

=== "pip"

    ```bash
    pip install behave-format
    ```

=== "pipx"

    ```bash
    pipx install behave-format
    ```

=== "uv"

    ```bash
    uv pip install behave-format
    ```

## From source

```bash
git clone https://github.com/MathiasPaulenko/behave-format.git
cd behave-format
pip install -e ".[dev]"
```

## Pre-commit hook

Add behave-format to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/MathiasPaulenko/behave-format
    rev: v1.0.1
    hooks:
      - id: behave-format
```

Then install the hook:

```bash
pre-commit install
pre-commit run --all-files
```

## Verify installation

```bash
behave-format --version
# behave-format 1.0.1
```

```bash
behave-format --help
# Usage: behave-format [OPTIONS] PATH...
```

## Editor integration

### VS Code

Add to `.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode"
}
```

Or use a task in `.vscode/tasks.json`:

```json
{
  "label": "Format Feature Files",
  "command": "behave-format",
  "args": ["${workspaceFolder}/features/"],
  "type": "shell"
}
```

### Vim / Neovim

Use `--stdin` mode with your formatter of choice:

```vim
autocmd BufWritePre *.feature :%!behave-format --stdin
```

### Any editor

behave-format supports `--stdin` mode, which reads from stdin and writes
formatted output to stdout. This works with any editor that supports
external formatters:

```bash
behave-format --stdin < my-feature.feature
```
