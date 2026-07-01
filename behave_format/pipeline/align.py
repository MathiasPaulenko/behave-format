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


def _align_feature(feature: Feature) -> None:
    if feature.background:
        for step in feature.background.steps:
            _align_step(step)
    for scenario in feature.scenarios:
        for step in scenario.steps:
            _align_step(step)
        if isinstance(scenario, ScenarioOutline):
            for ex in scenario.examples:
                _align_table(examples_table=ex.table)
    for rule in feature.rules:
        if rule.background:
            for step in rule.background.steps:
                _align_step(step)
        for scenario in rule.scenarios:
            for step in scenario.steps:
                _align_step(step)
            if isinstance(scenario, ScenarioOutline):
                for ex in scenario.examples:
                    _align_table(examples_table=ex.table)


def _align_step(step: Step) -> None:
    if step.data_table:
        _align_table(step.data_table)


def _align_table(table: Table, *, examples_table: Table | None = None) -> None:
    target = examples_table if examples_table is not None else table
    _ensure_rectangular(target)


def _ensure_rectangular(table: Table) -> None:
    num_cols = len(table.headers)
    for row in table.rows:
        while len(row.cells) < num_cols:
            row.cells.append("")
        if len(row.cells) > num_cols:
            row.cells = row.cells[:num_cols]
