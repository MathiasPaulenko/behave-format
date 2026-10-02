"""Tag printer — formats tags as space-separated strings."""

from __future__ import annotations

from behave_model.model.tag import Tag


def print_tags(tags: list[Tag], indent: int = 0, line_length: int | None = None) -> str:
    """Format a list of tags as one or more space-separated lines.

    Args:
        tags: List of Tag objects.
        indent: Number of spaces to prefix.
        line_length: Optional maximum line length. When exceeded, tags
            wrap onto continuation lines at the same indent.

    Returns:
        A space-separated tag string, or empty string if no tags.
    """
    if not tags:
        return ""
    prefix = " " * indent
    names = [t.name for t in tags]
    if line_length is None or line_length <= 0:
        return prefix + " ".join(names)

    lines: list[str] = []
    current: list[str] = []
    current_len = indent
    for name in names:
        extra = len(name) + (1 if current else 0)
        if current and current_len + extra > line_length:
            lines.append(prefix + " ".join(current))
            current = [name]
            current_len = indent + len(name)
        else:
            current.append(name)
            current_len += extra
    if current:
        lines.append(prefix + " ".join(current))
    return "\n".join(lines)
