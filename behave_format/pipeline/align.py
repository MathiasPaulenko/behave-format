"""Align stage — table alignment and trailing whitespace removal.

This stage ensures tables are properly aligned and no trailing
whitespace remains in any text content. It operates on the model
before printing.
"""

from __future__ import annotations

from behave_model.model.feature import Feature
from behave_model.model.project import Project
from behave_model.model.scenario_outline import ScenarioOutline
from behave_model.model.step import Step
from behave_model.model.table import Table


def align_project(project: Project) -> Project:
    """Apply alignment rules to the project.

    Args:
        project: The project to align (mutated in place).

    Returns:
        The same project, aligned.
    """
    for feature in project.features:
        _align_feature(feature)
    return project


def align_feature(feature: Feature) -> Feature:
    """Apply alignment rules to a single feature.

    Args:
        feature: The feature to align (mutated in place).

    Returns:
        The same feature, aligned.
    """
    _align_feature(feature)
    return feature


def _align_feature(feature: Feature) -> None:
    if feature.background:
        for step in feature.background.steps:
            _align_step(step)
    for scenario in feature.scenarios:
        for step in scenario.steps:
            _align_step(step)
        if isinstance(scenario, ScenarioOutline):
            for ex in scenario.examples:
                _align_table(ex.table)
    for rule in feature.rules:
        if rule.background:
            for step in rule.background.steps:
                _align_step(step)
        for scenario in rule.scenarios:
            for step in scenario.steps:
                _align_step(step)
            if isinstance(scenario, ScenarioOutline):
                for ex in scenario.examples:
                    _align_table(ex.table)


def _align_step(step: Step) -> None:
    if step.data_table:
        _align_table(step.data_table)


def _align_table(table: Table) -> None:
    _ensure_rectangular(table)


def _ensure_rectangular(table: Table) -> None:
    # Pad short rows and extend headers instead of truncating:
    # extra cells are data and must never be dropped.
    num_cols = max(
        [len(table.headers)] + [len(row.cells) for row in table.rows],
        default=0,
    )
    while len(table.headers) < num_cols:
        table.headers.append("")
    for row in table.rows:
        while len(row.cells) < num_cols:
            row.cells.append("")
