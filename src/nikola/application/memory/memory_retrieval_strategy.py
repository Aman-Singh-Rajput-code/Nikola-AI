"""`MemoryRetrievalStrategy` — application-layer ordering and limiting policy.

The repository answers "which entries match these filters?" The retrieval
strategy answers "in what order, and how many?" Separating these concerns
means future sprints can introduce a `RecencyRetrievalStrategy` or a
`SemanticRelevanceStrategy` (once embeddings exist) without touching the
repository, the service, or each other.

`ImportanceRetrievalStrategy` is Sprint 8's sole concrete implementation:
sort by `importance` descending, break ties by `created_at` descending,
then apply `query.limit` if set.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.entities.memory_entry import MemoryEntry
    from nikola.domain.entities.memory_query import MemoryQuery

__all__ = ["MemoryRetrievalStrategy", "ImportanceRetrievalStrategy"]


class MemoryRetrievalStrategy(ABC):
    """Abstract application-layer policy for ordering and limiting memory results.

    Receives the full list of filter-matched entries from the repository and
    returns an ordered, optionally-limited subset according to its strategy.
    Implementations must be pure (no I/O, no side effects) so they can be
    tested in isolation.
    """

    @abstractmethod
    def apply(self, entries: list[MemoryEntry], query: MemoryQuery) -> list[MemoryEntry]:
        """Order `entries` and apply `query.limit`.

        Args:
            entries: All entries that passed the repository's filter step.
                May be empty.
            query: The original query — used for `limit` and may carry
                other hints a concrete strategy chooses to act on.

        Returns:
            An ordered list of `MemoryEntry` objects, truncated to
            `query.limit` entries if `limit` is not `None`.
        """
        raise NotImplementedError


class ImportanceRetrievalStrategy(MemoryRetrievalStrategy):
    """Orders memories by importance (descending), then recency (descending).

    Primary sort key: `importance` — higher scores appear first, so the
    most relevant memories are recalled first.

    Tiebreaker: `created_at` — among entries with identical importance,
    more recent memories appear first on the assumption that recency
    correlates with relevance when importance alone cannot distinguish.

    After ordering, applies `query.limit` if set.
    """

    def apply(self, entries: list[MemoryEntry], query: MemoryQuery) -> list[MemoryEntry]:
        """Sort by importance desc, created_at desc; apply limit.

        Args:
            entries: Unordered, filter-matched entries from the repository.
            query: Used solely for `query.limit` in this implementation.

        Returns:
            Ordered and optionally-limited entries.
        """
        ordered = sorted(
            entries,
            key=lambda e: (e.importance, e.created_at),
            reverse=True,
        )
        if query.limit is not None:
            return ordered[: query.limit]
        return ordered
