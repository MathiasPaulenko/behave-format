"""Regression tests for bugs found in the stabilization audit.

Each test guards a defect that was reproduced against the previous
implementation; see the audit notes for the original failure modes.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest
from behave_model.exceptions import ParseError
from behave_model.model.feature import Feature
from behave_model.model.scenario import Scenario
from behave_model.model.step import Step
from behave_model.parser.parser import parse_feature

from behave_format.cli.main import main
from behave_format.config.settings import Settings
from behave_format.loader import load_feature_text
from behave_format.pipeline.formatter import render_feature


def _render(text: str, settings: Settings | None = None) -> str:
    return render_feature(load_feature_text(text), settings or Settings())


def _reparses(text: str) -> None:
    parse_feature(text, filename="<test>")


def _assert_stable(text: str, settings: Settings | None = None) -> str:
    out = _render(text, settings)
    _reparses(out)
    assert _render(out, settings) == out, f"not idempotent:\n{out!r}"
    return out


# -- comments ------------------------------------------------------------------


def test_trailing_comment_stays_at_end() -> None:
    text = "Feature: T\n  Scenario: s\n    Given x\n# trailing comment\n"
    out = _assert_stable(text)
    assert out.splitlines()[-1] == "# trailing comment"


def test_comment_before_background_keeps_position() -> None:
    text = (
        "Feature: T\n"
        "  # sets up everything\n"
        "  Background:\n"
        "    Given set up\n"
        "  Scenario: s\n"
        "    Given x\n"
    )
    out = _assert_stable(text)
    lines = out.splitlines()
    assert lines.index("  # sets up everything") < lines.index("  Background:")


def test_comment_before_examples_keeps_position() -> None:
    text = (
        "Feature: T\n"
        "  Scenario Outline: s\n"
        "    Given <x>\n"
        "  # data for cases\n"
        "  Examples:\n"
        "    | x |\n"
        "    | 1 |\n"
    )
    out = _assert_stable(text)
    lines = out.splitlines()
    assert lines.index("    # data for cases") < lines.index("    Examples:")


def test_comment_inside_table_emitted_after_table() -> None:
    text = (
        "Feature: T\n"
        "  Scenario: s\n"
        "    Given t:\n"
        "      | a |\n"
        "      # about the table\n"
        "    Given y\n"
    )
    out = _assert_stable(text)
    lines = out.splitlines()
    assert lines.index("      | a |") < lines.index("    # about the table")
    assert lines.index("    # about the table") < lines.index("    Given y")


def test_headers_only_table_preserved() -> None:
    text = "Feature: T\n  Scenario: s\n    Given t:\n      | a |\n    Given y\n"
    out = _assert_stable(text)
    assert "| a |" in out


def test_empty_background_preserved() -> None:
    text = "Feature: T\n  Background:\n  Scenario: s\n    Given x\n"
    out = _assert_stable(text)
    assert "Background:" in out


def test_rule_phantom_background_not_printed() -> None:
    # behave injects an empty Background into every Rule without one
    # (line == rule.line); it must never reach the output.
    text = "Feature: T\n  Rule: r\n    Scenario: s\n      Given x\n"
    out = _assert_stable(text)
    assert "Background:" not in out


def test_real_empty_rule_background_preserved() -> None:
    text = "Feature: T\n  Rule: r\n    Background:\n    Scenario: s\n      Given x\n"
    out = _assert_stable(text)
    assert out.count("Background:") == 1


def test_render_project_sort_features() -> None:
    from behave_model.model.project import Project

    from behave_format import format_project, render_project

    p = Project(
        features=[
            load_feature_text("Feature: B\n"),
            load_feature_text("Feature: A\n"),
        ]
    )
    assert render_project(p) == "Feature: B\n\nFeature: A\n"
    assert (
        render_project(format_project(p, Settings(sort_features=True)))
        == "Feature: A\n\nFeature: B\n"
    )


def test_cli_symlink_formats_target(tmp_path: Path) -> None:
    # os.replace on a symlink would silently replace the link with a
    # regular file and leave the real file unformatted.
    target = tmp_path / "real.feature"
    target.write_text("Feature: x\n  Scenario: s\n    Given x\n", encoding="utf-8")
    link = tmp_path / "link.feature"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation not permitted")
    assert main([str(link)]) == 0
    assert link.is_symlink()
    assert "\n\n  Scenario:" in target.read_text(encoding="utf-8")


def test_cli_stdin_roundtrip_subprocess(tmp_path: Path) -> None:
    import os
    import subprocess

    src = "Feature: T\n\n  Scenario: s\n    Given x\n"
    env = os.environ.copy()
    repo_root = str(Path(__file__).resolve().parent.parent)
    env["PYTHONPATH"] = repo_root + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "behave_format", "--stdin"],
        input=src,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
    )
    assert result.returncode == 0
    assert result.stdout == src


def test_examples_header_without_table_survives() -> None:
    # behave stores examples.table = None; behave-model's adapter crashed
    # dereferencing it. The header alone must round-trip.
    text = "Feature: x\n  Scenario Outline: o\n    Given <a>\n    Examples:\n"
    out = _assert_stable(text)
    assert "Examples:" in out


def test_inline_tag_comment_preserved() -> None:
    text = "@a @b # why these tags\nFeature: T\n  Scenario: s\n    Given x\n"
    out = _assert_stable(text)
    assert "# why these tags" in out
    assert "@a @b" in out


# -- docstrings ----------------------------------------------------------------


def test_triple_single_quote_docstring_roundtrips() -> None:
    text = (
        "Feature: T\n"
        "  Scenario: s\n"
        "    Given text:\n"
        "      '''python\n"
        "      # not a comment\n"
        "      code()\n"
        "      '''\n"
        "    Then ok\n"
    )
    out = _assert_stable(text)
    assert "'''python" in out
    assert "# not a comment" in out


def test_empty_docstring_preserved() -> None:
    text = 'Feature: T\n  Scenario: s\n    Given empty:\n      """\n      """\n    Then ok\n'
    out = _assert_stable(text)
    assert '"""\n      """' in out


def test_docstring_delimiter_in_description_does_not_desync() -> None:
    text = (
        "Feature: T\n"
        "  Scenario: s\n"
        '    a description line mentioning """\n'
        "    Given x\n"
        "    # real step comment\n"
        "    Given y\n"
    )
    out = _assert_stable(text)
    assert "# real step comment" in out
    assert 'description line mentioning """' in out


def test_docstring_content_starting_with_delimiter_switches() -> None:
    # A programmatic docstring whose content starts with the delimiter
    # would close early on re-parse; the printer must switch delimiters.
    from behave_model.model.docstring import DocString

    feature = Feature(
        name="T",
        scenarios=[
            Scenario(
                name="s",
                steps=[Step(keyword="Given", name="t", doc_string=DocString(content='"""x'))],
            )
        ],
    )
    out = render_feature(feature, Settings())
    _reparses(out)
    assert '"""x' in out


# -- names and whitespace -------------------------------------------------------


def test_nbsp_in_step_name_preserved() -> None:
    text = "Feature: T\n  Scenario: s\n    Given foo\xa0bar   baz\n"
    out = _assert_stable(text)
    assert "foo\xa0bar baz" in out


def test_wide_unicode_space_in_step_name_preserved() -> None:
    text = "Feature: T\n  Scenario: s\n    Given foo\u3000bar   baz\n"
    out = _assert_stable(text)
    assert "foo\u3000bar baz" in out


def test_escaped_quotes_preserve_literal() -> None:
    text = 'Feature: T\n  Scenario: s\n    Given "a \\"   b\\"" end\n'
    out = _assert_stable(text)
    assert '"a \\"   b\\""' in out


def test_nbsp_in_feature_name_preserved() -> None:
    text = "Feature: My\xa0Feature\n  Scenario: s\n    Given x\n"
    out = _assert_stable(text)
    assert "My\xa0Feature" in out


# -- background description ------------------------------------------------------


def test_background_description_preserved() -> None:
    text = "Feature: T\n  Background:\n    a description line\n    Given set up\n"
    out = _assert_stable(text)
    assert "a description line" in out


# -- loader edge cases ------------------------------------------------------------


def test_bom_input_parses_and_strips() -> None:
    out = _assert_stable("\ufeffFeature: T\n  Scenario: s\n    Given x\n")
    assert not out.startswith("\ufeff")


def test_empty_text_raises_clear_error() -> None:
    with pytest.raises(ParseError, match="no feature found"):
        load_feature_text("")


def test_comments_only_text_raises_clear_error() -> None:
    with pytest.raises(ParseError, match="no feature found"):
        load_feature_text("# just a comment\n")


def test_render_feature_none_settings_matches_default() -> None:
    feature_a = load_feature_text("Feature: T\n  Scenario: s\n    Given x\n")
    feature_b = load_feature_text("Feature: T\n  Scenario: s\n    Given x\n")
    assert render_feature(feature_a, None) == render_feature(feature_b, Settings())


# -- settings validation ----------------------------------------------------------


def test_from_pyproject_non_table_section_raises_value_error(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool]\nbehave-format = 5\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a table"):
        Settings.from_pyproject(str(tmp_path / "pyproject.toml"))


def test_from_pyproject_non_table_tool_returns_defaults(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("tool = 5\n", encoding="utf-8")
    assert Settings.from_pyproject(str(tmp_path / "pyproject.toml")) == Settings()


def test_from_pyproject_string_bool_rejected(tmp_path: Path) -> None:
    # ``bool("false")`` is True — a string value must not silently invert.
    cfg = tmp_path / "pyproject.toml"
    cfg.write_text('[tool.behave-format]\nsort_tags = "false"\n')
    with pytest.raises(ValueError, match="boolean"):
        Settings.from_pyproject(str(cfg))


def test_from_pyproject_bool_indent_rejected(tmp_path: Path) -> None:
    # int(True) == 1 — a boolean must not become a valid indent.
    cfg = tmp_path / "pyproject.toml"
    cfg.write_text("[tool.behave-format]\nindent = true\n")
    with pytest.raises(ValueError, match="integer"):
        Settings.from_pyproject(str(cfg))


def test_from_dict_rejects_non_dict() -> None:
    with pytest.raises(TypeError):
        Settings.from_dict("not a dict")  # type: ignore[arg-type]


# -- CLI ---------------------------------------------------------------------------


def test_cli_missing_config_file_returns_2(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    feature = tmp_path / "f.feature"
    feature.write_text("Feature: T\n  Scenario: s\n    Given x\n", encoding="utf-8")
    exit_code = main(["--config", str(tmp_path / "missing.toml"), str(feature), "--check"])
    assert exit_code == 2
    assert "config file not found" in capsys.readouterr().err


def test_cli_empty_feature_file_returns_2(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    feature = tmp_path / "empty.feature"
    feature.write_text("", encoding="utf-8")
    exit_code = main([str(feature)])
    assert exit_code == 2
    assert "no feature found" in capsys.readouterr().err


def test_cli_malformed_config_section_returns_2(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool]\nbehave-format = 5\n", encoding="utf-8")
    feature = tmp_path / "f.feature"
    feature.write_text("Feature: T\n  Scenario: s\n    Given x\n", encoding="utf-8")
    exit_code = main(["--config", str(tmp_path / "pyproject.toml"), str(feature)])
    assert exit_code == 2


def test_cli_stdin_invalid_utf8_returns_2(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeStdin:
        buffer = io.BytesIO(b"\xff\xfe bad bytes")

    monkeypatch.setattr("sys.stdin", FakeStdin())
    assert main(["--stdin"]) == 2


def test_cli_uppercase_suffix_accepted(tmp_path: Path) -> None:
    feature = tmp_path / "UPPER.FEATURE"
    feature.write_text("@b @a\nFeature: T\n  Scenario: s\n    Given x\n", encoding="utf-8")
    assert main(["--check", str(feature)]) == 1
