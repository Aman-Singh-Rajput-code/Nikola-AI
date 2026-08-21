"""Unit tests for Tool domain entity."""

from __future__ import annotations

import pytest

from nikola.domain.entities.tool import Tool
from nikola.domain.value_objects.tool_id import ToolId


def _tid(name: str = "test.tool") -> ToolId:
    return ToolId(value=name)


@pytest.mark.unit
class TestToolCreate:
    def test_create_sets_all_fields(self) -> None:
        tid = _tid()
        tool = Tool.create(
            tid, description="A test tool", version="2.0.0", metadata={"category": "test"}
        )
        assert tool.id == tid
        assert tool.description == "A test tool"
        assert tool.version == "2.0.0"
        assert tool.metadata["category"] == "test"

    def test_create_default_version(self) -> None:
        tool = Tool.create(_tid(), description="desc")
        assert tool.version == "1.0.0"

    def test_create_default_metadata_is_empty(self) -> None:
        tool = Tool.create(_tid(), description="desc")
        assert tool.metadata == {}

    def test_create_with_none_metadata_gives_empty_dict(self) -> None:
        tool = Tool.create(_tid(), description="desc", metadata=None)
        assert tool.metadata == {}

    def test_empty_description_rejected(self) -> None:
        with pytest.raises(ValueError, match="description"):
            Tool.create(_tid(), description="")

    def test_whitespace_description_rejected(self) -> None:
        with pytest.raises(ValueError):
            Tool.create(_tid(), description="   ")

    def test_direct_construction_also_validates(self) -> None:
        with pytest.raises(ValueError):
            Tool(id=_tid(), description="")


@pytest.mark.unit
class TestToolImmutability:
    def test_tool_is_immutable(self) -> None:
        tool = Tool.create(_tid(), description="desc")
        with pytest.raises(AttributeError):
            tool.description = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestToolEquality:
    def test_same_id_and_fields_are_equal(self) -> None:
        tid = _tid()
        a = Tool.create(tid, description="desc")
        b = Tool.create(tid, description="desc")
        assert a == b

    def test_different_ids_are_not_equal(self) -> None:
        a = Tool.create(_tid("a.tool"), description="desc")
        b = Tool.create(_tid("b.tool"), description="desc")
        assert a != b
