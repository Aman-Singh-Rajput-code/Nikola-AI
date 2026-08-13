"""Unit tests for ExecutionRequest, ExecutionOptions, ExecutionResult."""

from __future__ import annotations

import pytest

from nikola.domain.entities.execution import Execution
from nikola.domain.entities.execution_request import (
    ExecutionOptions,
    ExecutionRequest,
    ExecutionResult,
)
from nikola.domain.entities.plan import Plan
from nikola.domain.entities.plan_step import PlanStep
from nikola.domain.entities.step_execution_result import StepExecutionResult
from nikola.domain.value_objects.enums import ExecutionStatus, StepType
from nikola.domain.value_objects.plan_id import PlanId


def _plan_with_steps(n: int = 2) -> Plan:
    p = Plan.create(goal="test goal")
    for i in range(1, n + 1):
        p.add_step(
            PlanStep.create(title=f"step {i}", description="d", order=i, step_type=StepType.GENERIC)
        )
    return p


@pytest.mark.unit
class TestExecutionOptions:
    def test_defaults(self) -> None:
        opts = ExecutionOptions()
        assert opts.stop_on_first_failure is True
        assert opts.dry_run is False

    def test_is_immutable(self) -> None:
        opts = ExecutionOptions()
        with pytest.raises(AttributeError):
            opts.dry_run = True  # type: ignore[misc]


@pytest.mark.unit
class TestExecutionRequest:
    def test_create_with_plan(self) -> None:
        p = _plan_with_steps()
        req = ExecutionRequest.create(p)
        assert req.plan is p
        assert req.context is None
        assert req.options.stop_on_first_failure is True

    def test_create_with_context(self) -> None:
        req = ExecutionRequest.create(_plan_with_steps(), context="prod")
        assert req.context == "prod"

    def test_create_with_options(self) -> None:
        req = ExecutionRequest.create(_plan_with_steps(), stop_on_first_failure=False, dry_run=True)
        assert req.options.stop_on_first_failure is False
        assert req.options.dry_run is True

    def test_is_immutable(self) -> None:
        req = ExecutionRequest.create(_plan_with_steps())
        with pytest.raises(AttributeError):
            req.context = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestExecutionResult:
    def _completed_execution(self) -> Execution:
        e = Execution.create(plan_id=PlanId.generate())
        e.start()
        sid = _plan_with_steps(1).steps[0].id
        e.record_step_result(StepExecutionResult.success(sid))
        e.complete()
        return e

    def test_from_execution_completed(self) -> None:
        e = self._completed_execution()
        r = ExecutionResult.from_execution(e)
        assert r.final_status is ExecutionStatus.COMPLETED
        assert len(r.completed_steps) == 1
        assert "completed" in r.summary.lower()

    def test_from_execution_failed(self) -> None:
        from nikola.domain.value_objects.step_id import StepId

        e = Execution.create(plan_id=PlanId.generate())
        e.start()
        e.record_step_result(StepExecutionResult.failed(StepId.generate(), error="err"))
        e.fail()
        r = ExecutionResult.from_execution(e)
        assert r.final_status is ExecutionStatus.FAILED
        assert len(r.failed_steps) == 1
        assert "failed" in r.summary.lower()

    def test_from_execution_cancelled(self) -> None:
        from nikola.domain.value_objects.step_id import StepId

        e = Execution.create(plan_id=PlanId.generate())
        e.start()
        e.record_step_result(StepExecutionResult.cancelled(StepId.generate()))
        e.cancel()
        r = ExecutionResult.from_execution(e)
        assert r.final_status is ExecutionStatus.CANCELLED
        assert len(r.skipped_steps) == 1

    def test_is_immutable(self) -> None:
        r = ExecutionResult.from_execution(self._completed_execution())
        with pytest.raises(AttributeError):
            r.summary = "mutated"  # type: ignore[misc]
