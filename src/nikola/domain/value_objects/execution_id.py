"""`ExecutionId` — an immutable, globally unique identifier for an `Execution`."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

__all__ = ["ExecutionId"]


@dataclass(frozen=True, slots=True)
class ExecutionId:
    """A unique identifier for an `Execution`.

    Always construct new identifiers via `ExecutionId.generate()`.
    Use the constructor directly only when reconstructing a previously
    generated identifier (e.g. when loading from a repository).
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("ExecutionId value must not be empty.")

    @classmethod
    def generate(cls) -> ExecutionId:
        """Return a new, randomly generated `ExecutionId`."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
