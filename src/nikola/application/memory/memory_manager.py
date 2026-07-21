"""`MemoryManager` — high-level coordinator for memory operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.application.memory.memory_service import MemoryService  # noqa: TC001
from nikola.domain.value_objects.enums import MemoryType

if TYPE_CHECKING:
    from nikola.domain.entities.memory_entry import MemoryEntry
    from nikola.domain.entities.memory_query import MemoryQuery, MemoryResult
    from nikola.domain.value_objects.memory_id import MemoryId

__all__ = ["MemoryManager"]

_DEFAULT_FACT_IMPORTANCE: float = 0.6
_DEFAULT_EPISODE_IMPORTANCE: float = 0.5
_DEFAULT_PROCEDURE_IMPORTANCE: float = 0.7
_DEFAULT_WORKING_IMPORTANCE: float = 0.4


class MemoryManager:
    """High-level memory API for Orchestrator and Planner use.

    Delegates all persistence and retrieval to `MemoryService`. Adds
    type-specific store methods and sensible importance defaults for each
    memory type, so callers do not need to know the taxonomy's details.
    """

    def __init__(self, service: MemoryService) -> None:
        self._service = service

    def remember_fact(
        self,
        content: str,
        *,
        tags: frozenset[str] | None = None,
        importance: float = _DEFAULT_FACT_IMPORTANCE,
        metadata: dict[str, object] | None = None,
    ) -> MemoryEntry:
        """Store a semantic (factual) memory.

        Use for persistent facts about the user or the world:
        "The user's name is Aman.", "The project uses Python 3.12."
        """
        return self._service.store(
            memory_type=MemoryType.SEMANTIC,
            content=content,
            importance=importance,
            tags=tags,
            metadata=metadata,
        )

    def record_episode(
        self,
        content: str,
        *,
        tags: frozenset[str] | None = None,
        importance: float = _DEFAULT_EPISODE_IMPORTANCE,
        metadata: dict[str, object] | None = None,
    ) -> MemoryEntry:
        """Store an episodic (event-based) memory.

        Use for records of specific past interactions:
        "On 2026-07-01, helped user deploy nikola-ai to production."
        """
        return self._service.store(
            memory_type=MemoryType.EPISODIC,
            content=content,
            importance=importance,
            tags=tags,
            metadata=metadata,
        )

    def note_procedure(
        self,
        content: str,
        *,
        tags: frozenset[str] | None = None,
        importance: float = _DEFAULT_PROCEDURE_IMPORTANCE,
        metadata: dict[str, object] | None = None,
    ) -> MemoryEntry:
        """Store a procedural (know-how) memory.

        Use for learned preferences and patterns:
        "User prefers GitHub Actions for CI/CD, not Jenkins."
        """
        return self._service.store(
            memory_type=MemoryType.PROCEDURAL,
            content=content,
            importance=importance,
            tags=tags,
            metadata=metadata,
        )

    def set_working_memory(
        self,
        content: str,
        *,
        tags: frozenset[str] | None = None,
        metadata: dict[str, object] | None = None,
    ) -> MemoryEntry:
        """Store a working-memory entry for the current task context."""
        return self._service.store(
            memory_type=MemoryType.WORKING,
            content=content,
            importance=_DEFAULT_WORKING_IMPORTANCE,
            tags=tags,
            metadata=metadata,
        )

    def recall(self, query: MemoryQuery) -> MemoryResult:
        """Query the memory store with a structured filter."""
        return self._service.retrieve(query)

    def strengthen(self, memory_id: MemoryId, delta: float = 0.1) -> MemoryEntry:
        """Reinforce a memory entry after it proves useful."""
        return self._service.strengthen(memory_id, delta)

    def forget(self, memory_id: MemoryId) -> None:
        """Permanently remove a memory entry."""
        self._service.forget(memory_id)
