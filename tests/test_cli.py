"""CLI tests for behave-format."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from behave_format.cli.main import main

UNFORMATTED_INPUT = """@smoke @auth
Feature: Login
  As a user
  I want to log in

  Background:
    Given a database connection

  @happy
  Scenario: Successful login
    Given the user is on the login page
    When the user enters "admin" and "password"
    Then the user should be logged in
"""

FORMATTED_OUTPUT = """@auth @smoke
Feature: Login
  As a user
  I want to log in

  Background:
    Given a database connection

  @happy
  Scenario: Successful login
    Given the user is on the login page
    When the user enters "admin" and "password"
    Then the user should be logged in
"""


@pytest.fixture
def temp_feature_file():
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".feature", delete=False, encoding="utf-8"
    ) as f:
        f.write(UNFORMATTED_INPUT)
        path = Path(f.name)
    yield path
    if path.exists():
        path.unlink()


def test_cli_write_mode(temp_feature_file: Path) -> None:
    exit_code = main([str(temp_feature_file)])
    assert exit_code == 0
    content = temp_feature_file.read_text(encoding="utf-8")
    assert content == FORMATTED_OUTPUT


def test_cli_check_mode_clean(temp_feature_file: Path) -> None:
    main([str(temp_feature_file)])
    exit_code = main(["--check", str(temp_feature_file)])
    assert exit_code == 0


def test_cli_check_mode_dirty(temp_feature_file: Path) -> None:
    exit_code = main(["--check", str(temp_feature_file)])
    assert exit_code == 1


def test_cli_diff_mode(temp_feature_file: Path, capsys: pytest.CaptureFixture) -> None:
    exit_code = main(["--diff", str(temp_feature_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "@auth @smoke" in captured.out
    content = temp_feature_file.read_text(encoding="utf-8")
    assert content == UNFORMATTED_INPUT


def test_cli_no_paths_prints_help(capsys: pytest.CaptureFixture) -> None:
    exit_code = main([])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "usage" in captured.out.lower() or "behave-format" in captured.out.lower()


def test_cli_quiet_mode(temp_feature_file: Path, capsys: pytest.CaptureFixture) -> None:
    exit_code = main(["--quiet", str(temp_feature_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out == ""


def test_cli_directory_mode(tmp_path: Path) -> None:
    features_dir = tmp_path / "features"
    features_dir.mkdir()
    feature_file = features_dir / "test.feature"
    feature_file.write_text(UNFORMATTED_INPUT, encoding="utf-8")

    exit_code = main([str(features_dir)])
    assert exit_code == 0
    content = feature_file.read_text(encoding="utf-8")
    assert content == FORMATTED_OUTPUT


def test_cli_idempotent_write(temp_feature_file: Path) -> None:
    main([str(temp_feature_file)])
    first = temp_feature_file.read_text(encoding="utf-8")
    main([str(temp_feature_file)])
    second = temp_feature_file.read_text(encoding="utf-8")
    assert first == second


def test_cli_version_flag(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "behave-format" in captured.out
    assert "1.0.0" in captured.out


def test_cli_nonexistent_file_returns_2(capsys: pytest.CaptureFixture) -> None:
    exit_code = main(["nonexistent.feature"])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "not found" in captured.err.lower()


def test_cli_nonexistent_file_in_directory_does_not_crash(tmp_path: Path) -> None:
    features_dir = tmp_path / "features"
    features_dir.mkdir()
    feature_file = features_dir / "test.feature"
    feature_file.write_text(UNFORMATTED_INPUT, encoding="utf-8")

    exit_code = main([str(features_dir)])
    assert exit_code == 0
    content = feature_file.read_text(encoding="utf-8")
    assert content == FORMATTED_OUTPUT


def test_cli_indent_override(temp_feature_file: Path) -> None:
    exit_code = main(["--indent", "4", str(temp_feature_file)])
    assert exit_code == 0
    content = temp_feature_file.read_text(encoding="utf-8")
    assert "    Given a database connection" in content


def test_cli_stdin_mode(capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch) -> None:
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO(UNFORMATTED_INPUT))
    exit_code = main(["--stdin"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "@auth @smoke" in captured.out


def test_cli_stdin_check_clean(
    capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO(FORMATTED_OUTPUT))
    exit_code = main(["--stdin", "--check"])
    assert exit_code == 0


def test_cli_stdin_check_dirty(
    capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO(UNFORMATTED_INPUT))
    exit_code = main(["--stdin", "--check", "--quiet"])
    assert exit_code == 1
