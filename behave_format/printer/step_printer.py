"""Step printer — formats steps with proper indentation."""

from __future__ import annotations

from behave_model.model.docstring import DocString
from behave_model.model.step import Step

from behave_format.printer.table_printer import print_table


def print_step(step: Step, indent: int = 4) -> str:
    """Format a single step as Gherkin text.

    Args:
        step: The Step to print.
        indent: Number of spaces for indentation.

    Returns:
        Multi-line string with the step and any attached docstring or table.
    """
    prefix = " " * indent
    lines: list[str] = []

    for comment in step.comments:
        lines.append(f"{prefix}{comment.text}")

    lines.append(f"{prefix}{step.keyword} {step.name}".rstrip())

    if step.doc_string:
        lines.append(_print_doc_string(step.doc_string, indent))

    if step.data_table:
        lines.append(print_table(step.data_table, indent=indent + 2))

    return "\n".join(lines)


def _print_doc_string(doc_string: DocString, indent: int) -> str:
    prefix = " " * (indent + 2)
    delimiter = doc_string.delimiter or '"""'
    content_type = doc_string.content_type

    lines: list[str] = []
    header = f"{prefix}{delimiter}"
    if content_type:
        header += content_type
    lines.append(header)
    for content_line in doc_string.lines:
        lines.append(f"{prefix}{content_line}")
    lines.append(f"{prefix}{delimiter}")
    return "\n".join(lines)
