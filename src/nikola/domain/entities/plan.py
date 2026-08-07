"""`Plan` — an ordered collection of `PlanStep`s produced by a `PlannerPort`."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from nikola.domain.errors.domain_errors import PlanningError
from nikola.domain.value_objects.enums import PlanStatus, StepStatus
from nikola.domain.value_objects.plan_id import PlanId

if TYPE_CHECKING:
    from nikola.domain.entities.plan_step import PlanStep

__all__ = ["Plan"]


@dataclass(slots=True)
class Plan:
    """An ordered sequence of PlanSteps for achieving a goal.

    Attributes:
        id: Unique identifier.
        goal: The original goal string this plan was created to achieve.
        status: Lifecycle state — PENDING at creation.
        created_at: When created, in UTC.
        updated_at: When last mutated, in UTC.
    """

    id: PlanId
    goal: str
    status: PlanStatus = field(default=PlanStatus.PENDING)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _steps: list[PlanStep] = field(default_factory=list, repr=False)

    @classmethod
    def create(cls, *, goal: str) -> Plan:
        """Construct a new empty PENDING Plan. Raises PlanningError if goal is empty."""
        if not goal.strip():
            raise PlanningError("Plan goal must not be empty.")
        return cls(id=PlanId.generate(), goal=goal)

    @property
    def steps(self) -> tuple[PlanStep, ...]:
        """All steps sorted by order ascending, as an immutable tuple."""
        return tuple(sorted(self._steps, key=lambda s: s.order))

    @property
    def step_count(self) -> int:
        """Number of steps in this plan."""
        return len(self._steps)

    @property
    def is_empty(self) -> bool:
        """Whether this plan has no steps."""
        return len(self._steps) == 0

    @property
    def estimated_duration_seconds(self) -> int | None:
        """Sum of all step durations, or None if any step has no estimate."""
        total = 0
        for step in self._steps:
            if step.estimated_duration_seconds is None:
                return None
            total += step.estimated_duration_seconds
        return total

    def add_step(self, step: PlanStep) -> None:
        """Append a step (only valid while PENDING). Raises PlanningError otherwise."""
        if self.status is not PlanStatus.PENDING:
            raise PlanningError(
                f"Cannot add steps to a plan with status '{self.status}'. "
                "Steps may only be added while the plan is PENDING."
            )
        self._steps.append(step)
        self.updated_at = datetime.now(UTC)

    def start(self) -> None:
        """Transition PENDING -> IN_PROGRESS. Raises PlanningError if invalid."""
        if self.status is not PlanStatus.PENDING:
            raise PlanningError(
                f"Cannot start a plan with status '{self.status}'. "
                "Only PENDING plans can be started."
            )
        if self.is_empty:
            raise PlanningError("Cannot start an empty plan with no steps.")
        self.status = PlanStatus.IN_PROGRESS
        self.updated_at = datetime.now(UTC)

    def complete(self) -> None:
        """Transition IN_PROGRESS -> COMPLETED. Raises PlanningError if invalid."""
        if self.status is not PlanStatus.IN_PROGRESS:
            raise PlanningError(
                f"Cannot complete a plan with status '{self.status}'. "
                "Only IN_PROGRESS plans can be completed."
            )
        self.status = PlanStatus.COMPLETED
        self.updated_at = datetime.now(UTC)

    def fail(self, reason: str = "") -> None:
        """Transition IN_PROGRESS -> FAILED. Raises PlanningError if invalid."""
        _ = reason  # reserved for future use by the execution engine
        if self.status is not PlanStatus.IN_PROGRESS:
            raise PlanningError(
                f"Cannot fail a plan with status '{self.status}'. "
                "Only IN_PROGRESS plans can be failed."
            )
        self.status = PlanStatus.FAILED
        self.updated_at = datetime.now(UTC)

    def cancel(self) -> None:
        """Transition to CANCELLED from PENDING or IN_PROGRESS."""
        if self.status in (PlanStatus.COMPLETED, PlanStatus.FAILED, PlanStatus.CANCELLED):
            raise PlanningError(f"Cannot cancel a plan already in terminal status '{self.status}'.")
        self.status = PlanStatus.CANCELLED
        self.updated_at = datetime.now(UTC)

    @property
    def is_terminal(self) -> bool:
        """Whether this plan has reached a state it will never leave."""
        return self.status in (PlanStatus.COMPLETED, PlanStatus.FAILED, PlanStatus.CANCELLED)

    def pending_steps(self) -> tuple[PlanStep, ...]:
        """Return all PENDING steps ordered by order."""
        return tuple(s for s in self.steps if s.status is StepStatus.PENDING)

    def completed_steps(self) -> tuple[PlanStep, ...]:
        """Return all COMPLETED steps ordered by order."""
        return tuple(s for s in self.steps if s.status is StepStatus.COMPLETED)
