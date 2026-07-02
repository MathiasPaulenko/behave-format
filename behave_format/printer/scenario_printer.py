"""Scenario printer — formats scenarios and scenario outlines."""

from __future__ import annotations

from behave_model.model.background import Background
from behave_model.model.examples import Examples
from behave_model.model.scenario import Scenario
from behave_model.model.scenario_outline import ScenarioOutline

from behave_format.printer.step_printer import print_step
from behave_format.printer.table_printer import print_table
from behave_format.printer.tag_printer import print_tags


def print_background(background: Background, indent: int = 2) -> str:
    """Format a Background block.

    Args:
        background: The Background to print.
        indent: Base indentation level.

    Returns:
        Multi-line string with the background and its steps.
    """
    prefix = " " * indent
    header = "Background:"
    if background.name:
        header = f"Background: {background.name}"
    lines: list[str] = [f"{prefix}{header}"]
    for step in background.steps:
        lines.append(print_step(step, indent=indent + 2))
    return "\n".join(lines)


def print_scenario(scenario: Scenario, indent: int = 2) -> str:
    """Format a Scenario as Gherkin text.

    Args:
        scenario: The Scenario to print.
        indent: Base indentation level.

    Returns:
        Multi-line string with tags, scenario header, and steps.
    """
    prefix = " " * indent
    lines: list[str] = []

    for comment in scenario.comments:
        lines.append(f"{prefix}{comment.text}")

    if scenario.tags:
        lines.append(print_tags(scenario.tags, indent=indent))

    header = f"Scenario: {scenario.name}" if scenario.name else "Scenario:"
    lines.append(f"{prefix}{header}")

    if scenario.description:
        for desc_line in scenario.description.splitlines():
            if desc_line:
                lines.append(f"{prefix}  {desc_line}")
            else:
                lines.append("")

    for step in scenario.steps:
        lines.append(print_step(step, indent=indent + 2))

    return "\n".join(lines)


def print_scenario_outline(outline: ScenarioOutline, indent: int = 2) -> str:
    """Format a ScenarioOutline as Gherkin text.

    Args:
        outline: The ScenarioOutline to print.
        indent: Base indentation level.

    Returns:
        Multi-line string with tags, outline header, steps, and examples.
    """
    prefix = " " * indent
    lines: list[str] = []

    for comment in outline.comments:
        lines.append(f"{prefix}{comment.text}")

    if outline.tags:
        lines.append(print_tags(outline.tags, indent=indent))

    header = f"Scenario Outline: {outline.name}" if outline.name else "Scenario Outline:"
    lines.append(f"{prefix}{header}")

    if outline.description:
        for desc_line in outline.description.splitlines():
            if desc_line:
                lines.append(f"{prefix}  {desc_line}")
            else:
                lines.append("")

    for step in outline.steps:
        lines.append(print_step(step, indent=indent + 2))

    for examples in outline.examples:
        lines.append("")
        lines.append(_print_examples(examples, indent=indent + 2))

    return "\n".join(lines)


def _print_examples(examples: Examples, indent: int = 4) -> str:
    prefix = " " * indent
    lines: list[str] = []

    if examples.tags:
        lines.append(print_tags(examples.tags, indent=indent))

    header = "Examples:"
    if examples.name:
        header = f"Examples: {examples.name}"
    lines.append(f"{prefix}{header}")

    lines.append(print_table(examples.table, indent=indent + 2))

    return "\n".join(lines)
