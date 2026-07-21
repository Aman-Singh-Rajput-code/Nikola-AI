"""Unit tests for `ImportanceRetrievalStrategy`."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from nikola.application.memory.memory_retrieval_strategy import (
    ImportanceRetrievalStrategy,
    MemoryRetrievalStrategy,
)
from nikola.domain.entities.memory_entry import MemoryEntry
from nikola.domain.entities.memory_query import MemoryQuery
from nikola.domain.value_objects.enums import MemoryType
from nikola.domain.value_objects.memory_id import MemoryId


def _entry_with(
    importance: float, created_at: datetime | None = None, content: str = "x"
) -> MemoryEntry:
    return MemoryEntry(
        id=MemoryId.generate(),
        memory_type=MemoryType.SEMANTIC,
        content=content,
        importance=importance,
        created_at=created_at or datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.mark.unit
class TestImportanceRetrievalStrategyIsAbstract:
    def test_is_subclass_of_memory_retrieval_strategy(self) -> None:
        assert issubclass(ImportanceRetrievalStrategy, MemoryRetrievalStrategy)


@pytest.mark.unit
class TestImportanceRetrievalStrategyOrdering:
    def test_sorts_by_importance_descending(self) -> None:
        strategy = ImportanceRetrievalStrategy()
        entries = [
            _entry_with(0.3, content="low"),
            _entry_with(0.9, content="high"),
            _entry_with(0.6, content="mid"),
        ]
        result = strategy.apply(entries, MemoryQuery())
        assert [e.content for e in result] == ["high", "mid", "low"]

    def test_tiebreaks_by_recency_descending(self) -> None:
        strategy = ImportanceRetrievalStrategy()
        now = datetime.now(UTC)
        older = _entry_with(0.5, created_at=now - timedelta(days=2), content="older")
        newer = _entry_with(0.5, created_at=now, content="newer")
        result = strategy.apply([older, newer], MemoryQuery())
        assert result[0].content == "newer"

    def test_empty_entries_returns_empty(self) -> None:
        result = ImportanceRetrievalStrategy().apply([], MemoryQuery())
        assert result == []


@pytest.mark.unit
class TestImportanceRetrievalStrategyLimit:
    def test_applies_limit_from_query(self) -> None:
        strategy = ImportanceRetrievalStrategy()
        entries = [_entry_with(float(i) / 10) for i in range(8)]
        result = strategy.apply(entries, MemoryQuery(limit=3))
        assert len(result) == 3

    def test_no_limit_returns_all(self) -> None:
        strategy = ImportanceRetrievalStrategy()
        entries = [_entry_with(0.5) for _ in range(5)]
        result = strategy.apply(entries, MemoryQuery())
        assert len(result) == 5

    def test_limit_larger_than_entries_returns_all(self) -> None:
        strategy = ImportanceRetrievalStrategy()
        entries = [_entry_with(0.5) for _ in range(3)]
        result = strategy.apply(entries, MemoryQuery(limit=100))
        assert len(result) == 3

    def test_top_entries_by_importance_are_returned_when_limited(self) -> None:
        strategy = ImportanceRetrievalStrategy()
        entries = [
            _entry_with(0.2, content="lowest"),
            _entry_with(0.9, content="highest"),
            _entry_with(0.6, content="middle"),
        ]
        result = strategy.apply(entries, MemoryQuery(limit=2))
        contents = [e.content for e in result]
        assert "highest" in contents
        assert "middle" in contents
        assert "lowest" not in contents
