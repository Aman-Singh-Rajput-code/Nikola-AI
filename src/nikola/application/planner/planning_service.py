"""`PlanningService` — primary use-case service for planning operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.domain.entities.planning_request import PlanningRequest, PlanningResult

if TYPE_CHECKING:
    from nikola.domain.ports.planner_port import PlannerPort

__all__ = ["PlanningService"]


class PlanningService:
    """Orchestrates plan creation by delegating to the registered PlannerPort.

    Depends on PlannerPort (injected; swappable between RuleBasedPlanner,
    a future LLMBasedPlanner, etc.). Does NOT execute plans.
    """

    def __init__(self, planner: PlannerPort) -> None:
        self._planner = planner

    def create_plan(self, request: PlanningRequest) -> PlanningResult:
        """Delegate request to the active PlannerPort and return the result.

        Args:
            request: A validated PlanningRequest.

        Returns:
            A PlanningResult with the generated Plan.

        Raises:
            PlanningError: If the planner cannot produce a valid plan.
        """
        return self._planner.plan(request)

    def create_plan_for_goal(
        self,
        goal: str,
        *,
        context: str | None = None,
        constraints: list[str] | None = None,
    ) -> PlanningResult:
        """Build a PlanningRequest and create a plan in one call.

        Args:
            goal: The goal to plan for. Must be non-empty.
            context: Optional background information.
            constraints: Optional planning restrictions.

        Returns:
            A PlanningResult from the active planner.
        """
        request = PlanningRequest.create(goal, context=context, constraints=constraints)
        return self.create_plan(request)

    @property
    def active_planner_name(self) -> str:
        """Name of the currently active PlannerPort implementation."""
        return self._planner.planner_name
