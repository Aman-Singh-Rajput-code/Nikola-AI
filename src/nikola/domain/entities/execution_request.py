"""`ExecutionRequest` and `ExecutionResult` — the port boundary objects.

`ExecutionRequest` is what the application layer hands to `ExecutionService`
to begin executing a plan. `ExecutionResult` is what comes back when
execution finishes (successfully or otherwise).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.entities.execution import Execution
    from nikola.domain.entities.plan import Plan
    from nikola.domain.entities.step_execution_result import StepExecutionResult
    from nikola.domain.value_objects.enums import ExecutionStatus

__all__ = ["ExecutionOptions", "ExecutionRequest", "ExecutionResult"]


@dataclass(frozen=True, slots=True)
class ExecutionOptions:
    """Optional configuration for a single execution attempt.

    Kept minimal for Sprint 10. Future sprints may add retry policies,
    timeout configuration, and parallel execution limits.

    Attributes:
        stop_on_first_failure: When `True` (the default), the engine stops
            processing subsequent steps as soon as any step fails. When
            `False`, the engine attempts all steps whose dependencies have
            succeeded, even if other independent steps have failed.
        dry_run: When `True`, steps are dispatched to the executor but the
            executor is expected to return results without performing
            real-world side effects. `DeterministicStepExecutor` always
            behaves as a dry run regardless of this flag.
    """

    stop_on_first_failure: bool = field(default=True)
    dry_run: bool = field(default=False)


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    """An immutable request to execute a `Plan`.

    Attributes:
        plan: The `Plan` to execute. Must have at least one PENDING step.
        context: Optional string providing operational context to pass
            through to each step's executor (e.g. current working
            directory, user preferences, environment name).
        options: Execution behaviour options. Defaults to
            `ExecutionOptions()` (stop on first failure, not a dry run).

    Raises:
        ExecutionError at the application layer if the plan is empty or
        already in a terminal status — not at construction time, since
        the domain entity is a pure data holder.
    """

    plan: Plan
    context: str | None = field(default=None)
    options: ExecutionOptions = field(default_factory=ExecutionOptions)

    @classmethod
    def create(
        cls,
        plan: Plan,
        *,
        context: str | None = None,
        stop_on_first_failure: bool = True,
        dry_run: bool = False,
    ) -> ExecutionRequest:
        """Construct an `ExecutionRequest` with explicit option values.

        Args:
            plan: The plan to execute.
            context: Optional operational context string.
            stop_on_first_failure: Whether to stop at the first step failure.
            dry_run: Whether to run without real-world side effects.

        Returns:
            A validated, immutable `ExecutionRequest`.
        """
        return cls(
            plan=plan,
            context=context,
            options=ExecutionOptions(
                stop_on_first_failure=stop_on_first_failure,
                dry_run=dry_run,
            ),
        )


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """The structured outcome returned after an execution attempt.

    Attributes:
        execution: The `Execution` aggregate with its full step result
            history and final lifecycle state.
        final_status: The terminal `ExecutionStatus` reached.
        completed_steps: Results for steps that ended with SUCCESS.
        failed_steps: Results for steps that ended with FAILED.
        skipped_steps: Results for steps that were SKIPPED (dependency
            failure) or CANCELLED.
        summary: A human-readable one-line summary of the execution outcome,
            e.g. "3/4 steps completed successfully; 1 step failed."
    """

    execution: Execution
    final_status: ExecutionStatus
    completed_steps: tuple[StepExecutionResult, ...]
    failed_steps: tuple[StepExecutionResult, ...]
    skipped_steps: tuple[StepExecutionResult, ...]
    summary: str

    @classmethod
    def from_execution(cls, execution: Execution) -> ExecutionResult:
        """Build an `ExecutionResult` from a finished `Execution`.

        Classifies step results into completed/failed/skipped buckets and
        generates a summary string.

        Args:
            execution: The `Execution` aggregate after it has reached a
                terminal state.

        Returns:
            A fully populated `ExecutionResult`.
        """
        from nikola.domain.value_objects.enums import StepExecutionStatus

        completed: list[StepExecutionResult] = []
        failed: list[StepExecutionResult] = []
        skipped: list[StepExecutionResult] = []

        for result in execution.step_results:
            if result.status is StepExecutionStatus.SUCCESS:
                completed.append(result)
            elif result.status is StepExecutionStatus.FAILED:
                failed.append(result)
            else:
                skipped.append(result)

        total = len(execution.step_results)
        n_ok = len(completed)
        n_fail = len(failed)
        n_skip = len(skipped)

        if execution.status.value == "completed":
            summary = f"Execution completed: {n_ok}/{total} step(s) succeeded."
        elif execution.status.value == "failed":
            summary = f"Execution failed: {n_ok} succeeded, " f"{n_fail} failed, {n_skip} skipped."
        elif execution.status.value == "cancelled":
            summary = (
                f"Execution cancelled: {n_ok} completed before cancellation, "
                f"{n_skip} not started."
            )
        else:
            summary = f"Execution status: {execution.status}."

        return cls(
            execution=execution,
            final_status=execution.status,
            completed_steps=tuple(completed),
            failed_steps=tuple(failed),
            skipped_steps=tuple(skipped),
            summary=summary,
        )
