"""`CommandId` — an immutable, globally unique identifier for a `Command`.

Modeled as its own type (rather than a bare `str` or `uuid.UUID`) so that a
`CommandId` cannot be silently substituted for a `TaskId` or `SessionId`
elsewhere in the codebase — passing the wrong kind of identifier becomes a
type error MyPy catches at the call site, instead of a confusing runtime
bug discovered much later.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

__all__ = ["CommandId"]


@dataclass(frozen=True, slots=True)
class CommandId:
    """A unique identifier for a `Command`.

    Immutable and compared by value: two `CommandId` instances wrapping
    the same string are equal. Always construct new identifiers via
    `CommandId.generate()` rather than calling the constructor with a
    hand-written string, unless reconstructing an identifier that was
    previously generated (e.g. when deserializing).
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("CommandId value must not be empty.")

    @classmethod
    def generate(cls) -> CommandId:
        """Return a new, randomly generated `CommandId`."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
