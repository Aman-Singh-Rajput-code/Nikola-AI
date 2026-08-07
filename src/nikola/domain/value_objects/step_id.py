"""`StepId` — immutable unique identifier for a `PlanStep`."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

__all__ = ["StepId"]


@dataclass(frozen=True, slots=True)
class StepId:
    """Unique identifier for a PlanStep. Use StepId.generate() for new steps."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("StepId value must not be empty.")

    @classmethod
    def generate(cls) -> StepId:
        """Return a new randomly generated StepId."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
