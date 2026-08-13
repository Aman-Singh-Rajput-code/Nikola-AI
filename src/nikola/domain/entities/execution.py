"""`Execution` — the mutable aggregate tracking one attempt to execute a `Plan`.

An `Execution` is created by the `ExecutionEngine` when it begins
executing a `Plan`. It accumulates `StepExecutionResult` objects as steps
complete (successfully, with failure, or as skipped), and its `status`
transitions through the execution lifecycle.

`Execution` is distinct from `Plan`:
- `Plan` describes *what should be done* (ordered steps with types and dependencies).
- `Execution` records *what happened when it was tried* (outcomes, timestamps, errors).

This separation allows the same `Plan` to be executed multiple times (retry
attempts, re-executions after fixing a dependency) while preserving the
original plan's integrity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from nikola.domain.errors.domain_errors import ExecutionError
from nikola.domain.value_objects.enums import ExecutionStatus, StepExecutionStatus
from nikola.domain.value_objects.execution_id import ExecutionId

if TYPE_CHECKING:
    from nikola.domain.entities.step_execution_result import StepExecutionResult
    from nikola.domain.value_objects.plan_id import PlanId
    from nikola.domain.value_objects.step_id import StepId

__all__ = ["Execution"]


@dataclass(slots=True)
class Execution:
    """The mutable record of one attempt to execute a `Plan`.

    Attributes:
        id: The execution's unique identifier.
        plan_id: The `PlanId` of the `Plan` being executed.
        status: The execution's current lifecycle state.
        current_step_order: The order number of the step currently being
            processed (or about to be processed). `None` when execution
            has not started or has finished.
        started_at: When this execution began (`start()` was called).
            `None` until started.
        completed_at: When this execution reached a terminal state.
            `None` until completed, failed, or cancelled.
        created_at: When this `Execution` object was created, in UTC.
    """

    id: ExecutionId
    plan_id: PlanId
    status: ExecutionStatus = field(default=ExecutionStatus.PENDING)
    current_step_order: int | None = field(default=None)
    started_at: datetime | None = field(default=None)
    completed_at: datetime | None = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _step_results: list[StepExecutionResult] = field(default_factory=list, repr=False)

    @classmethod
    def create(cls, *, plan_id: PlanId) -> Execution:
        """Construct a new PENDING `Execution` for the given plan.

        Args:
            plan_id: The `PlanId` of the plan to execute.

        Returns:
            A new `Execution` with PENDING status and no step results.
        """
        return cls(id=ExecutionId.generate(), plan_id=plan_id)

    @property
    def step_results(self) -> tuple[StepExecutionResult, ...]:
        """All recorded step results, in the order they were added."""
        return tuple(self._step_results)

    @property
    def is_terminal(self) -> bool:
        """Whether this execution has reached a state it will never leave."""
        return self.status in (
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
        )

    @property
    def successful_step_ids(self) -> frozenset[StepId]:
        """IDs of all steps that completed with SUCCESS status."""
        return frozenset(
            r.step_id for r in self._step_results if r.status is StepExecutionStatus.SUCCESS
        )

    @property
    def failed_step_count(self) -> int:
        """Number of steps that completed with FAILED status."""
        return sum(1 for r in self._step_results if r.status is StepExecutionStatus.FAILED)

    @property
    def skipped_step_count(self) -> int:
        """Number of steps that were SKIPPED (due to a dependency failure)."""
        return sum(1 for r in self._step_results if r.status is StepExecutionStatus.SKIPPED)

    def start(self) -> None:
        """Transition from PENDING to RUNNING.

        Raises:
            ExecutionError: If this execution is not PENDING.
        """
        if self.status is not ExecutionStatus.PENDING:
            raise ExecutionError(
                f"Cannot start an execution with status '{self.status}'. "
                "Only PENDING executions can be started."
            )
        self.status = ExecutionStatus.RUNNING
        self.started_at = datetime.now(UTC)

    def record_step_result(self, result: StepExecutionResult) -> None:
        """Record the outcome of an individual step.

        Args:
            result: The `StepExecutionResult` to append.

        Raises:
            ExecutionError: If this execution is not RUNNING.
        """
        if self.status is not ExecutionStatus.RUNNING:
            raise ExecutionError(
                f"Cannot record a step result for an execution with status "
                f"'{self.status}'. Execution must be RUNNING."
            )
        self._step_results.append(result)

    def advance_to_step(self, order: int) -> None:
        """Update `current_step_order` to `order`.

        Called by the `ExecutionEngine` as it moves from step to step.

        Args:
            order: The `PlanStep.order` of the step now being processed.

        Raises:
            ExecutionError: If this execution is not RUNNING.
        """
        if self.status is not ExecutionStatus.RUNNING:
            raise ExecutionError(
                f"Cannot advance step for an execution with status '{self.status}'."
            )
        self.current_step_order = order

    def complete(self) -> None:
        """Transition from RUNNING to COMPLETED.

        Raises:
            ExecutionError: If this execution is not RUNNING.
        """
        if self.status is not ExecutionStatus.RUNNING:
            raise ExecutionError(
                f"Cannot complete an execution with status '{self.status}'. "
                "Only RUNNING executions can be completed."
            )
        self.status = ExecutionStatus.COMPLETED
        self.completed_at = datetime.now(UTC)

    def fail(self) -> None:
        """Transition from RUNNING to FAILED.

        Raises:
            ExecutionError: If this execution is not RUNNING.
        """
        if self.status is not ExecutionStatus.RUNNING:
            raise ExecutionError(
                f"Cannot fail an execution with status '{self.status}'. "
                "Only RUNNING executions can be failed."
            )
        self.status = ExecutionStatus.FAILED
        self.completed_at = datetime.now(UTC)

    def cancel(self) -> None:
        """Transition to CANCELLED from PENDING or RUNNING.

        Raises:
            ExecutionError: If this execution is already in a terminal state.
        """
        if self.is_terminal:
            raise ExecutionError(
                f"Cannot cancel an execution already in terminal " f"status '{self.status}'."
            )
        self.status = ExecutionStatus.CANCELLED
        self.completed_at = datetime.now(UTC)
