"""`DeterministicStepExecutor` — a no-side-effect `StepExecutorPort` for Sprint 10.

Like `NullBrain` and `RuleBasedPlanner`, this is a fully working implementation
of its port contract that requires no external dependencies. It returns
deterministic SUCCESS results for every step type, making the entire execution
pipeline testable end-to-end without any real-world tools.

It must NOT:
- Create, read, modify, or delete files.
- Execute shell commands or subprocesses.
- Open browsers or make network requests.
- Call any external service or AI provider.
- Access OS-level resources.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.domain.entities.step_execution_result import StepExecutionResult
from nikola.domain.ports.step_executor_port import StepExecutorPort

if TYPE_CHECKING:
    from nikola.domain.entities.plan_step import PlanStep

__all__ = ["DeterministicStepExecutor"]


class DeterministicStepExecutor(StepExecutorPort):
    """A deterministic, no-side-effect `StepExecutorPort` implementation.

    Returns a SUCCESS `StepExecutionResult` for every step, with an output
    message that records the step title and type. This makes the complete
    Execution Engine pipeline testable without any real-world tool integration.

    The same step always produces the same result — no randomness, no network
    dependency, no filesystem access.
    """

    @property
    def executor_name(self) -> str:
        return "deterministic"

    def execute(
        self,
        step: PlanStep,
        context: str | None = None,  # noqa: ARG002
    ) -> StepExecutionResult:
        """Return a deterministic SUCCESS result for `step`.

        Args:
            step: The step to record as successfully executed.
            context: Ignored by this implementation; accepted for interface
                compatibility.

        Returns:
            A `StepExecutionResult` with SUCCESS status and a message
            recording the step title and type.
        """
        output = (
            f"[DeterministicStepExecutor] Step '{step.title}' "
            f"(type: {step.step_type}) executed successfully."
        )
        return StepExecutionResult.success(step_id=step.id, output=output)
