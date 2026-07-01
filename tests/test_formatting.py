"""Formatting regression tests — verify specific formatting rules."""

from __future__ import annotations

from behave_model.model.table import Table, TableRow
from behave_model.model.tag import Tag

from behave_format.config.settings import Settings
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
