"""Tag printer — formats tags as space-separated strings."""

from __future__ import annotations

from behave_model.model.tag import Tag


def print_tags(tags: list[Tag], indent: int = 0) -> str:
    """Format a list of tags as a single line.

    Args:
        tags: List of Tag objects.
        indent: Number of spaces to prefix.

    Returns:
        A space-separated tag string, or empty string if no tags.
    """
    if not tags:
        return ""
    prefix = " " * indent
    return prefix + " ".join(t.name for t in tags)
