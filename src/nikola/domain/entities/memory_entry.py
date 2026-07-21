"""`MemoryEntry` — the core unit of information stored in Nikola AI's memory.

A `MemoryEntry` is not immutable in the way `Message` or `Command` are,
because memory is specifically designed to *evolve*: importance scores are
updated when a memory is reinforced; `updated_at` tracks that reinforcement.
However, `content` and `memory_type` are fixed at creation — what something
is and what it says don't change, only how important it is.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from nikola.domain.errors.domain_errors import MemoryError
from nikola.domain.value_objects.memory_id import MemoryId

if TYPE_CHECKING:
    from nikola.domain.value_objects.enums import MemoryType

__all__ = ["MemoryEntry"]

_MIN_IMPORTANCE: float = 0.0
_MAX_IMPORTANCE: float = 1.0
_DEFAULT_IMPORTANCE: float = 0.5


@dataclass(slots=True)
class MemoryEntry:
    """A single unit of information stored in Nikola AI's memory system.

    Attributes:
        id: The entry's unique identifier.
        memory_type: The cognitive category this entry belongs to —
            WORKING, EPISODIC, SEMANTIC, or PROCEDURAL.
        content: The actual remembered information. Non-empty string.
        created_at: When this memory was first formed, in UTC. Immutable.
        updated_at: When this memory was last reinforced or updated.
            Updated by `strengthen()`.
        importance: A [0.0, 1.0] relevance score. Higher values cause
            this entry to appear first in importance-ranked retrieval.
            Defaults to 0.5 (neutral).
        tags: An immutable set of string labels for category-based
            filtering (e.g. `{"python", "deployment"}`).
        metadata: Arbitrary key-value pairs for extensibility — e.g.
            the source conversation_id, a tool name, a confidence score.
            Not used for filtering in Sprint 8, but carried through for
            future use.

    Raises:
        MemoryError: If `content` is empty, or if `importance` is outside
            [0.0, 1.0].
    """

    id: MemoryId
    memory_type: MemoryType
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    importance: float = field(default=_DEFAULT_IMPORTANCE)
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise MemoryError("MemoryEntry.content must not be empty.")
        _validate_importance(self.importance)

    @classmethod
    def create(
        cls,
        *,
        memory_type: MemoryType,
        content: str,
        importance: float = _DEFAULT_IMPORTANCE,
        tags: frozenset[str] | None = None,
        metadata: dict[str, object] | None = None,
    ) -> MemoryEntry:
        """Construct a new `MemoryEntry` with a freshly generated `MemoryId`.

        Args:
            memory_type: The cognitive category for this entry.
            content: The remembered information. Must be non-empty.
            importance: Relevance score in [0.0, 1.0]. Defaults to 0.5.
            tags: Optional set of labels for filtering.
            metadata: Optional key-value pairs for extensibility.

        Returns:
            A new `MemoryEntry`.

        Raises:
            MemoryError: If `content` is empty or `importance` is out of range.
        """
        return cls(
            id=MemoryId.generate(),
            memory_type=memory_type,
            content=content,
            importance=importance,
            tags=tags if tags is not None else frozenset(),
            metadata=metadata if metadata is not None else {},
        )

    def strengthen(self, delta: float) -> None:
        """Increase this entry's importance by `delta`, clamped to [0.0, 1.0].

        Called when a memory is recalled and confirmed relevant — making it
        more likely to appear at the top of future retrieval results.

        Args:
            delta: The amount to add. May be negative to weaken a memory.
                The result is clamped to [0.0, 1.0], never going outside
                the valid range.
        """
        self.importance = max(_MIN_IMPORTANCE, min(_MAX_IMPORTANCE, self.importance + delta))
        self.updated_at = datetime.now(UTC)

    def has_all_tags(self, required_tags: frozenset[str]) -> bool:
        """Return True if this entry contains all of `required_tags`.

        Args:
            required_tags: Tags that must all be present. An empty set
                always returns True (vacuous truth).
        """
        return required_tags.issubset(self.tags)


def _validate_importance(value: float) -> None:
    if not (_MIN_IMPORTANCE <= value <= _MAX_IMPORTANCE):
        raise MemoryError(f"MemoryEntry.importance must be in [0.0, 1.0], got {value!r}.")
