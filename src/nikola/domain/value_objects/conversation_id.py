"""`ConversationId` — an immutable, globally unique identifier for a `Conversation`."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

__all__ = ["ConversationId"]


@dataclass(frozen=True, slots=True)
class ConversationId:
    """A unique identifier for a `Conversation`.

    Always construct new identifiers via `ConversationId.generate()`.
    Use the constructor directly only when reconstructing a previously
    generated identifier (e.g. when deserializing from a repository).
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("ConversationId value must not be empty.")

    @classmethod
    def generate(cls) -> ConversationId:
        """Return a new, randomly generated `ConversationId`."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
