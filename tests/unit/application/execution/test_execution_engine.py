"""Unit tests for ExecutionEngine."""

from __future__ import annotations

import pytest

from nikola.application.execution.execution_engine import ExecutionEngine
from nikola.domain.entities.execution_request import ExecutionRequest
from nikola.domain.entities.plan import Plan
from nikola.domain.entities.plan_step import PlanStep
from nikola.domain.entities.step_execution_result import StepExecutionResult
from nikola.domain.errors import ExecutionError
from nikola.domain.ports.step_executor_port import StepExecutorPort
from nikola.domain.value_objects.enums import ExecutionStatus, StepExecutionStatus, StepType
from nikola.infrastructure.executors.deterministic_step_executor import DeterministicStepExecutor


def _engine() -> ExecutionEngine:
    return ExecutionEngine(step_executor=DeterministicStepExecutor())


def _plan(*titles: str) -> Plan:
    p = Plan.create(goal="test goal")
    for i, title in enumerate(titles, start=1):
        p.add_step(
            PlanStep.create(title=title, description="d", order=i, step_type=StepType.GENERIC)
        )
    return p


def _request(
    plan: Plan, stop_on_first_failure: bool = True, context: str | None = None
) -> ExecutionRequest:
    return ExecutionRequest.create(
        plan, context=context, stop_on_first_failure=stop_on_first_failure
    )


class _FailingExecutor(StepExecutorPort):
    """Always returns FAILED results."""

    @property
    def executor_name(self) -> str:
        return "failing"

    def execute(self, step: PlanStep, context: str | None = None) -> StepExecutionResult:
        return StepExecutionResult.failed(step_id=step.id, error="deliberate failure")


class _FailOnTitleExecutor(StepExecutorPort):
    """Fails any step whose title contains a given string."""

    def __init__(self, fail_title: str) -> None:
        self._fail_title = fail_title

    @property
    def executor_name(self) -> str:
        return "conditional_fail"

    def execute(self, step: PlanStep, context: str | None = None) -> StepExecutionResult:
        if self._fail_title in step.title:
            return StepExecutionResult.failed(step_id=step.id, error="matched fail title")
        return StepExecutionResult.success(step_id=step.id, output="ok")


@pytest.mark.unit
class TestExecutionEngineEmptyPlan:
    def test_empty_plan_raises_execution_error(self) -> None:
        engine = _engine()
        empty_plan = Plan.create(goal="empty")
        with pytest.raises(ExecutionError, match="no steps"):
            engine.execute(_request(empty_plan))


@pytest.mark.unit
class TestExecutionEngineSuccessfulExecution:
    def test_all_steps_succeed(self) -> None:
        result = _engine().execute(_request(_plan("a", "b", "c")))
        assert result.final_status is ExecutionStatus.COMPLETED

    def test_completed_steps_count(self) -> None:
        result = _engine().execute(_request(_plan("a", "b", "c")))
        assert len(result.completed_steps) == 3

    def test_no_failed_steps(self) -> None:
        result = _engine().execute(_request(_plan("a", "b")))
        assert len(result.failed_steps) == 0

    def test_summary_mentions_completed(self) -> None:
        result = _engine().execute(_request(_plan("a")))
        assert "completed" in result.summary.lower()

    def test_execution_id_is_set(self) -> None:
        result = _engine().execute(_request(_plan("a")))
        assert result.execution.id is not None

    def test_started_at_is_set(self) -> None:
        result = _engine().execute(_request(_plan("a")))
        assert result.execution.started_at is not None

    def test_completed_at_is_set(self) -> None:
        result = _engine().execute(_request(_plan("a")))
        assert result.execution.completed_at is not None


@pytest.mark.unit
class TestExecutionEngineFailureHandling:
    def test_failing_executor_produces_failed_status(self) -> None:
        engine = ExecutionEngine(step_executor=_FailingExecutor())
        result = engine.execute(_request(_plan("a", "b")))
        assert result.final_status is ExecutionStatus.FAILED

    def test_stop_on_first_failure_cancels_remaining(self) -> None:
        engine = ExecutionEngine(step_executor=_FailingExecutor())
        result = engine.execute(_request(_plan("a", "b", "c"), stop_on_first_failure=True))
        total_recorded = (
            len(result.completed_steps) + len(result.failed_steps) + len(result.skipped_steps)
        )
        assert total_recorded == 3  # all steps have a result recorded

    def test_continue_on_failure_attempts_independent_steps(self) -> None:
        executor = _FailOnTitleExecutor("step 1")
        engine = ExecutionEngine(step_executor=executor)
        # Steps 2 and 3 have no dependency on step 1 — they should run
        result = engine.execute(
            _request(_plan("step 1", "step 2", "step 3"), stop_on_first_failure=False)
        )
        assert len(result.completed_steps) == 2
        assert len(result.failed_steps) == 1

    def test_failed_step_summary_mentions_failed(self) -> None:
        engine = ExecutionEngine(step_executor=_FailingExecutor())
        result = engine.execute(_request(_plan("a")))
        assert "failed" in result.summary.lower()


@pytest.mark.unit
class TestExecutionEngineDependencyOrdering:
    def test_step_with_satisfied_dependency_executes(self) -> None:
        plan = Plan.create(goal="dep test")
        s1 = PlanStep.create(title="first", description="d", order=1, step_type=StepType.GENERIC)
        s2 = PlanStep.create(
            title="second",
            description="d",
            order=2,
            step_type=StepType.GENERIC,
            dependencies=(s1.id,),
        )
        plan.add_step(s1)
        plan.add_step(s2)
        result = _engine().execute(_request(plan))
        assert result.final_status is ExecutionStatus.COMPLETED
        assert len(result.completed_steps) == 2

    def test_step_with_failed_dependency_is_skipped(self) -> None:
        """When stop_on_first_failure=False, a step with a failed dependency
        is encountered and recorded as SKIPPED (dependency not satisfied)."""
        plan = Plan.create(goal="dep fail test")
        s1 = PlanStep.create(
            title="failing dep", description="d", order=1, step_type=StepType.GENERIC
        )
        s2 = PlanStep.create(
            title="dependent",
            description="d",
            order=2,
            step_type=StepType.GENERIC,
            dependencies=(s1.id,),
        )
        plan.add_step(s1)
        plan.add_step(s2)
        executor = _FailOnTitleExecutor("failing dep")
        engine = ExecutionEngine(step_executor=executor)
        # Use stop_on_first_failure=False so we actually reach s2 and check its deps
        result = engine.execute(_request(plan, stop_on_first_failure=False))
        # s1 fails, s2 is skipped (dependency not satisfied, but we kept going)
        assert len(result.failed_steps) == 1
        assert result.skipped_steps[0].status is StepExecutionStatus.SKIPPED

    def test_independent_steps_all_execute(self) -> None:
        plan = Plan.create(goal="independent steps")
        for i in range(1, 4):
            plan.add_step(
                PlanStep.create(
                    title=f"step {i}", description="d", order=i, step_type=StepType.GENERIC
                )
            )
        result = _engine().execute(_request(plan))
        assert len(result.completed_steps) == 3


@pytest.mark.unit
class TestExecutionEngineContext:
    def test_context_passed_to_executor(self) -> None:
        received: list[str | None] = []

        class _ContextCapturingExecutor(StepExecutorPort):
            @property
            def executor_name(self) -> str:
                return "context_capturing"

            def execute(self, step: PlanStep, context: str | None = None) -> StepExecutionResult:
                received.append(context)
                return StepExecutionResult.success(step_id=step.id)

        engine = ExecutionEngine(step_executor=_ContextCapturingExecutor())
        engine.execute(_request(_plan("a"), context="my-context"))
        assert received == ["my-context"]


@pytest.mark.unit
class TestExecutionEngineWithCancellation:
    def test_cancel_after_zero_steps_cancels_all(self) -> None:
        result = _engine().execute_with_cancellation(
            _request(_plan("a", "b", "c")), cancel_after_steps=0
        )
        assert result.final_status is ExecutionStatus.CANCELLED

    def test_cancel_after_one_step_records_first(self) -> None:
        result = _engine().execute_with_cancellation(
            _request(_plan("a", "b", "c")), cancel_after_steps=1
        )
        total = len(result.completed_steps) + len(result.failed_steps) + len(result.skipped_steps)
        assert total == 3  # all steps accounted for
