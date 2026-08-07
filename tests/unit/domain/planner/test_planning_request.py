"""Unit tests for PlanningRequest and PlanningResult."""

from __future__ import annotations

import pytest

from nikola.domain.entities.plan import Plan
from nikola.domain.entities.planning_request import PlanningRequest, PlanningResult
from nikola.domain.errors import PlanningError


@pytest.mark.unit
class TestPlanningRequest:
    def test_create_with_goal_only(self) -> None:
        req = PlanningRequest.create("build an API")
        assert req.goal == "build an API"
        assert req.context is None
        assert req.constraints == ()

    def test_create_with_context_and_constraints(self) -> None:
        req = PlanningRequest.create(
            "deploy app", context="Python project", constraints=["no docker"]
        )
        assert req.context == "Python project"
        assert "no docker" in req.constraints

    def test_empty_goal_raises(self) -> None:
        with pytest.raises(PlanningError):
            PlanningRequest.create("")

    def test_whitespace_goal_raises(self) -> None:
        with pytest.raises(PlanningError):
            PlanningRequest.create("   ")

    def test_is_immutable(self) -> None:
        req = PlanningRequest.create("goal")
        with pytest.raises(AttributeError):
            req.goal = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestPlanningResult:
    def _plan(self) -> Plan:
        return Plan.create(goal="test goal")

    def test_valid_result(self) -> None:
        result = PlanningResult(plan=self._plan(), confidence=0.9)
        assert result.confidence == 0.9
        assert result.warnings == ()
        assert result.reasoning_summary == ""

    def test_confidence_below_zero_raises(self) -> None:
        with pytest.raises(PlanningError, match="confidence"):
            PlanningResult(plan=self._plan(), confidence=-0.1)

    def test_confidence_above_one_raises(self) -> None:
        with pytest.raises(PlanningError, match="confidence"):
            PlanningResult(plan=self._plan(), confidence=1.001)

    def test_confidence_exactly_zero_and_one_accepted(self) -> None:
        PlanningResult(plan=self._plan(), confidence=0.0)
        PlanningResult(plan=self._plan(), confidence=1.0)

    def test_with_warnings_and_summary(self) -> None:
        result = PlanningResult(
            plan=self._plan(),
            confidence=0.5,
            warnings=("check constraints",),
            reasoning_summary="matched keyword: python",
        )
        assert len(result.warnings) == 1
        assert "python" in result.reasoning_summary

    def test_is_immutable(self) -> None:
        result = PlanningResult(plan=self._plan(), confidence=1.0)
        with pytest.raises(AttributeError):
            result.confidence = 0.5  # type: ignore[misc]
