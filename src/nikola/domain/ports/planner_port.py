"""`PlannerPort` — the provider-agnostic planning interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.entities.planning_request import PlanningRequest, PlanningResult

__all__ = ["PlannerPort"]


class PlannerPort(ABC):
    """Abstract interface all planning backends must implement.

    Receives a PlanningRequest and returns a PlanningResult containing
    a structured Plan, confidence score, warnings, and reasoning summary.
    Implementations must NOT execute steps, call external services, or
    perform filesystem/terminal/browser operations.
    """

    @abstractmethod
    def plan(self, request: PlanningRequest) -> PlanningResult:
        """Convert request into a structured PlanningResult.

        Args:
            request: The validated, immutable planning input.

        Returns:
            A PlanningResult with ordered PlanSteps.

        Raises:
            nikola.domain.errors.PlanningError: If planning fails.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def planner_name(self) -> str:
        """Short human-readable identifier (e.g. 'rule_based', 'llm_based')."""
        raise NotImplementedError
