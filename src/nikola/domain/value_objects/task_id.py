"""`TaskId` — an immutable, globally unique identifier for a `Task`.

See `command_id.py` for the rationale behind modeling each entity's
identifier as its own distinct type rather than a bare `str`/`uuid.UUID`.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

__all__ = ["TaskId"]


@dataclass(frozen=True, slots=True)
class TaskId:
    """A unique identifier for a `Task`.

    Immutable and compared by value: two `TaskId` instances wrapping the
    same string are equal. Always construct new identifiers via
    `TaskId.generate()` rather than calling the constructor with a
    hand-written string, unless reconstructing an identifier that was
    previously generated (e.g. when deserializing).
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("TaskId value must not be empty.")

    @classmethod
    def generate(cls) -> TaskId:
        """Return a new, randomly generated `TaskId`."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
