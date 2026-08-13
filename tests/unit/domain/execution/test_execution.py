"""Unit tests for the Execution entity lifecycle."""

from __future__ import annotations

import pytest

from nikola.domain.entities.execution import Execution
from nikola.domain.entities.step_execution_result import StepExecutionResult
from nikola.domain.errors import ExecutionError
from nikola.domain.value_objects.enums import ExecutionStatus
from nikola.domain.value_objects.execution_id import ExecutionId
from nikola.domain.value_objects.plan_id import PlanId
from nikola.domain.value_objects.step_id import StepId


def _execution() -> Execution:
    return Execution.create(plan_id=PlanId.generate())


def _result(status: str = "success") -> StepExecutionResult:
    sid = StepId.generate()
    if status == "success":
        return StepExecutionResult.success(sid)
    elif status == "failed":
        return StepExecutionResult.failed(sid, error="err")
    return StepExecutionResult.skipped(sid)


@pytest.mark.unit
class TestExecutionCreate:
    def test_create_generates_id(self) -> None:
        assert isinstance(_execution().id, ExecutionId)

    def test_create_is_pending(self) -> None:
        assert _execution().status is ExecutionStatus.PENDING

    def test_create_no_step_results(self) -> None:
        assert _execution().step_results == ()

    def test_create_no_started_at(self) -> None:
        assert _execution().started_at is None


@pytest.mark.unit
class TestExecutionStart:
    def test_start_transitions_to_running(self) -> None:
        e = _execution()
        e.start()
        assert e.status is ExecutionStatus.RUNNING

    def test_start_sets_started_at(self) -> None:
        e = _execution()
        e.start()
        assert e.started_at is not None

    def test_start_non_pending_raises(self) -> None:
        e = _execution()
        e.start()
        with pytest.raises(ExecutionError, match="PENDING"):
            e.start()


@pytest.mark.unit
class TestExecutionRecordStepResult:
    def test_record_appends_result(self) -> None:
        e = _execution()
        e.start()
        e.record_step_result(_result())
        assert len(e.step_results) == 1

    def test_record_on_non_running_raises(self) -> None:
        e = _execution()
        with pytest.raises(ExecutionError, match="RUNNING"):
            e.record_step_result(_result())


@pytest.mark.unit
class TestExecutionAdvanceToStep:
    def test_advance_sets_current_step_order(self) -> None:
        e = _execution()
        e.start()
        e.advance_to_step(3)
        assert e.current_step_order == 3

    def test_advance_non_running_raises(self) -> None:
        e = _execution()
        with pytest.raises(ExecutionError):
            e.advance_to_step(1)


@pytest.mark.unit
class TestExecutionComplete:
    def test_complete_from_running(self) -> None:
        e = _execution()
        e.start()
        e.complete()
        assert e.status is ExecutionStatus.COMPLETED

    def test_complete_sets_completed_at(self) -> None:
        e = _execution()
        e.start()
        e.complete()
        assert e.completed_at is not None

    def test_complete_non_running_raises(self) -> None:
        with pytest.raises(ExecutionError):
            _execution().complete()


@pytest.mark.unit
class TestExecutionFail:
    def test_fail_from_running(self) -> None:
        e = _execution()
        e.start()
        e.fail()
        assert e.status is ExecutionStatus.FAILED

    def test_fail_non_running_raises(self) -> None:
        with pytest.raises(ExecutionError):
            _execution().fail()


@pytest.mark.unit
class TestExecutionCancel:
    def test_cancel_from_pending(self) -> None:
        e = _execution()
        e.cancel()
        assert e.status is ExecutionStatus.CANCELLED

    def test_cancel_from_running(self) -> None:
        e = _execution()
        e.start()
        e.cancel()
        assert e.status is ExecutionStatus.CANCELLED

    def test_cancel_completed_raises(self) -> None:
        e = _execution()
        e.start()
        e.complete()
        with pytest.raises(ExecutionError, match="terminal"):
            e.cancel()

    def test_cancel_failed_raises(self) -> None:
        e = _execution()
        e.start()
        e.fail()
        with pytest.raises(ExecutionError):
            e.cancel()


@pytest.mark.unit
class TestExecutionIsTerminal:
    def test_pending_not_terminal(self) -> None:
        assert not _execution().is_terminal

    def test_running_not_terminal(self) -> None:
        e = _execution()
        e.start()
        assert not e.is_terminal

    def test_completed_is_terminal(self) -> None:
        e = _execution()
        e.start()
        e.complete()
        assert e.is_terminal

    def test_failed_is_terminal(self) -> None:
        e = _execution()
        e.start()
        e.fail()
        assert e.is_terminal

    def test_cancelled_is_terminal(self) -> None:
        e = _execution()
        e.cancel()
        assert e.is_terminal


@pytest.mark.unit
class TestExecutionSuccessfulStepIds:
    def test_successful_step_ids_empty_initially(self) -> None:
        e = _execution()
        e.start()
        assert len(e.successful_step_ids) == 0

    def test_successful_step_ids_includes_success(self) -> None:
        e = _execution()
        e.start()
        r = _result("success")
        e.record_step_result(r)
        assert r.step_id in e.successful_step_ids

    def test_successful_step_ids_excludes_failed(self) -> None:
        e = _execution()
        e.start()
        r = _result("failed")
        e.record_step_result(r)
        assert r.step_id not in e.successful_step_ids


@pytest.mark.unit
class TestExecutionCounts:
    def test_failed_step_count(self) -> None:
        e = _execution()
        e.start()
        e.record_step_result(_result("failed"))
        assert e.failed_step_count == 1

    def test_skipped_step_count(self) -> None:
        e = _execution()
        e.start()
        e.record_step_result(_result("skipped"))
        assert e.skipped_step_count == 1
