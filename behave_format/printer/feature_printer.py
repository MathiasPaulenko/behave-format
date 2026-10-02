"""Feature printer — formats a complete Feature as .feature text."""

from __future__ import annotations

from behave_model.model.feature import Feature
from behave_model.model.rule import Rule
from behave_model.model.scenario_outline import ScenarioOutline

from behave_format.printer.keywords import gherkin_keyword, is_known_language
from behave_format.printer.scenario_printer import (
    print_background,
    print_scenario,
    print_scenario_outline,
)
from behave_format.printer.tag_printer import print_tags


def print_feature(
    feature: Feature,
    indent: int = 2,
    *,
    line_length: int | None = None,
) -> str:
    """Format a Feature as valid, deterministic Gherkin text.

    Args:
        feature: The Feature to print.
        indent: Base indentation for scenarios and rules.
        line_length: Optional maximum line length for tag wrapping.

    Returns:
        Multi-line string representing the complete feature file content.
    """
    language = feature.language or "en"
    lines: list[str] = []

    # Emit the directive only for languages behave can actually re-parse;
    # an unknown code would produce output that fails to round-trip.
    if language != "en" and is_known_language(language):
        lines.append(f"# language: {language}")

    for comment in feature.comments:
        lines.append(comment.text)

    if feature.tags:
        lines.append(print_tags(feature.tags, indent=0, line_length=line_length))

    keyword = gherkin_keyword(feature, "feature", language)
    header = f"{keyword}: {feature.name}" if feature.name else f"{keyword}:"
    lines.append(header)

    if feature.description:
        for desc_line in feature.description.splitlines():
            lines.append(f"{' ' * indent}{desc_line}" if desc_line else "")

    if feature.background:
        lines.append("")
        lines.append(print_background(feature.background, indent=indent, language=language))

    for scenario in feature.scenarios:
        lines.append("")
        lines.append(
            _print_scenario_like(
                scenario, indent=indent, language=language, line_length=line_length
            )
        )

    for rule in feature.rules:
        lines.append("")
        lines.append(_print_rule(rule, indent=indent, language=language, line_length=line_length))

    return "\n".join(lines)


def _print_scenario_like(scenario, indent: int, *, language: str, line_length) -> str:
    if isinstance(scenario, ScenarioOutline):
        return print_scenario_outline(
            scenario, indent=indent, language=language, line_length=line_length
        )
    return print_scenario(scenario, indent=indent, language=language, line_length=line_length)


def _print_rule(rule: Rule, indent: int = 2, *, language: str = "en", line_length=None) -> str:
    prefix = " " * indent
    lines: list[str] = []

    for comment in rule.comments:
        lines.append(f"{prefix}{comment.text}")

    if rule.tags:
        lines.append(print_tags(rule.tags, indent=indent, line_length=line_length))

    keyword = gherkin_keyword(rule, "rule", language)
    header = f"{keyword}: {rule.name}" if rule.name else f"{keyword}:"
    lines.append(f"{prefix}{header}")

    if rule.description:
        for desc_line in rule.description.splitlines():
            lines.append(f"{prefix}  {desc_line}" if desc_line else "")

    children: list[str] = []
    if rule.background:
        children.append(print_background(rule.background, indent=indent + 2, language=language))
    for scenario in rule.scenarios:
        children.append(
            _print_scenario_like(
                scenario, indent=indent + 2, language=language, line_length=line_length
            )
        )
    if children:
        lines.append("\n\n".join(children))

    return "\n".join(lines)
