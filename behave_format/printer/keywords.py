"""Gherkin keyword resolution.

Elements parsed from a file carry their original keyword in the private
``_gherkin_keyword`` attribute (restored by :mod:`behave_format.loader`).
Programmatically built models fall back to the first behave i18n alias
for the element's language.
"""

from __future__ import annotations

from behave import i18n

_ENGLISH = i18n.languages["en"]


def is_known_language(language: str) -> bool:
    """Return True if behave's i18n tables know this language code."""
    return language in i18n.languages


# Canonical spellings — behave's i18n tables list aliases in match order
# (e.g. "Example" before "Scenario"), so the first entry is not always
# the conventional keyword to print.
_PREFERRED = {
    "feature": "Feature",
    "background": "Background",
    "scenario": "Scenario",
    "scenario_outline": "Scenario Outline",
    "examples": "Examples",
    "rule": "Rule",
}


def gherkin_keyword(element, kind: str, language: str = "en") -> str:
    """Return the Gherkin keyword to print for an element.

    Args:
        element: Model element (Feature, Rule, Scenario, Examples, ...).
        kind: behave i18n keyword kind (``"feature"``, ``"scenario"``, ...).
        language: Feature file language code (e.g. ``"en"``, ``"es"``).

    Returns:
        The original keyword if the element was parsed from a file,
        otherwise the conventional i18n alias for the language.
    """
    keyword = getattr(element, "_gherkin_keyword", "")
    if keyword:
        return keyword
    aliases = i18n.languages.get(language, _ENGLISH)
    choices = aliases.get(kind) or _ENGLISH[kind]
    preferred = _PREFERRED[kind]
    return preferred if preferred in choices else choices[0]
