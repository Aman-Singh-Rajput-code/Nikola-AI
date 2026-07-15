"""`MessageId` — an immutable, globally unique identifier for a `Message`."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

__all__ = ["MessageId"]


@dataclass(frozen=True, slots=True)
class MessageId:
    """A unique identifier for a `Message`.

    Always construct new identifiers via `MessageId.generate()`.
    Use the constructor directly only when reconstructing a previously
    generated identifier (e.g. when deserializing from a repository).
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("MessageId value must not be empty.")

    @classmethod
    def generate(cls) -> MessageId:
        """Return a new, randomly generated `MessageId`."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
