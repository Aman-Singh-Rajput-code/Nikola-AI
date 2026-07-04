"""`DefaultIntentClassifier` — the standard intent classification use case.

This is the concrete `IntentClassifier` that the composition root wires up.
It delegates classification to the registered `BrainPort`, interpreting the
returned `ReasoningResponse.intent` as the classification result. Future
classifiers might add pre-classification rules (e.g. "a request containing
only 'hi' is always CHAT without calling the Brain") as an optimisation
layer above this one, without changing the downstream contract.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.application.brain.intent_classifier import IntentClassifier

if TYPE_CHECKING:
    from nikola.domain.entities.reasoning_request import ReasoningRequest
    from nikola.domain.ports.brain_port import BrainPort
    from nikola.domain.value_objects.intent import Intent

__all__ = ["DefaultIntentClassifier"]


class DefaultIntentClassifier(IntentClassifier):
    """Classifies intent by delegating a full `reason()` call to the `BrainPort`.

    This is the canonical, production-ready implementation: every
    classification is a real reasoning call. The `Intent` embedded in
    the `ReasoningResponse` is returned directly.

    Attributes:
        _brain: The `BrainPort` implementation resolved from the DI
            container. Injected at construction time to keep this class
            testable with any `BrainPort` implementation (including
            `NullBrain` and hand-rolled fakes).
    """

    def __init__(self, brain: BrainPort) -> None:
        self._brain = brain

    def classify(self, request: ReasoningRequest) -> Intent:
        """Classify `request` by calling `brain.reason()` and returning the intent.

        Args:
            request: The reasoning input to classify.

        Returns:
            The `Intent` embedded in the `BrainPort`'s `ReasoningResponse`.

        Raises:
            nikola.domain.errors.BrainError: Propagated from
                `BrainPort.reason()` if the Brain fails.
        """
        response = self._brain.reason(request)
        return response.intent
