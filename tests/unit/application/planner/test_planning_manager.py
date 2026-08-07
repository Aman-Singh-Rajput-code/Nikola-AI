"""Unit tests for PlanningManager."""

from __future__ import annotations

import pytest

from nikola.application.planner.planning_manager import PlanningManager
from nikola.application.planner.planning_service import PlanningService
from nikola.domain.entities.planning_request import PlanningResult
from nikola.domain.errors import PlanningError
from nikola.infrastructure.planners.rule_based_planner import RuleBasedPlanner


def _manager() -> PlanningManager:
    return PlanningManager(service=PlanningService(planner=RuleBasedPlanner()))


@pytest.mark.unit
class TestPlanningManagerPlanGoal:
    def test_plan_goal_returns_result(self) -> None:
        result = _manager().plan_goal("set up python")
        assert isinstance(result, PlanningResult)

    def test_plan_goal_with_context(self) -> None:
        result = _manager().plan_goal("set up python", context="web project")
        assert result.plan.step_count > 0

    def test_plan_goal_with_constraints(self) -> None:
        result = _manager().plan_goal("set up python", constraints=["no conda"])
        assert any("constraint" in w.lower() for w in result.warnings)

    def test_plan_goal_empty_raises(self) -> None:
        with pytest.raises(PlanningError):
            _manager().plan_goal("")


@pytest.mark.unit
class TestPlanningManagerPlanGoalSimple:
    def test_simple_returns_result(self) -> None:
        result = _manager().plan_goal_simple("set up python")
        assert isinstance(result, PlanningResult)

    def test_simple_empty_raises(self) -> None:
        with pytest.raises(PlanningError):
            _manager().plan_goal_simple("")


@pytest.mark.unit
class TestPlanningManagerActivePlannerName:
    def test_active_planner_name(self) -> None:
        assert _manager().active_planner_name == "rule_based"
