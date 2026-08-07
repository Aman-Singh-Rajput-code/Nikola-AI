"""`PlanningRequest` and `PlanningResult` — PlannerPort boundary objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from nikola.domain.errors.domain_errors import PlanningError

if TYPE_CHECKING:
    from nikola.domain.entities.plan import Plan

__all__ = ["PlanningRequest", "PlanningResult"]


@dataclass(frozen=True, slots=True)
class PlanningRequest:
    """Structured request for a PlannerPort to produce a Plan.

    Attributes:
        goal: The goal to achieve. Must be non-empty.
        context: Optional background information to guide planning.
        constraints: Optional restrictions the plan must respect.
    """

    goal: str
    context: str | None = field(default=None)
    constraints: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.goal.strip():
            raise PlanningError("PlanningRequest.goal must not be empty.")

    @classmethod
    def create(
        cls,
        goal: str,
        *,
        context: str | None = None,
        constraints: list[str] | None = None,
    ) -> PlanningRequest:
        """Construct a PlanningRequest. Raises PlanningError if goal is empty."""
        return cls(
            goal=goal,
            context=context,
            constraints=tuple(constraints) if constraints else (),
        )


@dataclass(frozen=True, slots=True)
class PlanningResult:
    """Output produced by a PlannerPort for a single planning cycle.

    Attributes:
        plan: The Plan produced by the planner.
        confidence: Planner confidence in [0.0, 1.0].
        warnings: Non-fatal issues noticed during planning.
        reasoning_summary: Human-readable explanation of plan rationale.
    """

    plan: Plan
    confidence: float
    warnings: tuple[str, ...] = field(default_factory=tuple)
    reasoning_summary: str = field(default="")

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise PlanningError(
                f"PlanningResult.confidence must be in [0.0, 1.0], got {self.confidence!r}."
            )
