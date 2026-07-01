"""Performance tests — ensure formatter handles large inputs efficiently."""

from __future__ import annotations

import time
from pathlib import Path

from behave_model.model.feature import Feature
from behave_model.model.scenario import Scenario
from behave_model.model.step import Step
from behave_model.model.tag import Tag

from behave_format.config.settings import Settings

EXAMPLES = Path(__file__).parent.parent / "examples"


def _generate_large_feature(num_scenarios: int = 500) -> Feature:
    feature = Feature(
        name="Large Feature",
        description="Performance test feature",
        tags=[Tag(name="@perf"), Tag(name="@large")],
    )
    for i in range(num_scenarios):
        scenario = Scenario(
            name=f"Scenario {i}",
            tags=[Tag(name=f"@tag{i % 10}")],
            steps=[
                Step(keyword="Given", name=f"step given {i}"),
                Step(keyword="When", name=f"step when {i}"),
                Step(keyword="Then", name=f"step then {i}"),
            ],
        )
        feature.scenarios.append(scenario)
    return feature


def test_large_feature_performance() -> None:
    from behave_format.pipeline.formatter import render_feature

    feature = _generate_large_feature(500)
    settings = Settings()

    start = time.perf_counter()
    output = render_feature(feature, settings)
    elapsed = time.perf_counter() - start

    assert len(output) > 0
    assert elapsed < 2.0, f"Formatting took {elapsed:.3f}s, expected < 2s"


def test_many_tags_sorted() -> None:
    from behave_format.pipeline.formatter import render_feature

    feature = Feature(name="Tag Test")
    scenario = Scenario(name="Tag scenario")
    for i in range(100):
        scenario.tags.append(Tag(name=f"@tag_{i:03d}"))
    feature.scenarios.append(scenario)

    settings = Settings(sort_tags=True)
    output = render_feature(feature, settings)

    lines = output.splitlines()
    tag_line = lines[2]
    tag_names = tag_line.split()
    assert tag_names == sorted(tag_names)
