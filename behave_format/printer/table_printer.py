"""Table printer — formats data tables with aligned columns."""

from __future__ import annotations

from unicodedata import east_asian_width

from behave_model.model.table import Table


def print_table(table: Table, indent: int = 4) -> str:
    """Format a Table as aligned Gherkin table text.

    Cell values are re-escaped for Gherkin (``|`` -> ``\\|``) and column
    widths are computed on the escaped, display-width of each cell so
    wide characters (CJK) stay aligned.

    Args:
        table: The Table to print.
        indent: Number of spaces for indentation.

    Returns:
        Multi-line string with aligned table rows.
    """
    if not table.headers and not table.rows:
        return ""

    rows = [[_escape_cell(c) for c in row.cells] for row in table.rows]
    headers = [_escape_cell(h) for h in table.headers]
    widths = _compute_widths(headers, rows)
    prefix = " " * indent
    lines: list[str] = []

    lines.append(_format_row(prefix, headers, widths))
    for row in rows:
        lines.append(_format_row(prefix, row, widths))

    return "\n".join(lines)


def _escape_cell(cell: str) -> str:
    return cell.replace("|", "\\|")


def _display_width(text: str) -> int:
    return sum(2 if east_asian_width(char) in ("W", "F") else 1 for char in text)


def _format_row(prefix: str, cells: list[str], widths: list[int]) -> str:
    padded = []
    for i, width in enumerate(widths):
        cell = cells[i] if i < len(cells) else ""
        padded.append(cell + " " * (width - _display_width(cell)))
    return f"{prefix}| {' | '.join(padded)} |"


def _compute_widths(headers: list[str], rows: list[list[str]]) -> list[int]:
    widths = [_display_width(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            width = _display_width(cell)
            if i < len(widths):
                widths[i] = max(widths[i], width)
            else:
                widths.append(width)
    return widths
