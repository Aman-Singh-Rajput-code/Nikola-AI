"""`SessionId` — an immutable, globally unique identifier for a `Session`.

See `command_id.py` for the rationale behind modeling each entity's
identifier as its own distinct type rather than a bare `str`/`uuid.UUID`.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

__all__ = ["SessionId"]


@dataclass(frozen=True, slots=True)
class SessionId:
    """A unique identifier for a `Session`.

    Immutable and compared by value: two `SessionId` instances wrapping
    the same string are equal. Always construct new identifiers via
    `SessionId.generate()` rather than calling the constructor with a
    hand-written string, unless reconstructing an identifier that was
    previously generated (e.g. when deserializing).
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("SessionId value must not be empty.")

    @classmethod
    def generate(cls) -> SessionId:
        """Return a new, randomly generated `SessionId`."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
