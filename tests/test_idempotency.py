"""Idempotency tests — format(format(x)) == format(x)."""

from __future__ import annotations

from pathlib import Path

import pytest
from behave_model import load_feature

from behave_format.config.settings import Settings
from behave_format.pipeline.formatter import render_feature

EXAMPLES = Path(__file__).parent.parent / "examples"

ALL_EXAMPLES = list(EXAMPLES.glob("*.feature"))


@pytest.mark.parametrize("feature_path", ALL_EXAMPLES, ids=lambda p: p.name)
def test_idempotent_single_feature(feature_path: Path) -> None:
    settings = Settings()
    feature = load_feature(feature_path)
    first = render_feature(feature, settings)

    feature2 = load_feature(feature_path)
    second = render_feature(feature2, settings)

    assert first == second


@pytest.mark.parametrize("feature_path", ALL_EXAMPLES, ids=lambda p: p.name)
def test_idempotent_double_format(feature_path: Path) -> None:
    from behave_model.parser.adapter import BehaveParserAdapter
    from behave_model.parser.parser import parse_feature

    settings = Settings()
    feature = load_feature(feature_path)
    first = render_feature(feature, settings)

    adapter = BehaveParserAdapter()
    parsed = parse_feature(first, filename=str(feature_path))
    reformatted_feature = adapter.adapt_feature(parsed, filename=str(feature_path))
    second = render_feature(reformatted_feature, settings)

    assert first == second


def test_idempotent_with_all_settings() -> None:
    feature_path = EXAMPLES / "login.feature"

    for sort_tags in [True, False]:
        for sort_features in [True, False]:
            for sort_scenarios in [True, False]:
                settings = Settings(
                    sort_tags=sort_tags,
                    sort_features=sort_features,
                    sort_scenarios=sort_scenarios,
                )
                feature = load_feature(feature_path)
                first = render_feature(feature, settings)

                from behave_model.parser.adapter import BehaveParserAdapter
                from behave_model.parser.parser import parse_feature

                adapter = BehaveParserAdapter()
                parsed = parse_feature(first, filename=str(feature_path))
                reformatted = adapter.adapt_feature(parsed, filename=str(feature_path))
                second = render_feature(reformatted, settings)

                assert first == second, (
                    f"Not idempotent with sort_tags={sort_tags}, "
                    f"sort_features={sort_features}, "
                    f"sort_scenarios={sort_scenarios}"
                )
