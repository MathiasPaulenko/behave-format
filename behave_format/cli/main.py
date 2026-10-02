"""CLI entry point for behave-format.

Usage:
    behave-format [OPTIONS] PATH...
    behave-format --stdin < file.feature

Options:
    --check          Check mode: exit 1 if formatting is needed, don't write.
    --diff           Show diffs without writing files.
    --stdin          Read from stdin, write formatted output to stdout.
    --indent N       Override indentation (number of spaces).
    --config PATH    Path to pyproject.toml (default: auto-discover).
    --quiet          Suppress output except errors.
    --help           Show help message.
"""

from __future__ import annotations

import argparse
import difflib
import os
import sys
import tempfile
from pathlib import Path

from behave_format import __version__
from behave_format.config.settings import Settings
from behave_format.loader import load_feature_text
from behave_format.pipeline.formatter import format_feature
from behave_format.printer.feature_printer import print_feature

_IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".tox",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "build",
    "dist",
    ".eggs",
    "htmlcov",
    "site",
}


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv).

    Returns:
        Exit code: 0 on success, 1 if formatting is needed (--check),
        2 on errors or invalid arguments.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.indent is not None and args.indent < 1:
        parser.error("--indent must be >= 1")

    if args.stdin and args.paths:
        parser.error("cannot combine --stdin with file paths")

    settings_cache: dict = {}

    if args.stdin:
        settings = _resolve_settings(Path.cwd(), args.config, args.indent, settings_cache)
        if settings is None:
            return 2
        return _process_stdin(settings, check=args.check, diff=args.diff, quiet=args.quiet)

    paths = [Path(p) for p in args.paths]
    if not paths:
        parser.print_help()
        return 0

    files, had_errors = _collect_files(paths)

    needs_formatting = False
    for fpath in files:
        settings = _resolve_settings(fpath.parent, args.config, args.indent, settings_cache)
        if settings is None:
            return 2
        try:
            if _process_file(fpath, settings, check=args.check, diff=args.diff, quiet=args.quiet):
                needs_formatting = True
        except Exception as e:
            print(f"Error: {fpath}: {e}", file=sys.stderr)
            had_errors = True

    if had_errors:
        return 2

    if args.check and needs_formatting:
        if not args.quiet:
            print("Files would be reformatted")
        return 1

    if not args.quiet and not args.check and not args.diff:
        if needs_formatting:
            print("Formatted files")
        else:
            print("No changes needed")

    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="behave-format",
        description="The opinionated formatter for Behave .feature files.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Paths to .feature files or directories containing them.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: exit 1 if formatting is needed, don't write files.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Show diffs without writing files.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to pyproject.toml for configuration.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=None,
        help="Override indentation (number of spaces, >= 1).",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read from stdin, write formatted output to stdout.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output except errors.",
    )
    return parser


def _collect_files(paths: list[Path]) -> tuple[list[Path], bool]:
    """Expand paths into the list of .feature files to process."""
    files: list[Path] = []
    had_errors = False
    for path in paths:
        if path.is_dir():
            files.extend(f for f in sorted(path.rglob("*.feature")) if not _is_ignored(f, path))
        elif path.is_file() and path.suffix == ".feature":
            files.append(path)
        elif not path.exists():
            print(f"Error: {path}: file not found", file=sys.stderr)
            had_errors = True
        else:
            print(
                f"Warning: skipping {path} (not a .feature file or directory)",
                file=sys.stderr,
            )
    return files, had_errors


def _is_ignored(path: Path, root: Path) -> bool:
    """Skip files under hidden or tooling directories relative to ``root``."""
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    return any(part.startswith(".") or part in _IGNORED_DIRS for part in parts[:-1])


def _discover_pyproject(start: Path) -> Path | None:
    """Walk upward from ``start`` looking for the nearest pyproject.toml."""
    try:
        current = start.resolve()
    except OSError:
        current = start.absolute()
    for directory in (current, *current.parents):
        candidate = directory / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None


def _resolve_settings(
    start: Path,
    config_path: str | None,
    indent_override: int | None,
    cache: dict,
) -> Settings | None:
    """Load settings once per config source, with error reporting."""
    key = ("explicit", config_path) if config_path else ("discover", start)
    if key not in cache:
        try:
            if config_path:
                settings = Settings.from_pyproject(config_path)
            else:
                found = _discover_pyproject(start)
                settings = Settings.from_pyproject(str(found)) if found else Settings()
        except (OSError, ValueError) as e:
            source = config_path or "pyproject.toml"
            print(f"Error: invalid configuration in {source}: {e}", file=sys.stderr)
            settings = None
        cache[key] = settings
    settings = cache[key]
    if settings is not None and indent_override is not None:
        settings = settings.with_indent(indent_override)
    return settings


def _process_file(
    fpath: Path,
    settings: Settings,
    *,
    check: bool,
    diff: bool,
    quiet: bool,
) -> bool:
    # Read without newline translation so CRLF files compare unequal and
    # get normalized to LF on write.
    with fpath.open("r", encoding="utf-8", newline="") as fh:
        original = fh.read()

    feature = load_feature_text(original, filename=str(fpath))
    format_feature(feature, settings)
    formatted = print_feature(feature, indent=settings.indent, line_length=settings.line_length)
    formatted += "\n"

    if formatted == original:
        return False

    if check and not quiet:
        print(f"would reformat {fpath}")

    if diff:
        _show_diff(fpath, original, formatted, quiet=quiet)

    if not check and not diff:
        _write_atomic(fpath, formatted)
        if not quiet:
            print(f"reformatted {fpath}")

    return True


def _write_atomic(fpath: Path, content: str) -> None:
    fd, tmp_name = tempfile.mkstemp(dir=str(fpath.parent), prefix=fpath.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as tmp:
            tmp.write(content)
        os.replace(tmp_name, fpath)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def _process_stdin(settings: Settings, *, check: bool, diff: bool, quiet: bool) -> int:
    original = sys.stdin.read()
    try:
        feature = load_feature_text(original, filename="<stdin>")
    except Exception as e:
        print(f"Error: <stdin>: {e}", file=sys.stderr)
        return 2
    format_feature(feature, settings)
    formatted = print_feature(feature, indent=settings.indent, line_length=settings.line_length)
    formatted += "\n"

    if diff and formatted != original:
        _show_diff(Path("<stdin>"), original, formatted, quiet=quiet)

    if check:
        if formatted == original:
            return 0
        if not quiet:
            print("stdin would be reformatted", file=sys.stderr)
        return 1

    if diff:
        return 0

    sys.stdout.write(formatted)
    return 0


def _show_diff(fpath: Path, original: str, formatted: str, *, quiet: bool) -> None:
    diff_lines = difflib.unified_diff(
        original.splitlines(keepends=True),
        formatted.splitlines(keepends=True),
        fromfile=str(fpath),
        tofile=f"{fpath} (formatted)",
    )
    diff_text = "".join(diff_lines)
    if diff_text and not quiet:
        sys.stdout.write(diff_text)


if __name__ == "__main__":
    sys.exit(main())
