"""Unit tests for StepExecutionResult entity."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from nikola.domain.entities.step_execution_result import StepExecutionResult
from nikola.domain.value_objects.enums import StepExecutionStatus
from nikola.domain.value_objects.step_id import StepId


def _sid() -> StepId:
    return StepId.generate()


@pytest.mark.unit
class TestStepExecutionResultSuccess:
    def test_success_sets_status(self) -> None:
        r = StepExecutionResult.success(_sid(), output="ok")
        assert r.status is StepExecutionStatus.SUCCESS

    def test_success_sets_output(self) -> None:
        r = StepExecutionResult.success(_sid(), output="output text")
        assert r.output == "output text"

    def test_success_empty_error(self) -> None:
        assert StepExecutionResult.success(_sid()).error == ""

    def test_success_is_immutable(self) -> None:
        r = StepExecutionResult.success(_sid())
        with pytest.raises(AttributeError):
            r.output = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestStepExecutionResultFailed:
    def test_failed_sets_status(self) -> None:
        r = StepExecutionResult.failed(_sid(), error="boom")
        assert r.status is StepExecutionStatus.FAILED

    def test_failed_sets_error(self) -> None:
        r = StepExecutionResult.failed(_sid(), error="something went wrong")
        assert r.error == "something went wrong"


@pytest.mark.unit
class TestStepExecutionResultSkipped:
    def test_skipped_sets_status(self) -> None:
        r = StepExecutionResult.skipped(_sid())
        assert r.status is StepExecutionStatus.SKIPPED

    def test_skipped_has_error_message(self) -> None:
        assert "dependency" in StepExecutionResult.skipped(_sid()).error.lower()


@pytest.mark.unit
class TestStepExecutionResultCancelled:
    def test_cancelled_sets_status(self) -> None:
        r = StepExecutionResult.cancelled(_sid())
        assert r.status is StepExecutionStatus.CANCELLED

    def test_cancelled_has_error_message(self) -> None:
        assert "cancelled" in StepExecutionResult.cancelled(_sid()).error.lower()


@pytest.mark.unit
class TestStepExecutionResultTimestamps:
    def test_started_at_before_or_equal_completed_at(self) -> None:
        r = StepExecutionResult.success(_sid())
        assert r.started_at <= r.completed_at

    def test_custom_started_at(self) -> None:
        t = datetime(2024, 1, 1, tzinfo=UTC)
        r = StepExecutionResult.success(_sid(), started_at=t)
        assert r.started_at == t
