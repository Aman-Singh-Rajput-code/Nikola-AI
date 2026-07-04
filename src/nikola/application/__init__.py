"""Application layer: use cases and orchestration logic.

Sprint 6 adds the Brain use-case layer:
- `brain/intent_classifier.py` — `IntentClassifier`, the abstract
  application-layer service that uses a `BrainPort` to classify the
  intent of a `ReasoningRequest`.
- `brain/default_intent_classifier.py` — `DefaultIntentClassifier`, the
  concrete implementation that delegates to the registered `BrainPort`.

Planner, Agent, Conversation, Memory, Scheduler, and Orchestration use
cases are implemented in later sprints.
"""
