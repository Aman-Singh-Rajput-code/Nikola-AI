"""`ExecutionManager` — high-level execution coordinator.

Follows the same conventions as `ConversationManager`, `MemoryManager`,
and `PlanningManager`: provides a simple, expressive API that future
Orchestrator sprints will call, delegating all mechanics to the service.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.application.execution.execution_service import ExecutionService  # noqa: TC001

if TYPE_CHECKING:
    from nikola.domain.entities.execution_request import ExecutionResult
    from nikola.domain.entities.plan import Plan

__all__ = ["ExecutionManager"]


class ExecutionManager:
    """High-level execution API for Orchestrator and Agent use.

    Provides convenience wrappers over `ExecutionService` so callers
    only need to supply a plan and optional context.
    """

    def __init__(self, service: ExecutionService) -> None:
        self._service = service

    def execute_plan(
        self,
        plan: Plan,
        *,
        context: str | None = None,
        stop_on_first_failure: bool = True,
    ) -> ExecutionResult:
        """Execute `plan` and return the structured result.

        Args:
            plan: The plan to execute. Must have at least one PENDING step.
            context: Optional operational context passed through to each
                step executor.
            stop_on_first_failure: When True (default), halt on the first
                step failure and cancel remaining steps.

        Returns:
            An `ExecutionResult` with the final execution state and per-step
            outcomes.

        Raises:
            ExecutionError: If the plan is empty or not executable.
        """
        return self._service.execute_plan(
            plan,
            context=context,
            stop_on_first_failure=stop_on_first_failure,
        )

    def execute_plan_best_effort(self, plan: Plan) -> ExecutionResult:
        """Execute `plan`, continuing past failures where possible.

        Unlike `execute_plan()` (which stops at the first failure),
        this method attempts all steps whose dependencies have succeeded,
        even if other independent steps have failed.

        Args:
            plan: The plan to execute.

        Returns:
            An `ExecutionResult` showing all step outcomes.
        """
        return self._service.execute_plan(plan, stop_on_first_failure=False)

    @property
    def executor_name(self) -> str:
        """The name of the active `StepExecutorPort` implementation."""
        return self._service._engine._executor.executor_name
