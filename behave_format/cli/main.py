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
import sys
from pathlib import Path

from behave_model import load_feature

from behave_format import __version__
from behave_format.config.settings import Settings
from behave_format.pipeline.formatter import format_feature
from behave_format.printer.feature_printer import print_feature


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv).

    Returns:
        Exit code: 0 on success, 1 if formatting is needed (--check).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    settings = _load_settings(args.config, args.indent)

    if args.stdin:
        return _process_stdin(settings, check=args.check, quiet=args.quiet)

    paths = [Path(p) for p in args.paths]
    if not paths:
        parser.print_help()
        return 0

    needs_formatting = False
    had_errors = False

    for path in paths:
        if path.is_dir():
            changed = _process_directory(
                path, settings, check=args.check, diff=args.diff, quiet=args.quiet
            )
            if changed:
                needs_formatting = True
        elif path.is_file() and path.suffix == ".feature":
            try:
                changed = _process_file(
                    path, settings, check=args.check, diff=args.diff, quiet=args.quiet
                )
                if changed:
                    needs_formatting = True
            except Exception as e:
                print(f"Error: {path}: {e}", file=sys.stderr)
                had_errors = True
        elif not path.exists():
            print(f"Error: {path}: file not found", file=sys.stderr)
            had_errors = True
        else:
            print(f"Warning: skipping {path} (not a .feature file or directory)", file=sys.stderr)

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
        help="Override indentation (number of spaces).",
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


def _load_settings(config_path: str | None, indent_override: int | None = None) -> Settings:
    if config_path:
        settings = Settings.from_pyproject(config_path)
    else:
        settings = Settings.from_pyproject("pyproject.toml")
    if indent_override is not None:
        settings = settings.with_indent(indent_override)
    return settings


def _process_directory(
    directory: Path,
    settings: Settings,
    *,
    check: bool,
    diff: bool,
    quiet: bool,
) -> bool:
    feature_files = sorted(directory.rglob("*.feature"))
    changed = False
    for fpath in feature_files:
        try:
            if _process_file(fpath, settings, check=check, diff=diff, quiet=quiet):
                changed = True
        except Exception as e:
            print(f"Error: {fpath}: {e}", file=sys.stderr)
    return changed


def _process_file(
    fpath: Path,
    settings: Settings,
    *,
    check: bool,
    diff: bool,
    quiet: bool,
) -> bool:
    original = fpath.read_text(encoding="utf-8")

    feature = load_feature(fpath)
    format_feature(feature, settings)
    formatted = print_feature(feature, indent=settings.indent) + "\n"

    if formatted == original:
        return False

    if diff:
        _show_diff(fpath, original, formatted, quiet=quiet)

    if not check and not diff:
        fpath.write_text(formatted, encoding="utf-8")
        if not quiet:
            print(f"reformatted {fpath}")

    return True


def _process_stdin(settings: Settings, *, check: bool, quiet: bool) -> int:
    original = sys.stdin.read()
    formatted = _format_feature_from_text(original, settings)

    if check:
        if formatted == original:
            return 0
        if not quiet:
            print("stdin would be reformatted", file=sys.stderr)
        return 1

    sys.stdout.write(formatted)
    return 0


def _show_diff(fpath: Path, original: str, formatted: str, *, quiet: bool) -> None:
    diff_lines = difflib.unified_diff(
        original.splitlines(keepends=True),
        formatted.splitlines(keepends=True),
        fromfile=str(fpath),
        tofile=str(fpath),
    )
    diff_text = "".join(diff_lines)
    if diff_text and not quiet:
        sys.stdout.write(diff_text)


def _format_feature_from_text(text: str, settings: Settings) -> str:
    """Format a feature from raw text and return the formatted output."""
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".feature", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(text)
        tmp_path = Path(tmp.name)

    try:
        feature = load_feature(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    format_feature(feature, settings)
    return print_feature(feature, indent=settings.indent) + "\n"


if __name__ == "__main__":
    sys.exit(main())
