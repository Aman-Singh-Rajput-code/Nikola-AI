"""Unit tests for `MemoryService`."""

from __future__ import annotations

import pytest

from nikola.application.memory.memory_retrieval_strategy import ImportanceRetrievalStrategy
from nikola.application.memory.memory_service import MemoryService
from nikola.domain.entities.memory_entry import MemoryEntry
from nikola.domain.entities.memory_query import MemoryQuery
from nikola.domain.errors import MemoryError
from nikola.domain.value_objects.enums import MemoryType
from nikola.domain.value_objects.memory_id import MemoryId
from nikola.infrastructure.persistence.in_memory.memory_repository import (
    InMemoryMemoryRepository,
)


def _service() -> tuple[MemoryService, InMemoryMemoryRepository]:
    repo = InMemoryMemoryRepository()
    strategy = ImportanceRetrievalStrategy()
    return MemoryService(repository=repo, retrieval_strategy=strategy), repo


@pytest.mark.unit
class TestMemoryServiceStore:
    def test_store_returns_a_memory_entry(self) -> None:
        svc, _ = _service()
        entry = svc.store(memory_type=MemoryType.SEMANTIC, content="a fact")
        assert isinstance(entry, MemoryEntry)

    def test_store_persists_entry(self) -> None:
        svc, repo = _service()
        entry = svc.store(memory_type=MemoryType.SEMANTIC, content="a fact")
        assert repo.get(entry.id) is entry

    def test_store_with_all_fields(self) -> None:
        svc, _ = _service()
        entry = svc.store(
            memory_type=MemoryType.PROCEDURAL,
            content="user prefers docker",
            importance=0.8,
            tags=frozenset({"docker", "deployment"}),
            metadata={"source": "conversation_123"},
        )
        assert entry.importance == 0.8
        assert "docker" in entry.tags
        assert entry.metadata["source"] == "conversation_123"

    def test_store_empty_content_raises(self) -> None:
        svc, _ = _service()
        with pytest.raises(MemoryError):
            svc.store(memory_type=MemoryType.SEMANTIC, content="")


@pytest.mark.unit
class TestMemoryServiceGet:
    def test_get_returns_stored_entry(self) -> None:
        svc, _ = _service()
        entry = svc.store(memory_type=MemoryType.SEMANTIC, content="fact")
        assert svc.get(entry.id) is entry

    def test_get_unknown_id_raises_memory_error(self) -> None:
        svc, _ = _service()
        with pytest.raises(MemoryError, match="was not found"):
            svc.get(MemoryId.generate())


@pytest.mark.unit
class TestMemoryServiceRetrieve:
    def test_retrieve_returns_memory_result(self) -> None:
        from nikola.domain.entities.memory_query import MemoryResult

        svc, _ = _service()
        svc.store(memory_type=MemoryType.SEMANTIC, content="fact")
        result = svc.retrieve(MemoryQuery())
        assert isinstance(result, MemoryResult)

    def test_retrieve_orders_by_importance(self) -> None:
        svc, _ = _service()
        svc.store(memory_type=MemoryType.SEMANTIC, content="low", importance=0.2)
        svc.store(memory_type=MemoryType.SEMANTIC, content="high", importance=0.9)
        result = svc.retrieve(MemoryQuery())
        assert result.entries[0].content == "high"

    def test_retrieve_total_found_reflects_pre_limit_count(self) -> None:
        svc, _ = _service()
        for i in range(5):
            svc.store(memory_type=MemoryType.SEMANTIC, content=f"entry {i}")
        result = svc.retrieve(MemoryQuery(limit=2))
        assert result.total_found == 5
        assert len(result.entries) == 2

    def test_retrieve_filters_by_type(self) -> None:
        svc, _ = _service()
        svc.store(memory_type=MemoryType.SEMANTIC, content="fact")
        svc.store(memory_type=MemoryType.EPISODIC, content="event")
        result = svc.retrieve(MemoryQuery(memory_types=frozenset({MemoryType.SEMANTIC})))
        assert len(result.entries) == 1
        assert result.entries[0].memory_type is MemoryType.SEMANTIC

    def test_retrieve_empty_store_returns_empty_result(self) -> None:
        svc, _ = _service()
        result = svc.retrieve(MemoryQuery())
        assert result.entries == ()
        assert result.total_found == 0


@pytest.mark.unit
class TestMemoryServiceStrengthen:
    def test_strengthen_updates_importance(self) -> None:
        svc, _ = _service()
        entry = svc.store(memory_type=MemoryType.SEMANTIC, content="fact", importance=0.5)
        updated = svc.strengthen(entry.id, delta=0.2)
        assert updated.importance == pytest.approx(0.7)

    def test_strengthen_persists_update(self) -> None:
        svc, repo = _service()
        entry = svc.store(memory_type=MemoryType.SEMANTIC, content="fact", importance=0.5)
        svc.strengthen(entry.id, delta=0.2)
        persisted = repo.get(entry.id)
        assert persisted is not None
        assert persisted.importance == pytest.approx(0.7)

    def test_strengthen_unknown_id_raises(self) -> None:
        svc, _ = _service()
        with pytest.raises(MemoryError):
            svc.strengthen(MemoryId.generate())


@pytest.mark.unit
class TestMemoryServiceForget:
    def test_forget_removes_entry(self) -> None:
        svc, repo = _service()
        entry = svc.store(memory_type=MemoryType.SEMANTIC, content="fact")
        svc.forget(entry.id)
        assert repo.get(entry.id) is None

    def test_forget_unknown_id_is_no_op(self) -> None:
        svc, _ = _service()
        svc.forget(MemoryId.generate())  # must not raise
