"""`PlanningManager` — high-level coordinator for planning operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.application.planner.planning_service import PlanningService  # noqa: TC001

if TYPE_CHECKING:
    from nikola.domain.entities.planning_request import PlanningResult

__all__ = ["PlanningManager"]


class PlanningManager:
    """High-level planning API for Orchestrator and Agent use.

    Wraps PlanningService with convenience methods so callers only
    need a goal string. Future Orchestrator sprints call plan_goal().
    """

    def __init__(self, service: PlanningService) -> None:
        self._service = service

    def plan_goal(
        self,
        goal: str,
        *,
        context: str | None = None,
        constraints: list[str] | None = None,
    ) -> PlanningResult:
        """Create a plan for goal with optional context and constraints.

        Args:
            goal: The goal to plan for. Must be non-empty.
            context: Optional background information.
            constraints: Optional restrictions the plan must respect.

        Returns:
            A PlanningResult with the generated plan.

        Raises:
            PlanningError: If goal is empty or the planner fails.
        """
        return self._service.create_plan_for_goal(goal, context=context, constraints=constraints)

    def plan_goal_simple(self, goal: str) -> PlanningResult:
        """Create a plan for goal with no context or constraints.

        Args:
            goal: The goal to plan for. Must be non-empty.

        Returns:
            A PlanningResult from the active planner.
        """
        return self._service.create_plan_for_goal(goal)

    @property
    def active_planner_name(self) -> str:
        """Name of the currently active planner implementation."""
        return self._service.active_planner_name
