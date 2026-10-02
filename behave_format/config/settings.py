"""Formatter settings with minimal configuration philosophy.

Settings can be loaded from ``pyproject.toml`` under ``[tool.behave-format]``
or constructed programmatically.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


@dataclass(frozen=True)
class Settings:
    """Immutable formatter settings.

    Attributes:
        indent: Number of spaces for indentation (default 2).
        sort_tags: Sort tags alphabetically (default True).
        sort_features: Sort features by name (default False).
        sort_scenarios: Sort scenarios by name (default False).
        line_length: Maximum line length for reference (default 120).
    """

    indent: int = 2
    sort_tags: bool = True
    sort_features: bool = False
    sort_scenarios: bool = False
    line_length: int = 120

    def __post_init__(self) -> None:
        if self.indent < 1:
            raise ValueError(f"indent must be >= 1, got {self.indent}")
        if self.line_length < 1:
            raise ValueError(f"line_length must be >= 1, got {self.line_length}")

    @classmethod
    def from_pyproject(cls, path: str = "pyproject.toml") -> Settings:
        """Load settings from a ``pyproject.toml`` file.

        Args:
            path: Path to the ``pyproject.toml`` file.

        Returns:
            A Settings instance. If the file or section is missing,
            defaults are returned.
        """
        from pathlib import Path

        p = Path(path)
        if not p.exists():
            return cls()

        with p.open("rb") as f:
            data = tomllib.load(f)

        section = data.get("tool", {}).get("behave-format", {})
        try:
            return cls(
                indent=int(section.get("indent", 2)),
                sort_tags=bool(section.get("sort_tags", True)),
                sort_features=bool(section.get("sort_features", False)),
                sort_scenarios=bool(section.get("sort_scenarios", False)),
                line_length=int(section.get("line_length", 120)),
            )
        except (TypeError, ValueError) as e:
            raise ValueError(f"invalid [tool.behave-format] section: {e}") from e

    @classmethod
    def from_dict(cls, data: dict) -> Settings:
        """Create settings from a dictionary.

        Args:
            data: Dictionary with optional keys: indent, sort_tags,
                sort_features, sort_scenarios, line_length.

        Returns:
            A Settings instance.
        """
        return cls(
            indent=int(data.get("indent", 2)),
            sort_tags=bool(data.get("sort_tags", True)),
            sort_features=bool(data.get("sort_features", False)),
            sort_scenarios=bool(data.get("sort_scenarios", False)),
            line_length=int(data.get("line_length", 120)),
        )

    def with_indent(self, indent: int) -> Settings:
        """Return a new Settings with the given indent.

        Args:
            indent: Number of spaces for indentation.

        Returns:
            A new Settings instance with the updated indent.
        """
        return replace(self, indent=indent)
