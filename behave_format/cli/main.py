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
import contextlib
import difflib
import os
import stat
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
    files = list(dict.fromkeys(files))

    needs_formatting = False
    for fpath in files:
        settings = _resolve_settings(fpath.parent, args.config, args.indent, settings_cache)
        if settings is None:
            return 2
        try:
            if _process_file(fpath, settings, check=args.check, diff=args.diff, quiet=args.quiet):
                needs_formatting = True
        except Exception as e:
            _print_error(f"Error: {fpath}: {e}")
            had_errors = True

    if had_errors:
        return 2

    if args.check and needs_formatting:
        if not args.quiet:
            _write_stdout("Files would be reformatted\n")
        return 1

    if not args.quiet and not args.check and not args.diff:
        if needs_formatting:
            _write_stdout("Formatted files\n")
        else:
            _write_stdout("No changes needed\n")

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
            try:
                candidates = sorted(path.rglob("*.feature"))
            except OSError as e:
                _print_error(f"Error: {path}: {e}")
                had_errors = True
                continue
            files.extend(f for f in candidates if not _is_ignored(f, path))
        elif path.is_file() and path.suffix.lower() == ".feature":
            files.append(path)
        elif not path.exists():
            _print_error(f"Error: {path}: file not found")
            had_errors = True
        else:
            _print_error(f"Warning: skipping {path} (not a .feature file or directory)")
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
        if config_path and not Path(config_path).is_file():
            _print_error(f"Error: config file not found: {config_path}")
            settings = None
        else:
            try:
                if config_path:
                    settings = Settings.from_pyproject(config_path)
                else:
                    found = _discover_pyproject(start)
                    settings = Settings.from_pyproject(str(found)) if found else Settings()
            except (OSError, ValueError) as e:
                source = config_path or "pyproject.toml"
                _print_error(f"Error: invalid configuration in {source}: {e}")
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
    # Resolve only real symlinks so os.replace writes the real file
    # instead of silently replacing the link itself. Unconditional
    # resolve would also rewrite 8.3 short names on Windows, making the
    # reported path differ from the one the user passed.
    if fpath.is_symlink():
        fpath = fpath.resolve()
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
        _write_stdout(f"would reformat {fpath}\n")

    if diff:
        _show_diff(fpath, original, formatted, quiet=quiet)

    if not check and not diff:
        _write_atomic(fpath, formatted)
        if not quiet:
            _write_stdout(f"reformatted {fpath}\n")

    return True


def _write_atomic(fpath: Path, content: str) -> None:
    fd, tmp_name = tempfile.mkstemp(dir=str(fpath.parent), prefix=fpath.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as tmp:
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
        # mkstemp creates the file 0600; keep the original permissions.
        with contextlib.suppress(OSError):
            os.chmod(tmp_name, stat.S_IMODE(fpath.stat().st_mode))
        os.replace(tmp_name, fpath)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def _read_stdin() -> str:
    """Read all of stdin as UTF-8, regardless of the console encoding."""
    buffer = getattr(sys.stdin, "buffer", None)
    if buffer is not None:
        return buffer.read().decode("utf-8")
    return sys.stdin.read()


def _write_stdout(text: str) -> None:
    """Write to stdout as UTF-8, regardless of the console encoding."""
    buffer = getattr(sys.stdout, "buffer", None)
    try:
        if buffer is not None:
            sys.stdout.flush()
            buffer.write(text.encode("utf-8"))
            buffer.flush()
        else:
            sys.stdout.write(text)
    except BrokenPipeError:
        # The downstream consumer is gone (e.g. ``| head``). Exit
        # without the interpreter's shutdown flush raising it again.
        os._exit(1)


def _print_error(message: str) -> None:
    """Write an error line to stderr as UTF-8 (survives unicode paths)."""
    buffer = getattr(sys.stderr, "buffer", None)
    if buffer is not None:
        buffer.write((message + "\n").encode("utf-8", errors="replace"))
        buffer.flush()
    else:
        print(message, file=sys.stderr)


def _process_stdin(settings: Settings, *, check: bool, diff: bool, quiet: bool) -> int:
    try:
        original = _read_stdin()
    except (OSError, UnicodeDecodeError) as e:
        _print_error(f"Error: <stdin>: {e}")
        return 2
    try:
        feature = load_feature_text(original, filename="<stdin>")
    except Exception as e:
        _print_error(f"Error: <stdin>: {e}")
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
            _print_error("stdin would be reformatted")
        return 1

    if diff:
        return 0

    _write_stdout(formatted)
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
        _write_stdout(diff_text)


if __name__ == "__main__":
    sys.exit(main())
