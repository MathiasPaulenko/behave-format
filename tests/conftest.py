"""Test fixtures and shared utilities for behave-format tests."""

from __future__ import annotations

from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
GOLDEN_DIR = Path(__file__).parent / "golden"


@pytest.fixture
def examples_dir() -> Path:
    return EXAMPLES_DIR


@pytest.fixture
def golden_dir() -> Path:
    return GOLDEN_DIR


@pytest.fixture
def settings():
    from behave_format.config.settings import Settings

    return Settings()
