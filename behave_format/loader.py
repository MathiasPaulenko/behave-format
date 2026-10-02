"""Feature loading with comment and keyword restoration.

``behave.parser`` discards comments, docstring content types, and the
original Gherkin keywords during parsing. This module bridges the gap:
it parses feature text via behave-model and then restores the lost
information onto the domain model so the formatter can emit it again.

Restored attributes:

- ``comments``: ``Comment`` objects attached to features, rules,
  scenarios, scenario outlines and steps, positioned before the element
  that follows them in the source file.
- ``_gherkin_keyword``: the original keyword as written (e.g.
  ``"Escenario"``, ``"Scenario Template"``). Printers use it when present
  and fall back to a language-canonical keyword otherwise.
- ``doc_string.content_type``: extracted from the opening delimiter line
  in the source (behave does not store it on its model).
"""

from __future__ import annotations

import bisect
import re
from pathlib import Path

from behave_model.model.comment import Comment
from behave_model.model.feature import Feature
from behave_model.model.location import Location
from behave_model.model.scenario_outline import ScenarioOutline
from behave_model.model.step import Step
from behave_model.parser.adapter import BehaveParserAdapter
from behave_model.parser.parser import parse_feature

_LANGUAGE_DIRECTIVE_RE = re.compile(r"^\s*#\s*language\s*:", re.IGNORECASE)
_DOCSTRING_OPEN_RE = re.compile(r'^\s*"""(.*)$')


def load_feature_text(text: str, *, filename: str = "") -> Feature:
    """Parse feature text into a model Feature with comments restored.

    Args:
        text: Raw ``.feature`` file content.
        filename: Optional source name used for locations and errors.

    Returns:
        A domain Feature with comments, original keywords and docstring
        content types restored from the source text.

    Raises:
        ParseError: If the text cannot be parsed.
    """
    behave_feature = parse_feature(text, filename=filename or None)
    feature = BehaveParserAdapter().adapt_feature(behave_feature, filename=filename)
    _restore_keywords(feature, behave_feature)
    _restore_comments_and_docstrings(feature, text)
    return feature


def load_feature_file(path: str | Path) -> Feature:
    """Load a ``.feature`` file with comments restored.

    Args:
        path: Path to the feature file.

    Returns:
        A domain Feature with source information restored.
    """
    path = Path(path)
    return load_feature_text(path.read_text(encoding="utf-8"), filename=str(path))


# -- keyword restoration -------------------------------------------------------


def _set_keyword(model_el, behave_el) -> None:
    keyword = getattr(behave_el, "keyword", "") or ""
    if keyword:
        model_el._gherkin_keyword = keyword


def _restore_scenario(scenario, behave_scenario) -> None:
    _set_keyword(scenario, behave_scenario)
    if isinstance(scenario, ScenarioOutline):
        for ex, behave_ex in zip(scenario.examples, behave_scenario.examples, strict=False):
            _set_keyword(ex, behave_ex)


def _restore_container(model_container, behave_container) -> None:
    """Restore keywords for a feature or rule body."""
    if model_container.background and getattr(behave_container, "background", None):
        _set_keyword(model_container.background, behave_container.background)
    for scenario, behave_scenario in zip(
        model_container.scenarios, behave_container.scenarios, strict=False
    ):
        _restore_scenario(scenario, behave_scenario)


def _restore_keywords(feature: Feature, behave_feature) -> None:
    _set_keyword(feature, behave_feature)
    _restore_container(feature, behave_feature)
    for rule, behave_rule in zip(feature.rules, getattr(behave_feature, "rules", []), strict=False):
        _set_keyword(rule, behave_rule)
        _restore_container(rule, behave_rule)


# -- comment / docstring restoration -------------------------------------------


def _iter_attachables(feature: Feature):
    """Yield every element that owns a ``comments`` list, in model order."""
    yield feature
    if feature.background:
        yield from feature.background.steps
    for scenario in feature.scenarios:
        yield from _iter_scenario_attachables(scenario)
    for rule in feature.rules:
        yield rule
        if rule.background:
            yield from rule.background.steps
        for scenario in rule.scenarios:
            yield from _iter_scenario_attachables(scenario)


def _iter_scenario_attachables(scenario):
    yield scenario
    yield from scenario.steps


def _iter_steps(feature: Feature):
    """Yield every step in model order."""
    for el in _iter_attachables(feature):
        if isinstance(el, Step):
            yield el


def _restore_comments_and_docstrings(feature: Feature, text: str) -> None:
    attachables = sorted(
        ((getattr(el.location, "line", 0) or 0, el) for el in _iter_attachables(feature)),
        key=lambda item: item[0],
    )
    if not attachables:
        return
    lines = [item[0] for item in attachables]
    feature_line = getattr(feature.location, "line", 0) or 0
    # Comments after the last element have no "next" attachable — attach
    # them to the last element so they stay near the end of the file.
    trailing_target = attachables[-1][1]

    docstring_openers: list[tuple[int, str]] = []
    in_docstring = False
    for lineno, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if in_docstring:
            if stripped == '"""':
                in_docstring = False
            continue
        opener = _DOCSTRING_OPEN_RE.match(raw)
        if opener:
            in_docstring = True
            docstring_openers.append((lineno, opener.group(1).strip()))
            continue
        if not stripped.startswith("#"):
            continue
        if lineno < feature_line and _LANGUAGE_DIRECTIVE_RE.match(raw):
            continue

        index = bisect.bisect_right(lines, lineno)
        target = attachables[index][1] if index < len(attachables) else trailing_target
        target.comments.append(Comment(text=stripped, location=Location(line=lineno)))

    docstring_steps = sorted(
        (s for s in _iter_steps(feature) if s.doc_string),
        key=lambda s: getattr(s.location, "line", 0) or 0,
    )
    opener_index = 0
    for step in docstring_steps:
        step_line = getattr(step.location, "line", 0) or 0
        while (
            opener_index < len(docstring_openers)
            and docstring_openers[opener_index][0] <= step_line
        ):
            opener_index += 1
        if opener_index >= len(docstring_openers):
            break
        content_type = docstring_openers[opener_index][1]
        opener_index += 1
        if content_type:
            step.doc_string.content_type = content_type
