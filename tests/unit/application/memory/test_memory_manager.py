"""Unit tests for `MemoryManager`."""

from __future__ import annotations

import pytest

from nikola.application.memory.memory_manager import MemoryManager
from nikola.application.memory.memory_retrieval_strategy import ImportanceRetrievalStrategy
from nikola.application.memory.memory_service import MemoryService
from nikola.domain.entities.memory_entry import MemoryEntry
from nikola.domain.entities.memory_query import MemoryQuery, MemoryResult
from nikola.domain.value_objects.enums import MemoryType
from nikola.infrastructure.persistence.in_memory.memory_repository import (
    InMemoryMemoryRepository,
)


def _manager() -> MemoryManager:
    repo = InMemoryMemoryRepository()
    strategy = ImportanceRetrievalStrategy()
    service = MemoryService(repository=repo, retrieval_strategy=strategy)
    return MemoryManager(service=service)


@pytest.mark.unit
class TestMemoryManagerRememberFact:
    def test_stores_as_semantic_type(self) -> None:
        mgr = _manager()
        entry = mgr.remember_fact("User's name is Aman")
        assert entry.memory_type is MemoryType.SEMANTIC

    def test_default_importance_is_0_6(self) -> None:
        mgr = _manager()
        entry = mgr.remember_fact("some fact")
        assert entry.importance == pytest.approx(0.6)

    def test_accepts_tags(self) -> None:
        mgr = _manager()
        entry = mgr.remember_fact("a fact", tags=frozenset({"user", "identity"}))
        assert "user" in entry.tags

    def test_returns_memory_entry(self) -> None:
        assert isinstance(_manager().remember_fact("fact"), MemoryEntry)


@pytest.mark.unit
class TestMemoryManagerRecordEpisode:
    def test_stores_as_episodic_type(self) -> None:
        mgr = _manager()
        entry = mgr.record_episode("Deployed to production")
        assert entry.memory_type is MemoryType.EPISODIC

    def test_default_importance_is_0_5(self) -> None:
        mgr = _manager()
        entry = mgr.record_episode("an event")
        assert entry.importance == pytest.approx(0.5)


@pytest.mark.unit
class TestMemoryManagerNoteProcedure:
    def test_stores_as_procedural_type(self) -> None:
        mgr = _manager()
        entry = mgr.note_procedure("User prefers Docker")
        assert entry.memory_type is MemoryType.PROCEDURAL

    def test_default_importance_is_0_7(self) -> None:
        mgr = _manager()
        entry = mgr.note_procedure("a preference")
        assert entry.importance == pytest.approx(0.7)


@pytest.mark.unit
class TestMemoryManagerSetWorkingMemory:
    def test_stores_as_working_type(self) -> None:
        mgr = _manager()
        entry = mgr.set_working_memory("current task context")
        assert entry.memory_type is MemoryType.WORKING

    def test_default_importance_is_0_4(self) -> None:
        mgr = _manager()
        entry = mgr.set_working_memory("scratchpad")
        assert entry.importance == pytest.approx(0.4)


@pytest.mark.unit
class TestMemoryManagerRecall:
    def test_returns_memory_result(self) -> None:
        mgr = _manager()
        mgr.remember_fact("fact")
        result = mgr.recall(MemoryQuery())
        assert isinstance(result, MemoryResult)

    def test_filters_by_type(self) -> None:
        mgr = _manager()
        mgr.remember_fact("fact")
        mgr.record_episode("event")
        result = mgr.recall(MemoryQuery(memory_types=frozenset({MemoryType.SEMANTIC})))
        assert len(result.entries) == 1
        assert result.entries[0].memory_type is MemoryType.SEMANTIC

    def test_filters_by_tags(self) -> None:
        mgr = _manager()
        mgr.remember_fact("tagged", tags=frozenset({"python"}))
        mgr.remember_fact("untagged")
        result = mgr.recall(MemoryQuery(tags=frozenset({"python"})))
        assert len(result.entries) == 1

    def test_limit_applied(self) -> None:
        mgr = _manager()
        for i in range(5):
            mgr.remember_fact(f"fact {i}")
        result = mgr.recall(MemoryQuery(limit=2))
        assert len(result.entries) == 2

    def test_ordered_by_importance(self) -> None:
        mgr = _manager()
        mgr.remember_fact("low", importance=0.2)
        mgr.remember_fact("high", importance=0.9)
        result = mgr.recall(MemoryQuery())
        assert result.entries[0].content == "high"


@pytest.mark.unit
class TestMemoryManagerStrengthen:
    def test_strengthen_increases_importance(self) -> None:
        mgr = _manager()
        entry = mgr.remember_fact("fact")
        original = entry.importance
        updated = mgr.strengthen(entry.id, delta=0.2)
        assert updated.importance == pytest.approx(original + 0.2)

    def test_strengthen_default_delta_is_0_1(self) -> None:
        mgr = _manager()
        entry = mgr.remember_fact("fact")
        original = entry.importance
        updated = mgr.strengthen(entry.id)
        assert updated.importance == pytest.approx(original + 0.1)


@pytest.mark.unit
class TestMemoryManagerForget:
    def test_forget_removes_entry_from_store(self) -> None:
        mgr = _manager()
        entry = mgr.remember_fact("fact")
        mgr.forget(entry.id)
        result = mgr.recall(MemoryQuery())
        assert len(result.entries) == 0
