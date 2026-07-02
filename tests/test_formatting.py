"""Formatting regression tests — verify specific formatting rules."""

from __future__ import annotations

from behave_model.model.comment import Comment
from behave_model.model.feature import Feature
from behave_model.model.scenario import Scenario
from behave_model.model.step import Step
from behave_model.model.table import Table, TableRow
from behave_model.model.tag import Tag

from behave_format.config.settings import Settings
from behave_format.pipeline.formatter import format_feature
from behave_format.printer.feature_printer import print_feature
from behave_format.printer.table_printer import print_table
from behave_format.printer.tag_printer import print_tags


def _make_table() -> Table:
    return Table(
        headers=["user", "password"],
        rows=[
            TableRow(cells=["john", "123"]),
            TableRow(cells=["alice", "secret"]),
        ],
    )


def test_table_alignment() -> None:
    table = _make_table()
    output = print_table(table, indent=4)
    lines = output.splitlines()
    assert lines[0] == "    | user  | password |"
    assert lines[1] == "    | john  | 123      |"
    assert lines[2] == "    | alice | secret   |"


def test_tags_sorted_alphabetically() -> None:
    tags = [Tag(name="@zebra"), Tag(name="@apple"), Tag(name="@mango")]
    output = print_tags(sorted(tags, key=lambda t: t.name), indent=0)
    assert output == "@apple @mango @zebra"


def test_tags_not_sorted_when_disabled() -> None:
    tags = [Tag(name="@zebra"), Tag(name="@apple"), Tag(name="@mango")]
    output = print_tags(tags, indent=0)
    assert output == "@zebra @apple @mango"


def test_no_trailing_whitespace() -> None:
    table = _make_table()
    output = print_table(table, indent=4)
    for line in output.splitlines():
        assert line == line.rstrip()


def test_indent_default_2() -> None:
    settings = Settings()
    assert settings.indent == 2


def test_indent_custom() -> None:
    settings = Settings(indent=4)
    assert settings.indent == 4


def test_settings_from_dict() -> None:
    settings = Settings.from_dict(
        {
            "indent": 4,
            "sort_tags": False,
            "sort_features": True,
        }
    )
    assert settings.indent == 4
    assert settings.sort_tags is False
    assert settings.sort_features is True


def test_settings_defaults() -> None:
    settings = Settings()
    assert settings.indent == 2
    assert settings.sort_tags is True
    assert settings.sort_features is False
    assert settings.sort_scenarios is False
    assert settings.line_length == 120


def test_settings_immutable() -> None:
    settings = Settings()
    try:
        settings.indent = 4
        raise AssertionError("Should have raised FrozenInstanceError")
    except AttributeError:
        pass


def test_feature_comments_preserved() -> None:
    feature = Feature(
        name="Login",
        comments=[Comment(text="# This is a feature comment")],
        scenarios=[
            Scenario(
                name="Login scenario",
                steps=[Step(keyword="Given", name="user exists")],
            ),
        ],
    )
    format_feature(feature)
    output = print_feature(feature)
    assert "# This is a feature comment" in output


def test_scenario_comments_preserved() -> None:
    feature = Feature(
        name="Login",
        scenarios=[
            Scenario(
                name="Login scenario",
                comments=[Comment(text="# Scenario comment")],
                steps=[Step(keyword="Given", name="user exists")],
            ),
        ],
    )
    format_feature(feature)
    output = print_feature(feature)
    assert "# Scenario comment" in output


def test_step_comments_preserved() -> None:
    feature = Feature(
        name="Login",
        scenarios=[
            Scenario(
                name="Login scenario",
                steps=[
                    Step(
                        keyword="Given",
                        name="user exists",
                        comments=[Comment(text="# step comment")],
                    ),
                ],
            ),
        ],
    )
    format_feature(feature)
    output = print_feature(feature)
    assert "# step comment" in output


def test_language_directive_preserved() -> None:
    feature = Feature(
        name="Inicio de sesión",
        language="es",
        scenarios=[Scenario(name="Escenario", steps=[Step(keyword="Dado", name="usuario existe")])],
    )
    format_feature(feature)
    output = print_feature(feature)
    assert "# language: es" in output


def test_language_directive_omitted_for_english() -> None:
    feature = Feature(
        name="Login",
        language="en",
        scenarios=[
            Scenario(
                name="Login scenario",
                steps=[Step(keyword="Given", name="user exists")],
            ),
        ],
    )
    format_feature(feature)
    output = print_feature(feature)
    assert "# language:" not in output


def test_format_feature_applies_align() -> None:
    table = Table(
        headers=["user", "password"],
        rows=[TableRow(cells=["john", "123"])],
    )
    feature = Feature(
        name="Login",
        scenarios=[
            Scenario(
                name="Login scenario",
                steps=[Step(keyword="Given", name="user exists", data_table=table)],
            ),
        ],
    )
    format_feature(feature)
    output = print_feature(feature)
    table_lines = [line for line in output.splitlines() if "|" in line]
    assert all(line.rstrip() == line for line in table_lines)
    assert "| user | password |" in output
    assert "| john | 123      |" in output
