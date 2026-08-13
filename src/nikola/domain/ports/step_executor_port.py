"""`StepExecutorPort` — the provider-independent abstraction for step execution.

This port is the critical boundary between the `ExecutionEngine` (which
coordinates *what* to execute and in what order) and the real-world
implementation (which knows *how* to execute a specific `StepType`).

The intended future architecture is:

    ExecutionEngine → StepExecutorPort → Tool Registry → Concrete Tools

Sprint 10 implements only the port and a deterministic test adapter
(`DeterministicStepExecutor`). Future sprints add real-world implementations
behind this same port without changing the Execution Engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.entities.plan_step import PlanStep
    from nikola.domain.entities.step_execution_result import StepExecutionResult

__all__ = ["StepExecutorPort"]


class StepExecutorPort(ABC):
    """Abstract interface for executing an individual `PlanStep`.

    The `ExecutionEngine` depends on this port exclusively. It never imports
    any concrete tool, filesystem operation, or external service. This
    ensures the engine can be tested in complete isolation and that real-world
    implementations can be swapped via the composition root.

    All implementations must be safe to call from the execution engine loop:
    they must either return a `StepExecutionResult` or raise an exception
    (which the engine will catch and record as a FAILED result).
    """

    @abstractmethod
    def execute(
        self,
        step: PlanStep,
        context: str | None = None,
    ) -> StepExecutionResult:
        """Execute `step` and return its structured result.

        Implementations are responsible for:
        - Performing whatever action the step's `StepType` requires.
        - Returning a `StepExecutionResult` with SUCCESS or FAILED status.
        - Catching their own internal exceptions and converting them into
          FAILED results rather than letting them propagate.

        Implementations must NOT:
        - Modify the `Execution` or any `Plan` object.
        - Call back into the `ExecutionEngine` or any application service.
        - Block indefinitely without a timeout mechanism.

        Args:
            step: The `PlanStep` to execute. Contains the step type,
                title, description, and metadata needed to dispatch to
                the appropriate tool.
            context: Optional operational context string passed through
                from the `ExecutionRequest` (e.g. working directory,
                environment name, user preferences).

        Returns:
            A `StepExecutionResult` with SUCCESS or FAILED status and
            any output or error message produced.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def executor_name(self) -> str:
        """A short identifier for this executor implementation.

        Used in logs and the composition root.
        Examples: ``"deterministic"``, ``"tool_registry"``.
        """
        raise NotImplementedError
