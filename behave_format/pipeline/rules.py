"""Formatting rules registry.

Each rule is a callable that transforms the project at a specific
stage of the pipeline. Rules are applied in order.
"""

from __future__ import annotations

from collections.abc import Callable

from behave_model.model.project import Project

from behave_format.config.settings import Settings

Rule = Callable[[Project, Settings], Project]


def apply_rules(project: Project, settings: Settings, rules: list[Rule]) -> Project:
    """Apply a list of formatting rules to the project.

    Args:
        project: The project to format.
        settings: Formatter settings.
        rules: Ordered list of rule callables.

    Returns:
        The formatted project.
    """
    for rule in rules:
        project = rule(project, settings)
    return project
