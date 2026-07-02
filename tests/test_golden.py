"""Golden file tests — compare formatter output against expected files."""

from __future__ import annotations

from pathlib import Path

import pytest
from behave_model import load_feature

from behave_format.config.settings import Settings
from behave_format.pipeline.formatter import render_feature

EXAMPLES = Path(__file__).parent.parent / "examples"
GOLDEN = Path(__file__).parent / "golden"

GOLDEN_CASES = [
    ("login.feature", "login_expected.feature"),
    ("data_tables.feature", "data_tables_expected.feature"),
    ("rules.feature", "rules_expected.feature"),
    ("shopping_cart.feature", "shopping_cart_expected.feature"),
]


@pytest.mark.parametrize("input_name,expected_name", GOLDEN_CASES)
def test_golden_file(input_name: str, expected_name: str) -> None:
    input_path = EXAMPLES / input_name
    expected_path = GOLDEN / expected_name

    feature = load_feature(input_path)
    settings = Settings()
    output = render_feature(feature, settings)
    expected = expected_path.read_text(encoding="utf-8")

    assert output == expected, (
        f"Golden mismatch for {input_name}.\nExpected:\n{expected}\nGot:\n{output}"
    )
