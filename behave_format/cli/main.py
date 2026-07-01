"""CLI entry point for behave-format.

Usage:
    behave-format [OPTIONS] PATH...

Options:
    --check          Check mode: exit 1 if formatting is needed, don't write.
    --diff           Show diffs without writing files.
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

    settings = _load_settings(args.config)

    paths = [Path(p) for p in args.paths]
    if not paths:
        parser.print_help()
        return 0

    needs_formatting = False

    for path in paths:
        if path.is_dir():
            changed = _process_directory(
                path, settings, check=args.check, diff=args.diff, quiet=args.quiet
            )
            if changed:
                needs_formatting = True
        elif path.is_file() and path.suffix == ".feature":
            changed = _process_file(
                path, settings, check=args.check, diff=args.diff, quiet=args.quiet
            )
            if changed:
                needs_formatting = True
        else:
            print(f"Warning: skipping {path} (not a .feature file or directory)", file=sys.stderr)

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
        "--quiet",
        action="store_true",
        help="Suppress output except errors.",
    )
    return parser


def _load_settings(config_path: str | None) -> Settings:
    if config_path:
        return Settings.from_pyproject(config_path)
    return Settings.from_pyproject("pyproject.toml")


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
        if _process_file(fpath, settings, check=check, diff=diff, quiet=quiet):
            changed = True
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


if __name__ == "__main__":
    sys.exit(main())
