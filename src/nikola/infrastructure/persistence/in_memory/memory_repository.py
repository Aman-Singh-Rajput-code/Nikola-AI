"""`InMemoryMemoryRepository` — dict-backed `MemoryRepositoryPort`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.domain.ports.memory_repository_port import MemoryRepositoryPort

if TYPE_CHECKING:
    from nikola.domain.entities.memory_entry import MemoryEntry
    from nikola.domain.entities.memory_query import MemoryQuery
    from nikola.domain.value_objects.memory_id import MemoryId

__all__ = ["InMemoryMemoryRepository"]


class InMemoryMemoryRepository(MemoryRepositoryPort):
    """In-process, dict-backed memory repository.

    Filtering is performed in Python (no SQL, no vector index). Each
    non-None field on `MemoryQuery` is applied as an AND condition.
    Ordering and `limit` application are the retrieval strategy's
    responsibility, not this class's.
    """

    def __init__(self) -> None:
        self._store: dict[str, MemoryEntry] = {}

    def save(self, entry: MemoryEntry) -> None:
        """Persist `entry`, creating or replacing by id."""
        self._store[entry.id.value] = entry

    def get(self, memory_id: MemoryId) -> MemoryEntry | None:
        """Return the entry with `memory_id`, or `None`."""
        return self._store.get(memory_id.value)

    def search(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Return all entries matching every non-None filter on `query`.

        `query.limit` is intentionally NOT applied here; that is the
        retrieval strategy's responsibility.
        """
        results: list[MemoryEntry] = []
        for entry in self._store.values():
            if query.memory_types is not None and entry.memory_type not in query.memory_types:
                continue
            if query.tags is not None and not entry.has_all_tags(query.tags):
                continue
            if query.min_importance is not None and entry.importance < query.min_importance:
                continue
            if query.created_after is not None and entry.created_at <= query.created_after:
                continue
            if query.created_before is not None and entry.created_at >= query.created_before:
                continue
            results.append(entry)
        return results

    def delete(self, memory_id: MemoryId) -> None:
        """Remove the entry; no-op if absent."""
        self._store.pop(memory_id.value, None)

    def count(self) -> int:
        """Return the total number of entries currently stored."""
        return len(self._store)
