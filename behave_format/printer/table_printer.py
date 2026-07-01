"""Table printer — formats data tables with aligned columns."""

from __future__ import annotations

from behave_model.model.table import Table


def print_table(table: Table, indent: int = 4) -> str:
    """Format a Table as aligned Gherkin table text.

    Args:
        table: The Table to print.
        indent: Number of spaces for indentation.

    Returns:
        Multi-line string with aligned table rows.
    """
    if not table.headers and not table.rows:
        return ""

    widths = _compute_widths(table)
    prefix = " " * indent
    lines: list[str] = []

    header_cells = [
        h.ljust(widths[i]) if i < len(widths) else h for i, h in enumerate(table.headers)
    ]
    lines.append(f"{prefix}| {' | '.join(header_cells)} |")

    for row in table.rows:
        row_cells = [
            cell.ljust(widths[i]) if i < len(widths) else cell for i, cell in enumerate(row.cells)
        ]
        lines.append(f"{prefix}| {' | '.join(row_cells)} |")

    return "\n".join(lines)


def _compute_widths(table: Table) -> list[int]:
    widths = [len(h) for h in table.headers]
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
            else:
                widths.append(len(cell))
    return widths
