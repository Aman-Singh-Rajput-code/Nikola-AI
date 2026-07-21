"""Unit tests for `MemoryId` value object and `MemoryType` enum."""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.enums import MemoryType
from nikola.domain.value_objects.memory_id import MemoryId


@pytest.mark.unit
class TestMemoryId:
    def test_generate_returns_a_memory_id(self) -> None:
        assert isinstance(MemoryId.generate(), MemoryId)

    def test_generate_produces_unique_values(self) -> None:
        assert MemoryId.generate() != MemoryId.generate()

    def test_equal_values_are_equal(self) -> None:
        assert MemoryId(value="abc") == MemoryId(value="abc")

    def test_different_values_are_not_equal(self) -> None:
        assert MemoryId(value="abc") != MemoryId(value="xyz")

    def test_is_hashable(self) -> None:
        ids = {MemoryId(value="a"), MemoryId(value="a"), MemoryId(value="b")}
        assert len(ids) == 2

    def test_empty_value_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            MemoryId(value="")

    def test_str_returns_value(self) -> None:
        assert str(MemoryId(value="abc")) == "abc"

    def test_is_immutable(self) -> None:
        mid = MemoryId(value="abc")
        with pytest.raises(AttributeError):
            mid.value = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestMemoryType:
    def test_has_exactly_four_members(self) -> None:
        assert {m.value for m in MemoryType} == {
            "working",
            "episodic",
            "semantic",
            "procedural",
        }

    def test_is_str_subclass(self) -> None:
        assert isinstance(MemoryType.SEMANTIC, str)

    def test_members_equal_their_string_values(self) -> None:
        assert MemoryType.WORKING == "working"  # type: ignore[comparison-overlap]
