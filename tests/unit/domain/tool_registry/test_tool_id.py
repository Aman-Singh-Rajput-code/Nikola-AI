"""Unit tests for ToolId value object."""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.tool_id import ToolId


@pytest.mark.unit
class TestToolId:
    def test_valid_construction(self) -> None:
        tid = ToolId(value="filesystem.read_file")
        assert tid.value == "filesystem.read_file"

    def test_str_returns_value(self) -> None:
        assert str(ToolId(value="terminal.execute")) == "terminal.execute"

    def test_equal_values_are_equal(self) -> None:
        assert ToolId(value="a.b") == ToolId(value="a.b")

    def test_different_values_are_not_equal(self) -> None:
        assert ToolId(value="a.b") != ToolId(value="a.c")

    def test_is_hashable_and_usable_in_set(self) -> None:
        ids = {ToolId(value="x"), ToolId(value="x"), ToolId(value="y")}
        assert len(ids) == 2

    def test_empty_value_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            ToolId(value="")

    def test_whitespace_only_rejected(self) -> None:
        with pytest.raises(ValueError):
            ToolId(value="   ")

    def test_is_immutable(self) -> None:
        tid = ToolId(value="a.b")
        with pytest.raises(AttributeError):
            tid.value = "mutated"  # type: ignore[misc]

    def test_usable_as_dict_key(self) -> None:
        d: dict[ToolId, str] = {ToolId(value="k"): "v"}
        assert d[ToolId(value="k")] == "v"
