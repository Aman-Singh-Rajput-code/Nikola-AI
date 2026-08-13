"""Unit tests for ExecutionId, ExecutionStatus, StepExecutionStatus."""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.enums import ExecutionStatus, StepExecutionStatus
from nikola.domain.value_objects.execution_id import ExecutionId


@pytest.mark.unit
class TestExecutionId:
    def test_generate_returns_execution_id(self) -> None:
        assert isinstance(ExecutionId.generate(), ExecutionId)

    def test_generate_produces_unique_values(self) -> None:
        assert ExecutionId.generate() != ExecutionId.generate()

    def test_equal_values_are_equal(self) -> None:
        assert ExecutionId(value="abc") == ExecutionId(value="abc")

    def test_empty_value_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            ExecutionId(value="")

    def test_str_returns_value(self) -> None:
        assert str(ExecutionId(value="abc")) == "abc"

    def test_is_immutable(self) -> None:
        eid = ExecutionId(value="abc")
        with pytest.raises(AttributeError):
            eid.value = "x"  # type: ignore[misc]


@pytest.mark.unit
class TestExecutionStatus:
    def test_has_expected_members(self) -> None:
        assert {m.value for m in ExecutionStatus} == {
            "pending",
            "running",
            "completed",
            "failed",
            "cancelled",
        }

    def test_is_str_subclass(self) -> None:
        assert isinstance(ExecutionStatus.PENDING, str)


@pytest.mark.unit
class TestStepExecutionStatus:
    def test_has_expected_members(self) -> None:
        assert {m.value for m in StepExecutionStatus} == {
            "success",
            "failed",
            "skipped",
            "cancelled",
        }

    def test_is_str_subclass(self) -> None:
        assert isinstance(StepExecutionStatus.SUCCESS, str)
