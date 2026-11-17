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
    feature.name = _collapse_name(feature.name)
    feature.description = _normalize_description(feature.description)
    _normalize_tags(feature.tags)
    # Model objects are falsy when empty (``__len__``); compare with None.
    if feature.background is not None:
        _normalize_background(feature.background)
    for scenario in feature.scenarios:
        _normalize_scenario(scenario)
    for rule in feature.rules:
        _normalize_rule(rule)
    for comment in feature.comments:
        comment.text = comment.text.rstrip()
    _rstrip_comments(feature, "_trailing_comments")


def _normalize_rule(rule: Rule) -> None:
    rule.name = _collapse_name(rule.name)
    rule.description = _normalize_description(rule.description)
    _normalize_tags(rule.tags)
    if rule.background is not None:
        _normalize_background(rule.background)
    for scenario in rule.scenarios:
        _normalize_scenario(scenario)
    for comment in rule.comments:
        comment.text = comment.text.rstrip()


def _normalize_background(background: Background) -> None:
    background.name = _collapse_name(background.name)
    description = getattr(background, "_description", None)
    if description is not None:
        background._description = _normalize_description(description)
    for step in background.steps:
        _normalize_step(step)
    _rstrip_comments(background, "comments")


def _normalize_scenario(scenario: Scenario | ScenarioOutline) -> None:
    scenario.name = _collapse_name(scenario.name)
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
    examples.name = _collapse_name(examples.name)
    _normalize_tags(examples.tags)
    _normalize_table(examples.table)
    _rstrip_comments(examples, "comments")
    _rstrip_comments(examples, "_trailing_comments")


def _rstrip_comments(element, attr: str) -> None:
    for comment in getattr(element, attr, ()):
        comment.text = comment.text.rstrip()


# Whitespace runs that collapse to a single space. Space-like Unicode
# characters (NBSP, ideographic space, ...) are excluded: inside step
# names they are semantic (a step regex may match them literally), so
# they must survive normalization.
_COLLAPSIBLE_WS_RE = re.compile(r"[^\S\xa0\u1680\u2000-\u200a\u202f\u205f\u3000]+")

# Quoted strings and <placeholders> inside step names keep their interior
# whitespace. A backslash escape prevents the quote from ending the literal.
_STEP_LITERAL_RE = re.compile(r'("(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|<[^>\n]*>)')


def _collapse_name(name: str) -> str:
    """Collapse whitespace runs in an element name to single spaces."""
    return _COLLAPSIBLE_WS_RE.sub(" ", name).strip(" ")


def _collapse_unprotected(text: str) -> str:
    words = [word for word in _COLLAPSIBLE_WS_RE.split(text) if word]
    if not words:
        return " " if text else ""
    head = " " if _COLLAPSIBLE_WS_RE.match(text) else ""
    tail = " " if _COLLAPSIBLE_WS_RE.match(text[-1]) else ""
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
    if step.doc_string is not None:
        _normalize_doc_string(step.doc_string)
    if step.data_table is not None:
        _normalize_table(step.data_table)
    for comment in step.comments:
        comment.text = comment.text.rstrip()
    _rstrip_comments(step, "_trailing_comments")


def _normalize_doc_string(doc_string: DocString) -> None:
    doc_string.content_type = doc_string.content_type.strip()
    # Trailing whitespace inside docstring content is invisible and
    # would violate the formatter's no-trailing-whitespace invariant.
    doc_string.content = "\n".join(line.rstrip() for line in doc_string.content.splitlines())
    delimiter = doc_string.delimiter or '"""'
    # A content line starting with the delimiter would close the docstring
    # early on re-parse; switch to the other delimiter to stay lossless.
    if any(line.strip().startswith(delimiter) for line in doc_string.content.splitlines()):
        delimiter = "'''" if delimiter == '"""' else '"""'
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
