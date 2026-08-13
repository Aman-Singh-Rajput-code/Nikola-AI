"""Unit tests for ExecutionService."""

from __future__ import annotations

import pytest

from nikola.application.execution.execution_engine import ExecutionEngine
from nikola.application.execution.execution_service import ExecutionService
from nikola.domain.entities.execution_request import ExecutionRequest, ExecutionResult
from nikola.domain.entities.plan import Plan
from nikola.domain.entities.plan_step import PlanStep
from nikola.domain.errors import ExecutionError
from nikola.domain.value_objects.enums import ExecutionStatus, StepType
from nikola.infrastructure.executors.deterministic_step_executor import DeterministicStepExecutor


def _service() -> ExecutionService:
    return ExecutionService(engine=ExecutionEngine(step_executor=DeterministicStepExecutor()))


def _plan_with_step() -> Plan:
    p = Plan.create(goal="test")
    p.add_step(PlanStep.create(title="step", description="d", order=1, step_type=StepType.GENERIC))
    return p


@pytest.mark.unit
class TestExecutionServiceExecute:
    def test_returns_execution_result(self) -> None:
        svc = _service()
        req = ExecutionRequest.create(_plan_with_step())
        result = svc.execute(req)
        assert isinstance(result, ExecutionResult)

    def test_completed_on_success(self) -> None:
        svc = _service()
        result = svc.execute(ExecutionRequest.create(_plan_with_step()))
        assert result.final_status is ExecutionStatus.COMPLETED

    def test_empty_plan_raises(self) -> None:
        svc = _service()
        empty = Plan.create(goal="empty")
        with pytest.raises(ExecutionError):
            svc.execute(ExecutionRequest.create(empty))


@pytest.mark.unit
class TestExecutionServiceExecutePlan:
    def test_convenience_method_works(self) -> None:
        svc = _service()
        result = svc.execute_plan(_plan_with_step())
        assert result.final_status is ExecutionStatus.COMPLETED

    def test_with_context(self) -> None:
        svc = _service()
        result = svc.execute_plan(_plan_with_step(), context="test-env")
        assert result.execution.id is not None

    def test_stop_on_first_failure_propagated(self) -> None:
        svc = _service()
        result = svc.execute_plan(_plan_with_step(), stop_on_first_failure=False)
        assert result.final_status is ExecutionStatus.COMPLETED
