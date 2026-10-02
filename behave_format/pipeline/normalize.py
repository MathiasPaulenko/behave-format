"""Normalize stage — clean whitespace and standardize structure.

This stage operates on a behave-model Project in place.
It NEVER changes semantics: only whitespace, indentation, and
structural consistency are normalized.
"""

from __future__ import annotations

import re

from behave_model.model.background import Background
from behave_model.model.docstring import DocString
from behave_model.model.examples import Examples
from behave_model.model.feature import Feature
from behave_model.model.project import Project
from behave_model.model.rule import Rule
from behave_model.model.scenario import Scenario
from behave_model.model.scenario_outline import ScenarioOutline
from behave_model.model.step import Step
from behave_model.model.table import Table
from behave_model.model.tag import Tag


def normalize_project(project: Project) -> Project:
    """Normalize whitespace and structure across the entire project.

    Args:
        project: The project to normalize (mutated in place).

    Returns:
        The same project, normalized.
    """
    for feature in project.features:
        _normalize_feature(feature)
    return project


def _normalize_feature(feature: Feature) -> None:
    feature.name = " ".join(feature.name.split())
    feature.description = _normalize_description(feature.description)
    _normalize_tags(feature.tags)
    if feature.background:
        _normalize_background(feature.background)
    for scenario in feature.scenarios:
        _normalize_scenario(scenario)
    for rule in feature.rules:
        _normalize_rule(rule)
    for comment in feature.comments:
        comment.text = comment.text.rstrip()


def _normalize_rule(rule: Rule) -> None:
    rule.name = " ".join(rule.name.split())
    rule.description = _normalize_description(rule.description)
    _normalize_tags(rule.tags)
    if rule.background:
        _normalize_background(rule.background)
    for scenario in rule.scenarios:
        _normalize_scenario(scenario)
    for comment in rule.comments:
        comment.text = comment.text.rstrip()


def _normalize_background(background: Background) -> None:
    background.name = " ".join(background.name.split())
    for step in background.steps:
        _normalize_step(step)


def _normalize_scenario(scenario: Scenario | ScenarioOutline) -> None:
    scenario.name = " ".join(scenario.name.split())
    scenario.description = _normalize_description(scenario.description)
    _normalize_tags(scenario.tags)
    for step in scenario.steps:
        _normalize_step(step)
    if isinstance(scenario, ScenarioOutline):
        for examples in scenario.examples:
            _normalize_examples(examples)
    for comment in scenario.comments:
        comment.text = comment.text.rstrip()


def _normalize_examples(examples: Examples) -> None:
    examples.name = " ".join(examples.name.split())
    _normalize_tags(examples.tags)
    _normalize_table(examples.table)


_STEP_LITERAL_RE = re.compile(r'("[^"\n]*"|\'[^\'\n]*\'|<[^>\n]*>)')


def _collapse_unprotected(text: str) -> str:
    words = text.split()
    if not words:
        return " " if text else ""
    head = " " if text[0].isspace() else ""
    tail = " " if text[-1].isspace() else ""
    return head + " ".join(words) + tail


def _collapse_whitespace(name: str) -> str:
    """Collapse whitespace runs except inside quoted strings and <placeholders>.

    Step parameters carry semantic value (a step regex may capture them),
    so whitespace inside ``"..."``, ``'...'`` and ``<...>`` is preserved.
    """
    parts = _STEP_LITERAL_RE.split(name)
    collapsed = [part if i % 2 else _collapse_unprotected(part) for i, part in enumerate(parts)]
    return "".join(collapsed)


def _normalize_step(step: Step) -> None:
    step.keyword = step.keyword.strip()
    step.name = _collapse_whitespace(step.name)
    if step.doc_string:
        _normalize_doc_string(step.doc_string)
    if step.data_table:
        _normalize_table(step.data_table)
    for comment in step.comments:
        comment.text = comment.text.rstrip()


def _normalize_doc_string(doc_string: DocString) -> None:
    doc_string.content_type = doc_string.content_type.strip()
    delimiter = doc_string.delimiter or '"""'
    doc_string.delimiter = delimiter


def _normalize_table(table: Table) -> None:
    table.headers = [h.strip() for h in table.headers]
    for row in table.rows:
        row.cells = [c.strip() for c in row.cells]


def _normalize_tags(tags: list[Tag]) -> None:
    seen: set[str] = set()
    kept: list[Tag] = []
    for tag in tags:
        tag.name = tag.name.strip()
        if not tag.name.startswith("@"):
            tag.name = "@" + tag.name
        if tag.name not in seen:
            seen.add(tag.name)
            kept.append(tag)
    tags[:] = kept


def _normalize_description(description: str) -> str:
    # Descriptions are free text: strip edges but keep interior spacing,
    # which may be intentional (aligned columns, ASCII diagrams).
    return "\n".join(line.strip() for line in description.splitlines())
