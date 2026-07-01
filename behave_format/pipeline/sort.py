"""Sort stage — order tags, features, and scenarios.

Sorting is configurable via Settings. By default only tags are sorted
alphabetically. Feature and scenario sorting are opt-in.
"""

from __future__ import annotations

from behave_model.model.feature import Feature
from behave_model.model.project import Project
from behave_model.model.rule import Rule
from behave_model.model.scenario_outline import ScenarioOutline

from behave_format.config.settings import Settings


def sort_project(project: Project, settings: Settings) -> Project:
    """Apply sorting rules to the project.

    Args:
        project: The project to sort (mutated in place).
        settings: Formatter settings controlling sort behavior.

    Returns:
        The same project, sorted.
    """
    if settings.sort_tags:
        _sort_all_tags(project)

    if settings.sort_features:
        project.features.sort(key=lambda f: f.name)

    if settings.sort_scenarios:
        for feature in project.features:
            feature.scenarios.sort(key=lambda s: s.name)
            for rule in feature.rules:
                rule.scenarios.sort(key=lambda s: s.name)

    return project


def _sort_all_tags(project: Project) -> None:
    project.global_tags.sort(key=lambda t: t.name)
    for feature in project.features:
        _sort_feature_tags(feature)


def _sort_feature_tags(feature: Feature) -> None:
    feature.tags.sort(key=lambda t: t.name)
    for scenario in feature.scenarios:
        scenario.tags.sort(key=lambda t: t.name)
        if isinstance(scenario, ScenarioOutline):
            for ex in scenario.examples:
                ex.tags.sort(key=lambda t: t.name)
    for rule in feature.rules:
        _sort_rule_tags(rule)


def _sort_rule_tags(rule: Rule) -> None:
    rule.tags.sort(key=lambda t: t.name)
    for scenario in rule.scenarios:
        scenario.tags.sort(key=lambda t: t.name)
        if isinstance(scenario, ScenarioOutline):
            for ex in scenario.examples:
                ex.tags.sort(key=lambda t: t.name)
