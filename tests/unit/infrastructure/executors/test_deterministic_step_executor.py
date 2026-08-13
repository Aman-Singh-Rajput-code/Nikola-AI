"""Unit tests for DeterministicStepExecutor."""

from __future__ import annotations

import pytest

from nikola.domain.entities.plan_step import PlanStep
from nikola.domain.entities.step_execution_result import StepExecutionResult
from nikola.domain.ports.step_executor_port import StepExecutorPort
from nikola.domain.value_objects.enums import StepExecutionStatus, StepType
from nikola.infrastructure.executors.deterministic_step_executor import DeterministicStepExecutor


def _step(step_type: StepType = StepType.GENERIC, title: str = "test step") -> PlanStep:
    return PlanStep.create(title=title, description="desc", order=1, step_type=step_type)


@pytest.mark.unit
class TestDeterministicStepExecutorIsAPort:
    def test_is_subclass_of_port(self) -> None:
        assert issubclass(DeterministicStepExecutor, StepExecutorPort)

    def test_executor_name_is_deterministic(self) -> None:
        assert DeterministicStepExecutor().executor_name == "deterministic"


@pytest.mark.unit
class TestDeterministicStepExecutorExecute:
    def test_returns_step_execution_result(self) -> None:
        result = DeterministicStepExecutor().execute(_step())
        assert isinstance(result, StepExecutionResult)

    def test_always_returns_success(self) -> None:
        executor = DeterministicStepExecutor()
        for step_type in StepType:
            result = executor.execute(_step(step_type=step_type))
            assert result.status is StepExecutionStatus.SUCCESS

    def test_result_references_correct_step_id(self) -> None:
        step = _step()
        result = DeterministicStepExecutor().execute(step)
        assert result.step_id == step.id

    def test_output_contains_step_title(self) -> None:
        step = _step(title="My Unique Step Title")
        result = DeterministicStepExecutor().execute(step)
        assert "My Unique Step Title" in result.output

    def test_output_contains_step_type(self) -> None:
        step = _step(step_type=StepType.SHELL)
        result = DeterministicStepExecutor().execute(step)
        assert "shell" in result.output.lower()

    def test_no_error_on_success(self) -> None:
        result = DeterministicStepExecutor().execute(_step())
        assert result.error == ""

    def test_deterministic_same_step_same_output(self) -> None:
        executor = DeterministicStepExecutor()
        step = _step(title="repeatable")
        r1 = executor.execute(step)
        r2 = executor.execute(step)
        assert r1.status == r2.status
        assert r1.output == r2.output

    def test_context_accepted_but_not_required(self) -> None:
        result = DeterministicStepExecutor().execute(_step(), context="some context")
        assert result.status is StepExecutionStatus.SUCCESS
