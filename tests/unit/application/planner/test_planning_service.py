"""Unit tests for PlanningService."""

from __future__ import annotations

import pytest

from nikola.application.planner.planning_service import PlanningService
from nikola.domain.entities.planning_request import PlanningRequest, PlanningResult
from nikola.domain.errors import PlanningError
from nikola.infrastructure.planners.rule_based_planner import RuleBasedPlanner


def _service() -> PlanningService:
    return PlanningService(planner=RuleBasedPlanner())


@pytest.mark.unit
class TestPlanningServiceCreatePlan:
    def test_returns_planning_result(self) -> None:
        svc = _service()
        req = PlanningRequest.create("set up python")
        result = svc.create_plan(req)
        assert isinstance(result, PlanningResult)

    def test_plan_contains_steps(self) -> None:
        svc = _service()
        result = svc.create_plan(PlanningRequest.create("set up python"))
        assert result.plan.step_count > 0

    def test_active_planner_name(self) -> None:
        assert _service().active_planner_name == "rule_based"


@pytest.mark.unit
class TestPlanningServiceCreatePlanForGoal:
    def test_convenience_method_works(self) -> None:
        svc = _service()
        result = svc.create_plan_for_goal("set up python")
        assert isinstance(result, PlanningResult)

    def test_with_context_and_constraints(self) -> None:
        svc = _service()
        result = svc.create_plan_for_goal(
            "set up python", context="web project", constraints=["no conda"]
        )
        assert result.plan.step_count > 0
        assert any("constraint" in w.lower() for w in result.warnings)

    def test_empty_goal_raises(self) -> None:
        svc = _service()
        with pytest.raises(PlanningError):
            svc.create_plan_for_goal("")
