"""Unit tests for `nikola.domain.entities.memory_entry.MemoryEntry`."""

from __future__ import annotations

from datetime import datetime

import pytest

from nikola.domain.entities.memory_entry import MemoryEntry
from nikola.domain.errors import MemoryError
from nikola.domain.value_objects.enums import MemoryType
from nikola.domain.value_objects.memory_id import MemoryId


def _entry(
    memory_type: MemoryType = MemoryType.SEMANTIC,
    content: str = "test content",
    importance: float = 0.5,
    tags: frozenset[str] | None = None,
) -> MemoryEntry:
    return MemoryEntry.create(
        memory_type=memory_type,
        content=content,
        importance=importance,
        tags=tags,
    )


@pytest.mark.unit
class TestMemoryEntryCreate:
    def test_create_generates_a_memory_id(self) -> None:
        assert isinstance(_entry().id, MemoryId)

    def test_create_sets_given_type_and_content(self) -> None:
        e = _entry(memory_type=MemoryType.EPISODIC, content="an event")
        assert e.memory_type is MemoryType.EPISODIC
        assert e.content == "an event"

    def test_create_sets_timestamps(self) -> None:
        e = _entry()
        assert isinstance(e.created_at, datetime)
        assert isinstance(e.updated_at, datetime)

    def test_create_sets_default_importance(self) -> None:
        e = MemoryEntry.create(memory_type=MemoryType.WORKING, content="temp")
        assert e.importance == 0.5

    def test_create_with_explicit_importance(self) -> None:
        e = _entry(importance=0.9)
        assert e.importance == 0.9

    def test_create_with_tags(self) -> None:
        tags = frozenset({"python", "deployment"})
        e = _entry(tags=tags)
        assert e.tags == tags

    def test_create_with_no_tags_gives_empty_frozenset(self) -> None:
        assert _entry().tags == frozenset()

    def test_two_entries_have_different_ids(self) -> None:
        assert _entry().id != _entry().id


@pytest.mark.unit
class TestMemoryEntryValidation:
    def test_empty_content_is_rejected(self) -> None:
        with pytest.raises(MemoryError):
            MemoryEntry.create(memory_type=MemoryType.SEMANTIC, content="")

    def test_whitespace_content_is_rejected(self) -> None:
        with pytest.raises(MemoryError):
            MemoryEntry.create(memory_type=MemoryType.SEMANTIC, content="   ")

    def test_importance_below_zero_is_rejected(self) -> None:
        with pytest.raises(MemoryError, match="importance"):
            _entry(importance=-0.1)

    def test_importance_above_one_is_rejected(self) -> None:
        with pytest.raises(MemoryError, match="importance"):
            _entry(importance=1.001)

    def test_importance_exactly_zero_is_accepted(self) -> None:
        assert _entry(importance=0.0).importance == 0.0

    def test_importance_exactly_one_is_accepted(self) -> None:
        assert _entry(importance=1.0).importance == 1.0


@pytest.mark.unit
class TestMemoryEntryStrengthen:
    def test_strengthen_increases_importance(self) -> None:
        e = _entry(importance=0.5)
        e.strengthen(0.2)
        assert abs(e.importance - 0.7) < 1e-9

    def test_strengthen_clamps_at_one(self) -> None:
        e = _entry(importance=0.9)
        e.strengthen(0.5)
        assert e.importance == 1.0

    def test_negative_delta_decreases_importance(self) -> None:
        e = _entry(importance=0.5)
        e.strengthen(-0.3)
        assert abs(e.importance - 0.2) < 1e-9

    def test_strengthen_clamps_at_zero(self) -> None:
        e = _entry(importance=0.1)
        e.strengthen(-0.5)
        assert e.importance == 0.0

    def test_strengthen_updates_updated_at(self) -> None:
        e = _entry()
        before = e.updated_at
        e.strengthen(0.1)
        assert e.updated_at >= before


@pytest.mark.unit
class TestMemoryEntryHasAllTags:
    def test_entry_has_all_required_tags_returns_true(self) -> None:
        e = _entry(tags=frozenset({"a", "b", "c"}))
        assert e.has_all_tags(frozenset({"a", "b"})) is True

    def test_entry_missing_a_tag_returns_false(self) -> None:
        e = _entry(tags=frozenset({"a"}))
        assert e.has_all_tags(frozenset({"a", "b"})) is False

    def test_empty_required_tags_always_returns_true(self) -> None:
        assert _entry(tags=frozenset()).has_all_tags(frozenset()) is True

    def test_entry_with_no_tags_fails_any_nonempty_requirement(self) -> None:
        assert _entry().has_all_tags(frozenset({"anything"})) is False
