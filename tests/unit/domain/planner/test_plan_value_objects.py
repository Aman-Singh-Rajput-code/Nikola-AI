"""Unit tests for PlanId, StepId, and planner enums."""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.enums import PlanStatus, StepStatus, StepType
from nikola.domain.value_objects.plan_id import PlanId
from nikola.domain.value_objects.step_id import StepId


@pytest.mark.unit
class TestPlanId:
    def test_generate_returns_plan_id(self) -> None:
        assert isinstance(PlanId.generate(), PlanId)

    def test_generate_produces_unique_values(self) -> None:
        assert PlanId.generate() != PlanId.generate()

    def test_equal_values_are_equal(self) -> None:
        assert PlanId(value="abc") == PlanId(value="abc")

    def test_empty_value_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            PlanId(value="")

    def test_str_returns_value(self) -> None:
        assert str(PlanId(value="abc")) == "abc"

    def test_is_immutable(self) -> None:
        pid = PlanId(value="abc")
        with pytest.raises(AttributeError):
            pid.value = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestStepId:
    def test_generate_returns_step_id(self) -> None:
        assert isinstance(StepId.generate(), StepId)

    def test_generate_produces_unique_values(self) -> None:
        assert StepId.generate() != StepId.generate()

    def test_empty_value_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            StepId(value="")

    def test_str_returns_value(self) -> None:
        assert str(StepId(value="abc")) == "abc"

    def test_is_immutable(self) -> None:
        sid = StepId(value="abc")
        with pytest.raises(AttributeError):
            sid.value = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestPlannerEnums:
    def test_plan_status_has_expected_members(self) -> None:
        assert {m.value for m in PlanStatus} == {
            "pending",
            "in_progress",
            "completed",
            "failed",
            "cancelled",
        }

    def test_step_status_has_expected_members(self) -> None:
        assert {m.value for m in StepStatus} == {
            "pending",
            "in_progress",
            "completed",
            "failed",
            "skipped",
        }

    def test_step_type_has_expected_members(self) -> None:
        assert {m.value for m in StepType} == {
            "research",
            "code",
            "shell",
            "file",
            "communication",
            "reasoning",
            "human_input",
            "generic",
        }

    def test_all_are_str_subclasses(self) -> None:
        assert isinstance(PlanStatus.PENDING, str)
        assert isinstance(StepStatus.PENDING, str)
        assert isinstance(StepType.GENERIC, str)
