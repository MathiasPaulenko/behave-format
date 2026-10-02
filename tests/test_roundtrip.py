"""Round-trip regression tests — parse real text, format, re-parse."""

from __future__ import annotations

from behave_model.parser.parser import parse_feature

from behave_format.config.settings import Settings
from behave_format.loader import load_feature_text
from behave_format.pipeline.formatter import render_feature


def _render(text: str, settings: Settings | None = None) -> str:
    return render_feature(load_feature_text(text), settings or Settings())


def _reparses(text: str) -> None:
    parse_feature(text, filename="<test>")


def test_escaped_pipe_in_cell_roundtrips() -> None:
    text = "Feature: T\n  Scenario: s\n    Given a table:\n      | a   | b |\n      | x\\|y | z |\n"
    out = _render(text)
    assert "x\\|y" in out
    _reparses(out)
    # And it is idempotent
    assert _render(out) == out


def test_comments_are_preserved() -> None:
    text = (
        "# file header comment\n"
        "Feature: T\n"
        "  # before background\n"
        "  Background:\n"
        "    Given base\n"
        "\n"
        "  # before scenario\n"
        "  Scenario: s\n"
        "    Given a step\n"
        "    # between steps\n"
        "    When another\n"
        "\n"
        "  # trailing comment\n"
    )
    out = _render(text)
    for comment in (
        "# file header comment",
        "# before background",
        "# before scenario",
        "# between steps",
        "# trailing comment",
    ):
        assert comment in out, f"lost comment: {comment}"
    _reparses(out)
    assert _render(out) == out


def test_comment_inside_docstring_is_content() -> None:
    text = (
        'Feature: T\n  Scenario: s\n    Given text:\n      """\n      # not a comment\n      """\n'
    )
    out = _render(text)
    assert "# not a comment" in out


def test_spanish_keywords_preserved() -> None:
    text = "# language: es\nCaracterística: Prueba\n  Escenario: algo\n    Dado algo\n"
    out = _render(text)
    assert "Característica: Prueba" in out
    assert "Escenario: algo" in out
    _reparses(out)
    assert _render(out) == out


def test_docstring_content_type_preserved() -> None:
    text = 'Feature: T\n  Scenario: s\n    Given json:\n      """json\n      {}\n      """\n'
    out = _render(text)
    assert '"""json' in out


def test_step_quoted_whitespace_preserved() -> None:
    text = (
        "Feature: T\n"
        "  Scenario: s\n"
        '    When I do "something   with   spaces"\n'
        "    And a   collapsed    step\n"
    )
    out = _render(text)
    assert 'When I do "something   with   spaces"' in out
    assert "And a collapsed step" in out


def test_placeholder_whitespace_preserved() -> None:
    text = (
        "Feature: T\n"
        "  Scenario Outline: o\n"
        "    Given <a  b>\n"
        "    Examples:\n"
        "      | a  b |\n"
        "      | 1    |\n"
    )
    out = _render(text)
    assert "<a  b>" in out


def test_docstring_blank_line_has_no_trailing_whitespace() -> None:
    text = (
        "Feature: T\n"
        "  Scenario: s\n"
        "    Given text:\n"
        '      """\n'
        "      line1\n"
        "\n"
        "      line3\n"
        '      """\n'
    )
    out = _render(text)
    for line in out.splitlines():
        assert line == line.rstrip(), f"trailing whitespace: {line!r}"


def test_ragged_table_pads_instead_of_truncating() -> None:
    # Via the API, a row may have more cells than headers — extra cells
    # must be kept, not dropped.
    from behave_model.model.feature import Feature
    from behave_model.model.scenario import Scenario
    from behave_model.model.step import Step
    from behave_model.model.table import Table, TableRow

    table = Table(headers=["a"], rows=[TableRow(cells=["x", "y", "z"])])
    feature = Feature(
        name="T",
        scenarios=[Scenario(name="s", steps=[Step(keyword="Given", name="t", data_table=table)])],
    )
    out = render_feature(feature, Settings())
    assert "z" in out


def test_description_keeps_interior_spacing() -> None:
    text = "Feature: T\n  col1   col2   col3\n  ---    ----   ----\n\n  Scenario: s\n    Given x\n"
    out = _render(text)
    assert "col1   col2   col3" in out


def test_duplicate_tags_removed() -> None:
    text = "@a @a @b\nFeature: T\n  Scenario: s\n    Given x\n"
    out = _render(text)
    assert "@a @b" in out
    assert "@a @a" not in out
