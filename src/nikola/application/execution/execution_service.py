"""`ExecutionService` — the use-case boundary for execution operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.domain.entities.execution_request import ExecutionRequest, ExecutionResult

if TYPE_CHECKING:
    from nikola.application.execution.execution_engine import ExecutionEngine
    from nikola.domain.entities.plan import Plan

__all__ = ["ExecutionService"]


class ExecutionService:
    """Use-case boundary for plan execution.

    Accepts an `ExecutionRequest`, delegates to `ExecutionEngine`,
    and returns a structured `ExecutionResult`. Future sprints may add
    pre/post execution hooks (permission checks, memory recording, etc.)
    here without changing the engine.
    """

    def __init__(self, engine: ExecutionEngine) -> None:
        self._engine = engine

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute the plan in `request` and return the result.

        Args:
            request: The immutable execution request.

        Returns:
            A structured `ExecutionResult`.

        Raises:
            ExecutionError: If the plan is empty or not executable.
        """
        return self._engine.execute(request)

    def execute_plan(
        self,
        plan: Plan,
        *,
        context: str | None = None,
        stop_on_first_failure: bool = True,
    ) -> ExecutionResult:
        """Convenience method: build an `ExecutionRequest` and execute.

        Args:
            plan: The plan to execute.
            context: Optional operational context string.
            stop_on_first_failure: Whether to stop at the first step failure.

        Returns:
            A structured `ExecutionResult`.
        """
        request = ExecutionRequest.create(
            plan,
            context=context,
            stop_on_first_failure=stop_on_first_failure,
        )
        return self._engine.execute(request)
