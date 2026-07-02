"""Formatter — the main orchestrator for the formatting pipeline.

The pipeline is:
    1. Normalize  — clean whitespace, standardize structure
    2. Sort       — order tags, features, scenarios
    3. Align      — table alignment, trailing whitespace
    4. Print      — convert model to .feature text
"""

from __future__ import annotations

from behave_model.model.feature import Feature
from behave_model.model.project import Project

from behave_format.config.settings import Settings
from behave_format.pipeline.align import align_feature, align_project
from behave_format.pipeline.normalize import normalize_project
from behave_format.pipeline.sort import sort_project
from behave_format.printer.feature_printer import print_feature


def format_project(project: Project, settings: Settings | None = None) -> Project:
    """Format a behave-model Project in place.

    Applies the full pipeline: normalize → sort → align.
    The project is mutated and returned.

    Args:
        project: The project to format.
        settings: Optional formatter settings. Defaults to Settings().

    Returns:
        The same project, formatted.
    """
    if settings is None:
        settings = Settings()

    normalize_project(project)
    sort_project(project, settings)
    align_project(project)
    return project


def format_feature(feature: Feature, settings: Settings | None = None) -> Feature:
    """Format a single Feature in place.

    Args:
        feature: The feature to format.
        settings: Optional formatter settings. Defaults to Settings().

    Returns:
        The same feature, formatted.
    """
    if settings is None:
        settings = Settings()

    from behave_format.pipeline.normalize import _normalize_feature
    from behave_format.pipeline.sort import _sort_feature_tags

    _normalize_feature(feature)
    if settings.sort_tags:
        _sort_feature_tags(feature)
    align_feature(feature)
    return feature


def render_feature(feature: Feature, settings: Settings | None = None) -> str:
    """Format and render a Feature as .feature text.

    Args:
        feature: The feature to format and print.
        settings: Optional formatter settings.

    Returns:
        The formatted .feature file content as a string.
    """
    format_feature(feature, settings)
    return print_feature(feature, indent=settings.indent if settings else 2) + "\n"


def render_project(project: Project, settings: Settings | None = None) -> str:
    """Format and render an entire Project as .feature text.

    Features are separated by a single blank line.

    Args:
        project: The project to format and print.
        settings: Optional formatter settings.

    Returns:
        The formatted content for all features, joined by blank lines.
    """
    format_project(project, settings)
    indent = settings.indent if settings else 2
    parts = [print_feature(f, indent=indent) for f in project.features]
    return "\n\n".join(parts) + "\n"
