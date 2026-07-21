"""Unit tests for `InMemoryMemoryRepository`."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from nikola.domain.entities.memory_entry import MemoryEntry
from nikola.domain.entities.memory_query import MemoryQuery
from nikola.domain.ports.memory_repository_port import MemoryRepositoryPort
from nikola.domain.value_objects.enums import MemoryType
from nikola.domain.value_objects.memory_id import MemoryId
from nikola.infrastructure.persistence.in_memory.memory_repository import (
    InMemoryMemoryRepository,
)


def _entry(
    memory_type: MemoryType = MemoryType.SEMANTIC,
    content: str = "test",
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
class TestInMemoryMemoryRepositoryIsAPort:
    def test_is_a_memory_repository_port(self) -> None:
        assert isinstance(InMemoryMemoryRepository(), MemoryRepositoryPort)


@pytest.mark.unit
class TestSaveAndGet:
    def test_save_and_get_round_trips(self) -> None:
        repo = InMemoryMemoryRepository()
        entry = _entry()
        repo.save(entry)
        assert repo.get(entry.id) is entry

    def test_get_unknown_id_returns_none(self) -> None:
        repo = InMemoryMemoryRepository()
        assert repo.get(MemoryId.generate()) is None

    def test_save_is_idempotent(self) -> None:
        repo = InMemoryMemoryRepository()
        entry = _entry()
        repo.save(entry)
        repo.save(entry)
        assert repo.count() == 1

    def test_save_updates_existing_entry(self) -> None:
        repo = InMemoryMemoryRepository()
        entry = _entry(importance=0.5)
        repo.save(entry)
        entry.strengthen(0.3)
        repo.save(entry)
        assert repo.get(entry.id).importance == pytest.approx(0.8)  # type: ignore[union-attr]


@pytest.mark.unit
class TestDelete:
    def test_delete_removes_entry(self) -> None:
        repo = InMemoryMemoryRepository()
        entry = _entry()
        repo.save(entry)
        repo.delete(entry.id)
        assert repo.get(entry.id) is None

    def test_delete_unknown_id_is_no_op(self) -> None:
        repo = InMemoryMemoryRepository()
        repo.delete(MemoryId.generate())  # must not raise

    def test_count_decreases_after_delete(self) -> None:
        repo = InMemoryMemoryRepository()
        entry = _entry()
        repo.save(entry)
        assert repo.count() == 1
        repo.delete(entry.id)
        assert repo.count() == 0


@pytest.mark.unit
class TestSearchByType:
    def test_filter_by_single_type(self) -> None:
        repo = InMemoryMemoryRepository()
        repo.save(_entry(memory_type=MemoryType.SEMANTIC, content="fact"))
        repo.save(_entry(memory_type=MemoryType.EPISODIC, content="event"))
        repo.save(_entry(memory_type=MemoryType.WORKING, content="temp"))

        results = repo.search(MemoryQuery(memory_types=frozenset({MemoryType.SEMANTIC})))
        assert len(results) == 1
        assert results[0].memory_type is MemoryType.SEMANTIC

    def test_filter_by_multiple_types(self) -> None:
        repo = InMemoryMemoryRepository()
        repo.save(_entry(memory_type=MemoryType.SEMANTIC, content="a"))
        repo.save(_entry(memory_type=MemoryType.EPISODIC, content="b"))
        repo.save(_entry(memory_type=MemoryType.WORKING, content="c"))

        results = repo.search(
            MemoryQuery(memory_types=frozenset({MemoryType.SEMANTIC, MemoryType.EPISODIC}))
        )
        assert len(results) == 2

    def test_no_type_filter_returns_all(self) -> None:
        repo = InMemoryMemoryRepository()
        for t in MemoryType:
            repo.save(_entry(memory_type=t, content=f"content-{t}"))
        results = repo.search(MemoryQuery())
        assert len(results) == len(list(MemoryType))


@pytest.mark.unit
class TestSearchByTags:
    def test_filter_by_single_tag(self) -> None:
        repo = InMemoryMemoryRepository()
        repo.save(_entry(content="match", tags=frozenset({"python"})))
        repo.save(_entry(content="no match", tags=frozenset({"rust"})))

        results = repo.search(MemoryQuery(tags=frozenset({"python"})))
        assert len(results) == 1
        assert results[0].content == "match"

    def test_filter_by_multiple_tags_requires_all(self) -> None:
        repo = InMemoryMemoryRepository()
        repo.save(_entry(content="both", tags=frozenset({"a", "b"})))
        repo.save(_entry(content="only-a", tags=frozenset({"a"})))

        results = repo.search(MemoryQuery(tags=frozenset({"a", "b"})))
        assert len(results) == 1
        assert results[0].content == "both"

    def test_entry_with_no_tags_does_not_match_tag_filter(self) -> None:
        repo = InMemoryMemoryRepository()
        repo.save(_entry(content="no tags"))
        results = repo.search(MemoryQuery(tags=frozenset({"python"})))
        assert len(results) == 0


@pytest.mark.unit
class TestSearchByImportance:
    def test_min_importance_filter(self) -> None:
        repo = InMemoryMemoryRepository()
        repo.save(_entry(content="low", importance=0.2))
        repo.save(_entry(content="high", importance=0.8))

        results = repo.search(MemoryQuery(min_importance=0.5))
        assert len(results) == 1
        assert results[0].content == "high"

    def test_exactly_at_threshold_is_included(self) -> None:
        repo = InMemoryMemoryRepository()
        repo.save(_entry(content="at threshold", importance=0.5))
        results = repo.search(MemoryQuery(min_importance=0.5))
        assert len(results) == 1


@pytest.mark.unit
class TestSearchByTime:
    def test_created_after_filter(self) -> None:
        repo = InMemoryMemoryRepository()
        early = MemoryEntry(
            id=MemoryId.generate(),
            memory_type=MemoryType.SEMANTIC,
            content="early",
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, tzinfo=UTC),
        )
        late = MemoryEntry(
            id=MemoryId.generate(),
            memory_type=MemoryType.SEMANTIC,
            content="late",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        repo.save(early)
        repo.save(late)

        results = repo.search(MemoryQuery(created_after=datetime(2025, 1, 1, tzinfo=UTC)))
        assert len(results) == 1
        assert results[0].content == "late"

    def test_created_before_filter(self) -> None:
        repo = InMemoryMemoryRepository()
        early = MemoryEntry(
            id=MemoryId.generate(),
            memory_type=MemoryType.SEMANTIC,
            content="early",
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, tzinfo=UTC),
        )
        repo.save(early)

        results = repo.search(MemoryQuery(created_before=datetime(2025, 1, 1, tzinfo=UTC)))
        assert len(results) == 1

    def test_combined_time_range(self) -> None:
        repo = InMemoryMemoryRepository()
        for year, label in [(2023, "too early"), (2025, "in range"), (2027, "too late")]:
            repo.save(
                MemoryEntry(
                    id=MemoryId.generate(),
                    memory_type=MemoryType.SEMANTIC,
                    content=label,
                    created_at=datetime(year, 6, 1, tzinfo=UTC),
                    updated_at=datetime(year, 6, 1, tzinfo=UTC),
                )
            )
        results = repo.search(
            MemoryQuery(
                created_after=datetime(2024, 1, 1, tzinfo=UTC),
                created_before=datetime(2026, 1, 1, tzinfo=UTC),
            )
        )
        assert len(results) == 1
        assert results[0].content == "in range"


@pytest.mark.unit
class TestSearchLimitNotApplied:
    def test_repository_does_not_apply_limit(self) -> None:
        """Limit is the retrieval strategy's responsibility, not the repo's."""
        repo = InMemoryMemoryRepository()
        for i in range(5):
            repo.save(_entry(content=f"entry {i}"))
        results = repo.search(MemoryQuery(limit=2))
        # Repository must return all 5, ignoring the limit
        assert len(results) == 5
