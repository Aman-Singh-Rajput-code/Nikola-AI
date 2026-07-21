"""`MemoryQuery` and `MemoryResult` — structured query input and output.

Keeping these as domain entities (not application-layer DTOs) means the
repository port, the retrieval strategy, and any future storage adapter
all use the same well-typed, validated query shape without needing
adapter-specific translation objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from nikola.domain.entities.memory_entry import MemoryEntry
    from nikola.domain.value_objects.enums import MemoryType

__all__ = ["MemoryQuery", "MemoryResult"]


@dataclass(frozen=True, slots=True)
class MemoryQuery:
    """A structured filter for querying the memory store.

    Every field is optional. An empty `MemoryQuery()` (all defaults) matches
    every entry in the store and returns them up to `limit` (or all of them
    if `limit` is `None`).

    Attributes:
        memory_types: If set, only entries whose `memory_type` is in this
            set are returned. `None` means "any type".
        tags: If set, only entries that possess *all* of these tags are
            returned (AND semantics — stricter, more predictable than OR).
            `None` means "any tags" (no tag filter).
        min_importance: If set, only entries with `importance >=
            min_importance` are returned. `None` means no lower bound.
        created_after: If set, only entries created strictly after this
            timestamp are returned. `None` means no lower time bound.
        created_before: If set, only entries created strictly before this
            timestamp are returned. `None` means no upper time bound.
        limit: If set, at most this many entries are returned after all
            other filters and ordering are applied. `None` means no cap.
    """

    memory_types: frozenset[MemoryType] | None = field(default=None)
    tags: frozenset[str] | None = field(default=None)
    min_importance: float | None = field(default=None)
    created_after: datetime | None = field(default=None)
    created_before: datetime | None = field(default=None)
    limit: int | None = field(default=None)


@dataclass(frozen=True, slots=True)
class MemoryResult:
    """The structured output of a memory query.

    Attributes:
        entries: The matching `MemoryEntry` objects, already ordered and
            limited per the query and retrieval strategy.
        total_found: The total number of entries that matched all filters
            *before* `query.limit` was applied. Useful for pagination
            metadata even though Sprint 8 does not implement pagination.
        query: The `MemoryQuery` that produced this result, included for
            audit and debugging.
    """

    entries: tuple[MemoryEntry, ...]
    total_found: int
    query: MemoryQuery
