"""Feature printer — formats a complete Feature as .feature text."""

from __future__ import annotations

from behave_model.model.feature import Feature
from behave_model.model.rule import Rule
from behave_model.model.scenario_outline import ScenarioOutline

from behave_format.printer.scenario_printer import (
    print_background,
    print_scenario,
    print_scenario_outline,
)
from behave_format.printer.tag_printer import print_tags


def print_feature(feature: Feature, indent: int = 2) -> str:
    """Format a Feature as valid, deterministic Gherkin text.

    Args:
        feature: The Feature to print.
        indent: Base indentation for scenarios and rules.

    Returns:
        Multi-line string representing the complete feature file content.
    """
    lines: list[str] = []

    if feature.tags:
        lines.append(print_tags(feature.tags, indent=0))

    header = f"Feature: {feature.name}" if feature.name else "Feature:"
    lines.append(header)

    if feature.description:
        for desc_line in feature.description.splitlines():
            if desc_line:
                lines.append(f"{' ' * indent}{desc_line}")
            else:
                lines.append("")

    if feature.background:
        lines.append("")
        lines.append(print_background(feature.background, indent=indent))

    for scenario in feature.scenarios:
        lines.append("")
        if isinstance(scenario, ScenarioOutline):
            lines.append(print_scenario_outline(scenario, indent=indent))
        else:
            lines.append(print_scenario(scenario, indent=indent))

    for rule in feature.rules:
        lines.append("")
        lines.append(_print_rule(rule, indent=indent))

    return "\n".join(lines)


def _print_rule(rule: Rule, indent: int = 2) -> str:
    prefix = " " * indent
    lines: list[str] = []

    if rule.tags:
        lines.append(print_tags(rule.tags, indent=indent))

    header = f"Rule: {rule.name}" if rule.name else "Rule:"
    lines.append(f"{prefix}{header}")

    if rule.description:
        for desc_line in rule.description.splitlines():
            if desc_line:
                lines.append(f"{prefix}  {desc_line}")
            else:
                lines.append("")

    first_child = True
    if rule.background:
        if not first_child:
            lines.append("")
        lines.append(print_background(rule.background, indent=indent + 2))
        first_child = False

    for scenario in rule.scenarios:
        if not first_child:
            lines.append("")
        if isinstance(scenario, ScenarioOutline):
            lines.append(print_scenario_outline(scenario, indent=indent + 2))
        else:
            lines.append(print_scenario(scenario, indent=indent + 2))
        first_child = False

    return "\n".join(lines)
