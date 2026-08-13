"""Unit tests for ExecutionManager."""

from __future__ import annotations

import pytest

from nikola.application.execution.execution_engine import ExecutionEngine
from nikola.application.execution.execution_manager import ExecutionManager
from nikola.application.execution.execution_service import ExecutionService
from nikola.domain.entities.execution_request import ExecutionResult
from nikola.domain.entities.plan import Plan
from nikola.domain.entities.plan_step import PlanStep
from nikola.domain.errors import ExecutionError
from nikola.domain.value_objects.enums import ExecutionStatus, StepType
from nikola.infrastructure.executors.deterministic_step_executor import DeterministicStepExecutor


def _manager() -> ExecutionManager:
    engine = ExecutionEngine(step_executor=DeterministicStepExecutor())
    svc = ExecutionService(engine=engine)
    return ExecutionManager(service=svc)


def _plan(*n: int) -> Plan:
    p = Plan.create(goal="test")
    for i in range(1, (n[0] if n else 2) + 1):
        p.add_step(
            PlanStep.create(title=f"step {i}", description="d", order=i, step_type=StepType.GENERIC)
        )
    return p


@pytest.mark.unit
class TestExecutionManagerExecutePlan:
    def test_returns_execution_result(self) -> None:
        assert isinstance(_manager().execute_plan(_plan()), ExecutionResult)

    def test_completed_on_success(self) -> None:
        assert _manager().execute_plan(_plan()).final_status is ExecutionStatus.COMPLETED

    def test_with_context(self) -> None:
        result = _manager().execute_plan(_plan(), context="ctx")
        assert result.final_status is ExecutionStatus.COMPLETED

    def test_empty_plan_raises(self) -> None:
        with pytest.raises(ExecutionError):
            _manager().execute_plan(Plan.create(goal="empty"))


@pytest.mark.unit
class TestExecutionManagerBestEffort:
    def test_best_effort_returns_result(self) -> None:
        result = _manager().execute_plan_best_effort(_plan(3))
        assert result.final_status is ExecutionStatus.COMPLETED


@pytest.mark.unit
class TestExecutionManagerExecutorName:
    def test_returns_executor_name(self) -> None:
        assert _manager().executor_name == "deterministic"
