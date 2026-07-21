"""`MemoryService` — primary use-case service for all memory operations.

Owns the coordination between the repository (persistence) and the retrieval
strategy (ordering policy). All public methods are atomic from the caller's
perspective: they either succeed fully or raise a `MemoryError`.

`MemoryService` deliberately does NOT:
- Call the Brain.
- Compute embeddings or similarity scores.
- Access databases or network resources.
- Import anything from `infrastructure/`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.domain.entities.memory_entry import MemoryEntry
from nikola.domain.entities.memory_query import MemoryQuery, MemoryResult
from nikola.domain.errors.domain_errors import MemoryError

if TYPE_CHECKING:
    from nikola.application.memory.memory_retrieval_strategy import MemoryRetrievalStrategy
    from nikola.domain.ports.memory_repository_port import MemoryRepositoryPort
    from nikola.domain.value_objects.enums import MemoryType
    from nikola.domain.value_objects.memory_id import MemoryId

__all__ = ["MemoryService"]


class MemoryService:
    """Orchestrates memory lifecycle: storage, retrieval, reinforcement, forgetting.

    Depends on:
    - `MemoryRepositoryPort` for persistence (injected; swappable).
    - `MemoryRetrievalStrategy` for ordering and limiting results (injected).
    """

    def __init__(
        self,
        repository: MemoryRepositoryPort,
        retrieval_strategy: MemoryRetrievalStrategy,
    ) -> None:
        self._repository = repository
        self._strategy = retrieval_strategy

    def store(
        self,
        *,
        memory_type: MemoryType,
        content: str,
        importance: float = 0.5,
        tags: frozenset[str] | None = None,
        metadata: dict[str, object] | None = None,
    ) -> MemoryEntry:
        """Create and persist a new memory entry.

        Args:
            memory_type: The cognitive category for this memory.
            content: The information to remember. Must be non-empty.
            importance: Relevance score in [0.0, 1.0]. Defaults to 0.5.
            tags: Optional set of string labels for filtering.
            metadata: Optional key-value pairs for extensibility.

        Returns:
            The newly created and persisted `MemoryEntry`.

        Raises:
            MemoryError: If `content` is empty or `importance` is out of range.
        """
        entry = MemoryEntry.create(
            memory_type=memory_type,
            content=content,
            importance=importance,
            tags=tags,
            metadata=metadata,
        )
        self._repository.save(entry)
        return entry

    def retrieve(self, query: MemoryQuery) -> MemoryResult:
        """Retrieve memory entries matching `query`.

        Delegates filtering to the repository and ordering/limiting to the
        retrieval strategy. The two steps are separate so each concern is
        independently testable and replaceable.

        Args:
            query: Structured filter describing which entries to return.

        Returns:
            A `MemoryResult` carrying the ordered entries, total count
            before limiting, and the query for audit.
        """
        matched = self._repository.search(query)
        total_found = len(matched)
        ordered = self._strategy.apply(matched, query)
        return MemoryResult(
            entries=tuple(ordered),
            total_found=total_found,
            query=query,
        )

    def get(self, memory_id: MemoryId) -> MemoryEntry:
        """Return the entry with `memory_id`.

        Args:
            memory_id: The identifier to look up.

        Returns:
            The matching `MemoryEntry`.

        Raises:
            MemoryError: If no entry with `memory_id` exists.
        """
        entry = self._repository.get(memory_id)
        if entry is None:
            raise MemoryError(f"Memory entry '{memory_id}' was not found.")
        return entry

    def strengthen(self, memory_id: MemoryId, delta: float = 0.1) -> MemoryEntry:
        """Reinforce an existing memory entry by increasing its importance.

        Fetches the entry, calls `entry.strengthen(delta)`, and persists the
        updated entry. The importance is clamped to [0.0, 1.0] by the entity.

        Args:
            memory_id: The entry to reinforce.
            delta: Amount to add to the entry's importance. Positive to
                strengthen, negative to weaken. Clamped so the result
                stays within [0.0, 1.0].

        Returns:
            The updated `MemoryEntry` with its new importance and
            `updated_at` timestamp.

        Raises:
            MemoryError: If no entry with `memory_id` exists.
        """
        entry = self.get(memory_id)
        entry.strengthen(delta)
        self._repository.save(entry)
        return entry

    def forget(self, memory_id: MemoryId) -> None:
        """Permanently remove a memory entry.

        Args:
            memory_id: The entry to remove.

        Note:
            Silently succeeds if the entry does not exist, consistent with
            the repository's idempotent `delete()` contract.
        """
        self._repository.delete(memory_id)
