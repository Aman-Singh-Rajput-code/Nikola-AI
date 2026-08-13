"""`StepExecutionResult` — the recorded outcome of executing one `PlanStep`.

A `StepExecutionResult` is produced by the `StepExecutorPort` and collected
by the `Execution` aggregate. It is immutable — once a step's outcome is
known, it is a historical fact that cannot be altered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.value_objects.enums import StepExecutionStatus
    from nikola.domain.value_objects.step_id import StepId

__all__ = ["StepExecutionResult"]


@dataclass(frozen=True, slots=True)
class StepExecutionResult:
    """The recorded outcome of executing one `PlanStep`.

    Attributes:
        step_id: The `StepId` of the `PlanStep` this result belongs to.
        status: The execution outcome — SUCCESS, FAILED, SKIPPED, or
            CANCELLED.
        output: Optional human-readable output produced by the step
            (e.g. a command's stdout, a tool's return value). Empty string
            if the step produced no output or was not attempted.
        error: Optional human-readable error message if the step failed.
            Empty string for non-FAILED statuses.
        started_at: When execution of this step began. For SKIPPED and
            CANCELLED steps, this is the time the skip/cancel was recorded,
            not the time a tool was invoked.
        completed_at: When execution of this step finished.
    """

    step_id: StepId
    status: StepExecutionStatus
    output: str = field(default="")
    error: str = field(default="")
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def success(
        cls,
        step_id: StepId,
        output: str = "",
        *,
        started_at: datetime | None = None,
    ) -> StepExecutionResult:
        """Construct a SUCCESS `StepExecutionResult`.

        Args:
            step_id: The step that succeeded.
            output: Optional output produced by the step.
            started_at: When the step started. Defaults to now.

        Returns:
            A frozen `StepExecutionResult` with SUCCESS status.
        """
        from nikola.domain.value_objects.enums import StepExecutionStatus

        now = datetime.now(UTC)
        return cls(
            step_id=step_id,
            status=StepExecutionStatus.SUCCESS,
            output=output,
            started_at=started_at or now,
            completed_at=now,
        )

    @classmethod
    def failed(
        cls,
        step_id: StepId,
        error: str = "",
        *,
        started_at: datetime | None = None,
    ) -> StepExecutionResult:
        """Construct a FAILED `StepExecutionResult`.

        Args:
            step_id: The step that failed.
            error: Human-readable description of the failure.
            started_at: When the step started. Defaults to now.

        Returns:
            A frozen `StepExecutionResult` with FAILED status.
        """
        from nikola.domain.value_objects.enums import StepExecutionStatus

        now = datetime.now(UTC)
        return cls(
            step_id=step_id,
            status=StepExecutionStatus.FAILED,
            error=error,
            started_at=started_at or now,
            completed_at=now,
        )

    @classmethod
    def skipped(cls, step_id: StepId) -> StepExecutionResult:
        """Construct a SKIPPED `StepExecutionResult`.

        Used when a step cannot be executed because one of its dependencies
        failed. The step is recorded as SKIPPED rather than FAILED to
        distinguish "could not run" from "ran and failed".

        Args:
            step_id: The step that was skipped.

        Returns:
            A frozen `StepExecutionResult` with SKIPPED status.
        """
        from nikola.domain.value_objects.enums import StepExecutionStatus

        now = datetime.now(UTC)
        return cls(
            step_id=step_id,
            status=StepExecutionStatus.SKIPPED,
            error="Skipped because a dependency step failed.",
            started_at=now,
            completed_at=now,
        )

    @classmethod
    def cancelled(cls, step_id: StepId) -> StepExecutionResult:
        """Construct a CANCELLED `StepExecutionResult`.

        Used when execution is cancelled before this step could run.

        Args:
            step_id: The step that was cancelled.

        Returns:
            A frozen `StepExecutionResult` with CANCELLED status.
        """
        from nikola.domain.value_objects.enums import StepExecutionStatus

        now = datetime.now(UTC)
        return cls(
            step_id=step_id,
            status=StepExecutionStatus.CANCELLED,
            error="Execution was cancelled.",
            started_at=now,
            completed_at=now,
        )
