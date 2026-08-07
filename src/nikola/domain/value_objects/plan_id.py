"""`PlanId` — immutable unique identifier for a `Plan`."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

__all__ = ["PlanId"]


@dataclass(frozen=True, slots=True)
class PlanId:
    """Unique identifier for a Plan. Use PlanId.generate() for new plans."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("PlanId value must not be empty.")

    @classmethod
    def generate(cls) -> PlanId:
        """Return a new randomly generated PlanId."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
