"""`IntentClassifier` — application-layer abstraction for intent classification.

Intent classification is the act of taking a `ReasoningRequest` and
deciding what kind of action it implies: is this a conversational exchange,
a request to invoke a tool, a clarification request, or something out of
scope? This determination shapes the entire execution path that follows.

`IntentClassifier` is defined as an abstract base class (not a domain port)
because it is an *application-layer policy*, not a swappable infrastructure
concern. There is one canonical classification strategy: ask the Brain.
Future variants (rule-based pre-classifier for common patterns, cached
classifier for repeated inputs) are still application logic, not
infrastructure adapters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.entities.reasoning_request import ReasoningRequest
    from nikola.domain.value_objects.intent import Intent

__all__ = ["IntentClassifier"]


class IntentClassifier(ABC):
    """Abstract application-layer service for classifying the intent of a request.

    The single method `classify()` takes a `ReasoningRequest` and returns
    an `Intent` describing what kind of action the Brain determined the
    request implies. Downstream use cases (Planner, Router, Agent
    Orchestrator — future sprints) depend on this abstraction and never
    call `BrainPort.reason()` directly; this keeps the "how do we decide
    what to do" policy testable and replaceable independently of the Brain
    adapter in use.
    """

    @abstractmethod
    def classify(self, request: ReasoningRequest) -> Intent:
        """Classify the intent implied by `request`.

        Args:
            request: The structured reasoning input to classify.

        Returns:
            An `Intent` describing what kind of action `request` implies
            and the Brain's confidence in that classification.

        Raises:
            nikola.domain.errors.BrainError: Propagated from the
                underlying `BrainPort.reason()` call if the Brain fails.
        """
        raise NotImplementedError
