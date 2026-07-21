"""`MemoryId` — an immutable, globally unique identifier for a `MemoryEntry`.

Modeled as its own type so it cannot be silently substituted for any other
identifier type (`ConversationId`, `MessageId`, `TaskId`, etc.) in
type-checked code. See `nikola.domain.value_objects.command_id` for the
full rationale behind per-entity typed identifiers.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

__all__ = ["MemoryId"]


@dataclass(frozen=True, slots=True)
class MemoryId:
    """A unique identifier for a `MemoryEntry`.

    Always construct new identifiers via `MemoryId.generate()`.
    Use the constructor directly only when reconstructing a previously
    generated identifier (e.g. when loading from a repository).
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("MemoryId value must not be empty.")

    @classmethod
    def generate(cls) -> MemoryId:
        """Return a new, randomly generated `MemoryId`."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
