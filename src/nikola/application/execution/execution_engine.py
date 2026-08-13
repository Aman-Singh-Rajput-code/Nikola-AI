"""`ExecutionEngine` — orchestrates plan execution through `StepExecutorPort`.

The ExecutionEngine manages the full lifecycle of executing a Plan: validating
it, creating an Execution, determining which steps are ready (dependency-aware),
dispatching each step through StepExecutorPort, recording outcomes, and driving
the Execution to a terminal state.

It does NOT know how individual steps accomplish their work.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.domain.entities.execution import Execution
from nikola.domain.entities.execution_request import ExecutionResult
from nikola.domain.entities.step_execution_result import StepExecutionResult
from nikola.domain.errors.domain_errors import ExecutionError
from nikola.domain.value_objects.enums import StepExecutionStatus

if TYPE_CHECKING:
    from nikola.domain.entities.execution_request import ExecutionRequest
    from nikola.domain.entities.plan import Plan
    from nikola.domain.entities.plan_step import PlanStep
    from nikola.domain.ports.step_executor_port import StepExecutorPort
    from nikola.domain.value_objects.step_id import StepId

__all__ = ["ExecutionEngine"]


class ExecutionEngine:
    """Orchestrates the execution of a `Plan` through `StepExecutorPort`.

    Responsibilities:
    1. Validate the plan before execution (non-empty).
    2. Create and manage the `Execution` lifecycle.
    3. Determine which steps are ready (all dependencies succeeded).
    4. Execute each ready step through `StepExecutorPort`.
    5. Record `StepExecutionResult` for every step (including skipped/cancelled).
    6. Handle step failures per `ExecutionOptions.stop_on_first_failure`.
    7. Skip steps whose dependencies failed.
    8. Support cancellation.
    9. Complete or fail the `Execution` when all steps are processed.
    """

    def __init__(self, step_executor: StepExecutorPort) -> None:
        self._executor = step_executor

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute the plan described in `request` and return the result.

        Args:
            request: The validated execution request.

        Returns:
            An `ExecutionResult` describing the final execution state.

        Raises:
            ExecutionError: If the plan is empty.
        """
        plan = request.plan
        self._validate_plan(plan)

        execution = Execution.create(plan_id=plan.id)
        execution.start()

        steps = list(plan.steps)  # sorted by order ascending

        for step in steps:
            execution.advance_to_step(step.order)

            # Check if all dependencies have succeeded
            if not self._dependencies_satisfied(step, execution):
                # Record this step as skipped (dependency failed)
                execution.record_step_result(StepExecutionResult.skipped(step_id=step.id))

                if request.options.stop_on_first_failure:
                    # Record all remaining steps as cancelled, then fail
                    self._record_remaining_as_cancelled(steps, step.order, execution)
                    execution.fail()
                    return ExecutionResult.from_execution(execution)
                continue

            # Execute the step through the port
            try:
                result = self._executor.execute(step, context=request.context)
            except Exception as exc:  # noqa: BLE001
                result = StepExecutionResult.failed(
                    step_id=step.id,
                    error=f"Executor raised an unexpected exception: {exc}",
                )

            execution.record_step_result(result)

            if (
                result.status is StepExecutionStatus.FAILED
                and request.options.stop_on_first_failure
            ):
                # Record remaining steps as cancelled, then fail
                self._record_remaining_as_cancelled(steps, step.order, execution)
                execution.fail()
                return ExecutionResult.from_execution(execution)

        # All steps processed — determine terminal state
        if execution.failed_step_count > 0:
            execution.fail()
        else:
            execution.complete()

        return ExecutionResult.from_execution(execution)

    def execute_with_cancellation(
        self,
        request: ExecutionRequest,
        *,
        cancel_after_steps: int,
    ) -> ExecutionResult:
        """Execute the plan, forcing cancellation after `cancel_after_steps` steps.

        Provided for testing and future orchestration use.

        Args:
            request: The execution request.
            cancel_after_steps: Cancel execution after this many steps have
                been attempted (regardless of outcome).

        Returns:
            An `ExecutionResult` reflecting the partially-executed state.
        """
        plan = request.plan
        self._validate_plan(plan)

        execution = Execution.create(plan_id=plan.id)
        execution.start()

        steps = list(plan.steps)
        attempted = 0

        for step in steps:
            if attempted >= cancel_after_steps:
                # Record remaining (including this step) as cancelled before cancelling
                self._record_remaining_as_cancelled(steps, step.order - 1, execution)
                execution.cancel()
                return ExecutionResult.from_execution(execution)

            execution.advance_to_step(step.order)

            if not self._dependencies_satisfied(step, execution):
                execution.record_step_result(StepExecutionResult.skipped(step_id=step.id))
                attempted += 1
                continue

            try:
                result = self._executor.execute(step, context=request.context)
            except Exception as exc:  # noqa: BLE001
                result = StepExecutionResult.failed(
                    step_id=step.id,
                    error=f"Executor raised an unexpected exception: {exc}",
                )

            execution.record_step_result(result)
            attempted += 1

        # All steps processed
        if execution.failed_step_count > 0:
            execution.fail()
        else:
            execution.complete()

        return ExecutionResult.from_execution(execution)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_plan(plan: Plan) -> None:
        """Raise `ExecutionError` if the plan cannot be executed."""
        if plan.is_empty:
            raise ExecutionError(f"Cannot execute plan '{plan.id}': the plan has no steps.")

    @staticmethod
    def _dependencies_satisfied(
        step: PlanStep,
        execution: Execution,
    ) -> bool:
        """Return True if all of step's dependencies have succeeded."""
        if not step.dependencies:
            return True
        succeeded: frozenset[StepId] = execution.successful_step_ids
        return all(dep_id in succeeded for dep_id in step.dependencies)

    @staticmethod
    def _record_remaining_as_cancelled(
        steps: list[PlanStep],
        after_order: int,
        execution: Execution,
    ) -> None:
        """Record CANCELLED results for all steps not yet recorded."""
        recorded_ids = {r.step_id for r in execution.step_results}
        for s in steps:
            if s.order > after_order and s.id not in recorded_ids:
                execution.record_step_result(StepExecutionResult.cancelled(step_id=s.id))
