"""`MemoryRepositoryPort` — abstract persistence contract for `MemoryEntry`.

Defined in the domain layer so that application use cases depend only on
this interface, never on a specific storage backend. Sprint 8's sole
implementation is `InMemoryMemoryRepository` in
`nikola.infrastructure.persistence.in_memory`. Future sprints may add
SQLite persistence, vector store adapters (Chroma, FAISS), or cloud-backed
storage as separate adapters — none of those changes will touch this port
or any application code that depends on it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.entities.memory_entry import MemoryEntry
    from nikola.domain.entities.memory_query import MemoryQuery
    from nikola.domain.value_objects.memory_id import MemoryId

__all__ = ["MemoryRepositoryPort"]


class MemoryRepositoryPort(ABC):
    """Abstract persistence interface for `MemoryEntry` aggregates."""

    @abstractmethod
    def save(self, entry: MemoryEntry) -> None:
        """Persist `entry`, creating or updating it as necessary.

        Idempotent: saving an entry that already exists updates it, not
        creates a duplicate.

        Args:
            entry: The memory entry to persist.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, memory_id: MemoryId) -> MemoryEntry | None:
        """Return the entry with `memory_id`, or `None` if absent.

        Args:
            memory_id: The identifier to look up.
        """
        raise NotImplementedError

    @abstractmethod
    def search(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Return all entries matching `query`'s filter criteria.

        Implementations must apply all non-None fields on `query` as
        filters (AND semantics between fields), but are NOT responsible
        for ordering or applying `query.limit` — that is the retrieval
        strategy's job. Returning the full unordered match set lets the
        strategy sort and truncate without the repository needing to know
        the desired ordering.

        Args:
            query: The structured filter describing which entries to return.

        Returns:
            All matching entries in no guaranteed order.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, memory_id: MemoryId) -> None:
        """Remove the entry with `memory_id`; no-op if absent.

        Args:
            memory_id: The identifier of the entry to remove.
        """
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Return the total number of entries currently stored."""
        raise NotImplementedError
