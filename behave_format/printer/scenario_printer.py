"""Scenario printer — formats scenarios and scenario outlines."""

from __future__ import annotations

from behave_model.model.background import Background
from behave_model.model.examples import Examples
from behave_model.model.scenario import Scenario
from behave_model.model.scenario_outline import ScenarioOutline

from behave_format.printer.keywords import gherkin_keyword
from behave_format.printer.step_printer import print_step
from behave_format.printer.table_printer import print_table
from behave_format.printer.tag_printer import print_tags


def print_background(
    background: Background,
    indent: int = 2,
    *,
    language: str = "en",
) -> str:
    """Format a Background block.

    Args:
        background: The Background to print.
        indent: Base indentation level.
        language: Feature language for keyword resolution.

    Returns:
        Multi-line string with the background and its steps.
    """
    prefix = " " * indent
    keyword = gherkin_keyword(background, "background", language)
    header = f"{keyword}:"
    if background.name:
        header = f"{keyword}: {background.name}"
    lines: list[str] = [f"{prefix}{header}"]
    for step in background.steps:
        lines.append(print_step(step, indent=indent + 2))
    return "\n".join(lines)


def print_scenario(
    scenario: Scenario,
    indent: int = 2,
    *,
    language: str = "en",
    line_length: int | None = None,
) -> str:
    """Format a Scenario as Gherkin text.

    Args:
        scenario: The Scenario to print.
        indent: Base indentation level.
        language: Feature language for keyword resolution.
        line_length: Optional maximum line length for tag wrapping.

    Returns:
        Multi-line string with tags, scenario header, and steps.
    """
    prefix = " " * indent
    lines: list[str] = []

    for comment in scenario.comments:
        lines.append(f"{prefix}{comment.text}")

    if scenario.tags:
        lines.append(print_tags(scenario.tags, indent=indent, line_length=line_length))

    keyword = gherkin_keyword(scenario, "scenario", language)
    header = f"{keyword}: {scenario.name}" if scenario.name else f"{keyword}:"
    lines.append(f"{prefix}{header}")

    _append_description(lines, scenario.description, indent + 2)

    for step in scenario.steps:
        lines.append(print_step(step, indent=indent + 2))

    return "\n".join(lines)


def print_scenario_outline(
    outline: ScenarioOutline,
    indent: int = 2,
    *,
    language: str = "en",
    line_length: int | None = None,
) -> str:
    """Format a ScenarioOutline as Gherkin text.

    Args:
        outline: The ScenarioOutline to print.
        indent: Base indentation level.
        language: Feature language for keyword resolution.
        line_length: Optional maximum line length for tag wrapping.

    Returns:
        Multi-line string with tags, outline header, steps, and examples.
    """
    prefix = " " * indent
    lines: list[str] = []

    for comment in outline.comments:
        lines.append(f"{prefix}{comment.text}")

    if outline.tags:
        lines.append(print_tags(outline.tags, indent=indent, line_length=line_length))

    keyword = gherkin_keyword(outline, "scenario_outline", language)
    header = f"{keyword}: {outline.name}" if outline.name else f"{keyword}:"
    lines.append(f"{prefix}{header}")

    _append_description(lines, outline.description, indent + 2)

    for step in outline.steps:
        lines.append(print_step(step, indent=indent + 2))

    for examples in outline.examples:
        lines.append("")
        lines.append(
            _print_examples(examples, indent=indent + 2, language=language, line_length=line_length)
        )

    return "\n".join(lines)


def _append_description(lines: list[str], description: str, indent: int) -> None:
    prefix = " " * indent
    for desc_line in description.splitlines():
        lines.append(f"{prefix}{desc_line}" if desc_line else "")


def _print_examples(
    examples: Examples,
    indent: int = 4,
    *,
    language: str = "en",
    line_length: int | None = None,
) -> str:
    prefix = " " * indent
    lines: list[str] = []

    if examples.tags:
        lines.append(print_tags(examples.tags, indent=indent, line_length=line_length))

    keyword = gherkin_keyword(examples, "examples", language)
    header = f"{keyword}:"
    if examples.name:
        header = f"{keyword}: {examples.name}"
    lines.append(f"{prefix}{header}")

    table_text = print_table(examples.table, indent=indent + 2)
    if table_text:
        lines.append(table_text)

    return "\n".join(lines)
