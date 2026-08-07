"""Unit tests for PlanStep entity."""

from __future__ import annotations

import pytest

from nikola.domain.entities.plan_step import PlanStep
from nikola.domain.value_objects.enums import StepStatus, StepType
from nikola.domain.value_objects.step_id import StepId


@pytest.mark.unit
class TestPlanStepCreate:
    def test_create_generates_step_id(self) -> None:
        s = PlanStep.create(title="t", description="d", order=1)
        assert isinstance(s.id, StepId)

    def test_create_defaults_to_pending(self) -> None:
        s = PlanStep.create(title="t", description="d", order=1)
        assert s.status is StepStatus.PENDING

    def test_create_defaults_to_generic_type(self) -> None:
        s = PlanStep.create(title="t", description="d", order=1)
        assert s.step_type is StepType.GENERIC

    def test_create_with_explicit_type(self) -> None:
        s = PlanStep.create(title="t", description="d", order=1, step_type=StepType.SHELL)
        assert s.step_type is StepType.SHELL

    def test_create_with_estimated_duration(self) -> None:
        s = PlanStep.create(title="t", description="d", order=1, estimated_duration_seconds=60)
        assert s.estimated_duration_seconds == 60

    def test_create_with_no_duration_gives_none(self) -> None:
        assert (
            PlanStep.create(title="t", description="d", order=1).estimated_duration_seconds is None
        )

    def test_create_with_metadata(self) -> None:
        s = PlanStep.create(title="t", description="d", order=1, metadata={"cmd": "ls"})
        assert s.metadata["cmd"] == "ls"

    def test_create_with_dependencies(self) -> None:
        dep = StepId.generate()
        s = PlanStep.create(title="t", description="d", order=2, dependencies=(dep,))
        assert dep in s.dependencies

    def test_two_steps_have_different_ids(self) -> None:
        a = PlanStep.create(title="t", description="d", order=1)
        b = PlanStep.create(title="t", description="d", order=1)
        assert a.id != b.id
