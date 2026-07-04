"""Brain use-case layer: intent classification and future brain-adjacent use cases.

Sprint 6 delivers:
- `IntentClassifier` — abstract base for intent classification use cases.
- `DefaultIntentClassifier` — concrete implementation delegating to `BrainPort`.
"""

from nikola.application.brain.default_intent_classifier import DefaultIntentClassifier
from nikola.application.brain.intent_classifier import IntentClassifier

__all__ = ["IntentClassifier", "DefaultIntentClassifier"]
