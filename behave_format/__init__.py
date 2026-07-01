"""behave-format — The opinionated formatter for Behave .feature files.

behave-format is the equivalent of Black for Gherkin .feature files.
It consumes a behave-model Project and produces deterministic,
beautifully formatted output.

Public API:

    from behave_format import format_project, render_project, Settings
    from behave_model import load_project

    project = load_project("features/")
    format_project(project)
    # or render to text:
    text = render_project(project)

CLI:

    behave-format features/        # format in place
    behave-format --check features/  # check mode (exit 1 if changes needed)
    behave-format --diff features/   # show diff without writing
"""

from behave_format.config.settings import Settings
from behave_format.pipeline.formatter import (
    format_feature,
    format_project,
    render_feature,
    render_project,
)

__version__ = "1.0.0"

__all__ = [
    "Settings",
    "format_feature",
    "format_project",
    "render_feature",
    "render_project",
    "__version__",
]
