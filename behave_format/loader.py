"""Feature loading with comment and keyword restoration.

``behave.parser`` discards comments, docstring content types, and the
original Gherkin keywords during parsing. This module bridges the gap:
it parses feature text via behave-model and then restores the lost
information onto the domain model so the formatter can emit it again.

Restored attributes:

- ``comments``: ``Comment`` objects attached to features, rules,
  backgrounds, scenarios, scenario outlines, examples blocks and steps,
  positioned before the element that follows them in the source file.
- ``_trailing_comments``: comments that fall inside the block of an
  element (between the element line and the end of its docstring or
  table) and comments after the last element of the file. Printers emit
  them after the element's body.
- ``_gherkin_keyword``: the original keyword as written (e.g.
  ``"Escenario"``, ``"Scenario Template"``). Printers use it when present
  and fall back to a language-canonical keyword otherwise.
- ``_description``: Background descriptions, which the behave-model
  domain class cannot store natively.
- ``doc_string.content_type`` and ``doc_string.delimiter``: extracted
  from the opening delimiter line in the source (behave stores neither).
"""

from __future__ import annotations

import bisect
import re
from pathlib import Path

from behave.model import Table as _BehaveTable
from behave_model.exceptions import ParseError
from behave_model.model.comment import Comment
from behave_model.model.docstring import DocString
from behave_model.model.examples import Examples
from behave_model.model.feature import Feature
from behave_model.model.location import Location
from behave_model.model.scenario_outline import ScenarioOutline
from behave_model.model.step import Step
from behave_model.parser.adapter import BehaveParserAdapter
from behave_model.parser.parser import parse_feature

_LANGUAGE_DIRECTIVE_RE = re.compile(r"^\s*#\s*language\s*:", re.IGNORECASE)
_DOCSTRING_OPEN_RE = re.compile(r'^\s*("""|\'\'\')')
_INLINE_TAG_COMMENT_RE = re.compile(r"(?:^|\s)(#.*)$")


def load_feature_text(text: str, *, filename: str = "") -> Feature:
    """Parse feature text into a model Feature with comments restored.

    Args:
        text: Raw ``.feature`` file content.
        filename: Optional source name used for locations and errors.

    Returns:
        A domain Feature with comments, original keywords, background
        descriptions and docstring metadata restored from the source.

    Raises:
        ParseError: If the text cannot be parsed or contains no feature.
        TypeError: If ``text`` is not a string.
    """
    if not isinstance(text, str):
        raise TypeError(f"load_feature_text expects str, got {type(text).__name__}")
    # A leading BOM breaks behave's keyword matching on line 1; the
    # formatter normalizes it away on output.
    if text.startswith("\ufeff"):
        text = text[1:]
    behave_feature = parse_feature(text, filename=filename or None)
    if behave_feature is None:
        raise ParseError(f"no feature found in {filename or '<string>'}")
    _patch_empty_examples_tables(behave_feature)
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


def _patch_empty_examples_tables(behave_feature) -> None:
    """Substitute ``None`` example tables with empty behave tables.

    Behave stores ``examples.table = None`` for an ``Examples:`` header
    without a table body; behave-model's adapter dereferences it
    unconditionally and crashes. The empty table lets the ``Examples:``
    header survive the round-trip.
    """
    containers = [behave_feature, *getattr(behave_feature, "rules", [])]
    for container in containers:
        for scenario in getattr(container, "scenarios", []):
            for examples in getattr(scenario, "examples", []):
                if getattr(examples, "table", None) is None:
                    line = getattr(examples, "line", 0) or 0
                    examples.table = _BehaveTable(headings=[], rows=[], line=line)


# -- keyword / step restoration ------------------------------------------------


def _set_keyword(model_el, behave_el) -> None:
    keyword = getattr(behave_el, "keyword", "") or ""
    if keyword:
        model_el._gherkin_keyword = keyword


def _restore_steps(model_steps, behave_steps) -> None:
    for step, behave_step in zip(model_steps, behave_steps, strict=False):
        behave_text = getattr(behave_step, "text", None)
        # behave-model's adapter drops docstrings whose content is empty
        # (``Text("")`` is falsy). An unclosed docstring is never attached
        # by behave, so ``text is not None`` only fires for real ones.
        if behave_text is not None and step.doc_string is None:
            step.doc_string = DocString(content=str(behave_text))


def _restore_scenario(scenario, behave_scenario) -> None:
    _set_keyword(scenario, behave_scenario)
    _restore_steps(scenario.steps, behave_scenario.steps)
    if isinstance(scenario, ScenarioOutline):
        for ex, behave_ex in zip(scenario.examples, behave_scenario.examples, strict=False):
            _set_keyword(ex, behave_ex)


def _restore_container(model_container, behave_container) -> None:
    """Restore keywords and background details for a feature or rule body."""
    behave_background = getattr(behave_container, "background", None)
    if behave_background is not None and getattr(behave_background, "line", 0) == getattr(
        behave_container, "line", -1
    ):
        # behave injects a phantom default background at the container's
        # own line when the source has no Background statement (it exists
        # for behave's runtime inheritance). It is not real content.
        behave_background = None
        model_container.background = None
    if model_container.background is not None and behave_background is not None:
        _set_keyword(model_container.background, behave_background)
        _restore_steps(model_container.background.steps, behave_background.steps)
        # The domain Background has no description field; keep the source
        # text on a private attribute the printers know about.
        description = getattr(behave_background, "description", None) or []
        if description:
            model_container.background._description = "\n".join(description)
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
    """Yield every element comments can attach to, in model order.

    Backgrounds and Examples have no ``comments`` field in the domain
    model; a list is created for them lazily when a comment is assigned.
    """
    yield feature
    # ``is not None``: an empty Background is falsy (``__len__``) but is
    # still a real element comments can attach to.
    if feature.background is not None:
        yield feature.background
        yield from feature.background.steps
    for scenario in feature.scenarios:
        yield from _iter_scenario_attachables(scenario)
    for rule in feature.rules:
        yield rule
        if rule.background is not None:
            yield rule.background
            yield from rule.background.steps
        for scenario in rule.scenarios:
            yield from _iter_scenario_attachables(scenario)


def _iter_scenario_attachables(scenario):
    yield scenario
    yield from scenario.steps
    if isinstance(scenario, ScenarioOutline):
        yield from scenario.examples


def _iter_steps(feature: Feature):
    """Yield every step in model order."""
    for el in _iter_attachables(feature):
        if isinstance(el, Step):
            yield el


def _trailing_comments(el) -> list[Comment]:
    comments = getattr(el, "_trailing_comments", None)
    if comments is None:
        comments = el._trailing_comments = []
    return comments


def _find_docstring_bounds(
    source_lines: list[str], step_line: int, bound: int
) -> tuple[int, int, str, str] | None:
    """Locate a step's docstring in the source.

    Scans forward from ``step_line`` (1-based) for the opening delimiter.
    Per behave semantics the opener is a line whose left-stripped text
    starts with ``\"\"\"`` or ``'''``, and the closer is the first
    following line whose stripped text starts with the same delimiter.

    Returns:
        ``(opener_line, closer_line, delimiter, content_type)`` with
        1-based line numbers, where ``closer_line`` is ``None`` for an
        unclosed docstring; ``None`` if no opener is found before
        ``bound``.
    """
    for index in range(step_line, min(bound, len(source_lines))):
        match = _DOCSTRING_OPEN_RE.match(source_lines[index])
        if not match:
            continue
        delimiter = match.group(1)
        content_type = source_lines[index].strip()[3:].strip()
        opener_line = index + 1
        for close in range(index + 1, len(source_lines)):
            if source_lines[close].strip().startswith(delimiter):
                return (opener_line, close + 1, delimiter, content_type)
        # Unclosed: behave swallows the remaining lines as docstring
        # content without attaching them to the model.
        return (opener_line, None, delimiter, content_type)
    return None


def _restore_comments_and_docstrings(feature: Feature, text: str) -> None:
    source_lines = text.splitlines()

    attachables: list[tuple[int, object]] = sorted(
        ((getattr(el.location, "line", 0) or 0, el) for el in _iter_attachables(feature)),
        key=lambda item: item[0],
    )
    if not attachables:
        return
    attachable_lines = [item[0] for item in attachables]
    feature_line = getattr(feature.location, "line", 0) or 0

    # -- pass 1: docstring ranges and content types ---------------------------
    doc_lines: set[int] = set()
    gap_regions: list[tuple[int, int, object]] = []
    for step in _iter_steps(feature):
        step_line = getattr(step.location, "line", 0) or 0
        next_index = bisect.bisect_right(attachable_lines, step_line)
        bound = (
            attachable_lines[next_index]
            if next_index < len(attachable_lines)
            else len(source_lines)
        )
        bounds = _find_docstring_bounds(source_lines, step_line, bound)
        if bounds:
            opener, closer, delimiter, content_type = bounds
            # An unclosed docstring consumes the rest of the file.
            end = closer if closer is not None else len(source_lines)
            doc_lines.update(range(opener, end + 1))
            if step.doc_string is not None:
                step.doc_string.delimiter = delimiter
                if content_type:
                    step.doc_string.content_type = content_type
                gap_regions.append((step_line, end, step))
        if step.data_table is not None and step.data_table.rows:
            last_row = getattr(step.data_table.rows[-1].location, "line", 0) or 0
            if last_row > step_line:
                gap_regions.append((step_line, last_row, step))

    for line, el in attachables:
        if isinstance(el, Examples) and el.table.rows:
            last_row = getattr(el.table.rows[-1].location, "line", 0) or 0
            if last_row > line:
                gap_regions.append((line, last_row, el))

    # Gap regions are disjoint; sort so lookups can use bisect.
    gap_regions.sort(key=lambda region: region[0])
    gap_starts = [start for start, _, _ in gap_regions]

    # -- pass 2: comments ------------------------------------------------------
    for lineno, raw in enumerate(source_lines, start=1):
        if lineno in doc_lines:
            continue
        stripped = raw.strip()
        comment_text: str | None = None
        if stripped.startswith("#"):
            if lineno < feature_line and _LANGUAGE_DIRECTIVE_RE.match(raw):
                continue
            comment_text = stripped
        elif stripped.startswith("@"):
            # Behave ignores anything after a ``#`` token on tag lines;
            # keep the text as a comment on the following element.
            inline = _INLINE_TAG_COMMENT_RE.search(stripped)
            if inline:
                comment_text = inline.group(1)
        if comment_text is None:
            continue

        target = _attach_target(
            lineno, attachables, attachable_lines, gap_regions, gap_starts, feature
        )
        target.append(Comment(text=comment_text, location=Location(line=lineno)))


def _attach_target(
    lineno: int,
    attachables: list[tuple[int, object]],
    attachable_lines: list[int],
    gap_regions: list[tuple[int, int, object]],
    gap_starts: list[int],
    feature: Feature,
) -> list[Comment]:
    """Pick the comment list for a comment at ``lineno``.

    Comments inside an element's own block (step + docstring/table, or
    an Examples header + table) become trailing comments of that element.
    Comments before the next element attach to it; comments after the
    last element trail the feature.
    """
    gap_index = bisect.bisect_right(gap_starts, lineno) - 1
    if gap_index >= 0:
        start, end, el = gap_regions[gap_index]
        if start < lineno <= end:
            return _trailing_comments(el)
    index = bisect.bisect_right(attachable_lines, lineno)
    if index < len(attachables):
        el = attachables[index][1]
        if not hasattr(el, "comments"):
            el.comments = []
        return el.comments
    return _trailing_comments(feature)
