"""Unit tests for `MemoryQuery` and `MemoryResult`."""

from __future__ import annotations

import pytest

from nikola.domain.entities.memory_entry import MemoryEntry
from nikola.domain.entities.memory_query import MemoryQuery, MemoryResult
from nikola.domain.value_objects.enums import MemoryType


@pytest.mark.unit
class TestMemoryQuery:
    def test_default_construction_has_all_none_fields(self) -> None:
        q = MemoryQuery()
        assert q.memory_types is None
        assert q.tags is None
        assert q.min_importance is None
        assert q.created_after is None
        assert q.created_before is None
        assert q.limit is None

    def test_is_immutable(self) -> None:
        q = MemoryQuery(limit=5)
        with pytest.raises(AttributeError):
            q.limit = 10  # type: ignore[misc]

    def test_accepts_all_fields(self) -> None:
        from datetime import UTC, datetime

        q = MemoryQuery(
            memory_types=frozenset({MemoryType.SEMANTIC}),
            tags=frozenset({"python"}),
            min_importance=0.5,
            created_after=datetime(2024, 1, 1, tzinfo=UTC),
            created_before=datetime(2026, 1, 1, tzinfo=UTC),
            limit=10,
        )
        assert q.limit == 10
        assert MemoryType.SEMANTIC in q.memory_types  # type: ignore[operator]


@pytest.mark.unit
class TestMemoryResult:
    def test_holds_entries_and_metadata(self) -> None:
        entry = MemoryEntry.create(memory_type=MemoryType.SEMANTIC, content="a fact")
        query = MemoryQuery()
        result = MemoryResult(entries=(entry,), total_found=1, query=query)
        assert len(result.entries) == 1
        assert result.total_found == 1
        assert result.query is query

    def test_empty_result(self) -> None:
        result = MemoryResult(entries=(), total_found=0, query=MemoryQuery())
        assert result.entries == ()

    def test_is_immutable(self) -> None:
        result = MemoryResult(entries=(), total_found=0, query=MemoryQuery())
        with pytest.raises(AttributeError):
            result.total_found = 99  # type: ignore[misc]
