"""Unit tests for Plan entity lifecycle."""

from __future__ import annotations

import pytest

from nikola.domain.entities.plan import Plan
from nikola.domain.entities.plan_step import PlanStep
from nikola.domain.errors import PlanningError
from nikola.domain.value_objects.enums import PlanStatus, StepType
from nikola.domain.value_objects.plan_id import PlanId


def _step(order: int = 1, step_type: StepType = StepType.GENERIC) -> PlanStep:
    return PlanStep.create(
        title=f"step {order}", description="desc", order=order, step_type=step_type
    )


@pytest.mark.unit
class TestPlanCreate:
    def test_create_generates_plan_id(self) -> None:
        assert isinstance(Plan.create(goal="do something").id, PlanId)

    def test_create_is_pending(self) -> None:
        assert Plan.create(goal="do something").status is PlanStatus.PENDING

    def test_create_is_empty(self) -> None:
        assert Plan.create(goal="do something").is_empty

    def test_create_empty_goal_raises(self) -> None:
        with pytest.raises(PlanningError):
            Plan.create(goal="")

    def test_create_whitespace_goal_raises(self) -> None:
        with pytest.raises(PlanningError):
            Plan.create(goal="   ")


@pytest.mark.unit
class TestPlanAddStep:
    def test_add_step_increases_count(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(_step())
        assert plan.step_count == 1

    def test_steps_are_sorted_by_order(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(_step(order=3))
        plan.add_step(_step(order=1))
        plan.add_step(_step(order=2))
        orders = [s.order for s in plan.steps]
        assert orders == [1, 2, 3]

    def test_add_step_to_non_pending_plan_raises(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(_step())
        plan.start()
        with pytest.raises(PlanningError, match="PENDING"):
            plan.add_step(_step(order=2))

    def test_messages_property_returns_tuple(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(_step())
        assert isinstance(plan.steps, tuple)


@pytest.mark.unit
class TestPlanEstimatedDuration:
    def test_sum_when_all_steps_have_estimates(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(
            PlanStep.create(title="a", description="d", order=1, estimated_duration_seconds=30)
        )
        plan.add_step(
            PlanStep.create(title="b", description="d", order=2, estimated_duration_seconds=60)
        )
        assert plan.estimated_duration_seconds == 90

    def test_none_when_any_step_has_no_estimate(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(
            PlanStep.create(title="a", description="d", order=1, estimated_duration_seconds=30)
        )
        plan.add_step(PlanStep.create(title="b", description="d", order=2))
        assert plan.estimated_duration_seconds is None

    def test_zero_for_empty_plan(self) -> None:
        assert Plan.create(goal="goal").estimated_duration_seconds == 0


@pytest.mark.unit
class TestPlanLifecycle:
    def test_start_transitions_to_in_progress(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(_step())
        plan.start()
        assert plan.status is PlanStatus.IN_PROGRESS

    def test_start_empty_plan_raises(self) -> None:
        with pytest.raises(PlanningError, match="empty"):
            Plan.create(goal="goal").start()

    def test_start_non_pending_raises(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(_step())
        plan.start()
        with pytest.raises(PlanningError):
            plan.start()

    def test_complete_from_in_progress(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(_step())
        plan.start()
        plan.complete()
        assert plan.status is PlanStatus.COMPLETED

    def test_complete_from_pending_raises(self) -> None:
        with pytest.raises(PlanningError):
            Plan.create(goal="goal").complete()

    def test_fail_from_in_progress(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(_step())
        plan.start()
        plan.fail()
        assert plan.status is PlanStatus.FAILED

    def test_cancel_from_pending(self) -> None:
        plan = Plan.create(goal="goal")
        plan.cancel()
        assert plan.status is PlanStatus.CANCELLED

    def test_cancel_from_in_progress(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(_step())
        plan.start()
        plan.cancel()
        assert plan.status is PlanStatus.CANCELLED

    def test_cancel_completed_raises(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(_step())
        plan.start()
        plan.complete()
        with pytest.raises(PlanningError, match="terminal"):
            plan.cancel()

    def test_is_terminal_for_completed(self) -> None:
        plan = Plan.create(goal="goal")
        plan.add_step(_step())
        plan.start()
        plan.complete()
        assert plan.is_terminal

    def test_is_not_terminal_for_pending(self) -> None:
        assert not Plan.create(goal="goal").is_terminal
