"""Unit tests for `nikola.application.brain.DefaultIntentClassifier`."""

from __future__ import annotations

import pytest

from nikola.application.brain import DefaultIntentClassifier, IntentClassifier
from nikola.domain.entities.reasoning_request import ReasoningRequest
from nikola.domain.entities.reasoning_response import ReasoningResponse
from nikola.domain.ports.brain_port import BrainPort
from nikola.domain.value_objects.intent import Intent, IntentType
from nikola.infrastructure.brains.null_brain import NullBrain


class _FakeBrain(BrainPort):
    """A scriptable fake Brain for testing the classifier in isolation."""

    def __init__(self, intent_type: IntentType, confidence: float = 1.0) -> None:
        self._intent_type = intent_type
        self._confidence = confidence
        self.last_request: ReasoningRequest | None = None

    @property
    def provider_name(self) -> str:
        return "fake"

    def reason(self, request: ReasoningRequest) -> ReasoningResponse:
        self.last_request = request
        tool_name = "fake_tool" if self._intent_type is IntentType.TOOL_INVOCATION else None
        return ReasoningResponse(
            content="fake content",
            intent=Intent(intent_type=self._intent_type, confidence=self._confidence),
            model_used="fake",
            tool_name=tool_name,
        )


@pytest.mark.unit
class TestDefaultIntentClassifierIsAnIntentClassifier:
    def test_is_an_instance_of_intent_classifier(self) -> None:
        classifier = DefaultIntentClassifier(brain=NullBrain())
        assert isinstance(classifier, IntentClassifier)


@pytest.mark.unit
class TestDefaultIntentClassifierClassify:
    def test_classify_returns_intent_from_brain_response(self) -> None:
        fake = _FakeBrain(IntentType.CHAT)
        classifier = DefaultIntentClassifier(brain=fake)

        req = ReasoningRequest(content="hello")
        intent = classifier.classify(req)

        assert intent.intent_type is IntentType.CHAT

    def test_classify_returns_tool_invocation_intent(self) -> None:
        fake = _FakeBrain(IntentType.TOOL_INVOCATION)
        classifier = DefaultIntentClassifier(brain=fake)

        intent = classifier.classify(ReasoningRequest(content="run something"))
        assert intent.intent_type is IntentType.TOOL_INVOCATION

    def test_classify_passes_request_to_brain(self) -> None:
        fake = _FakeBrain(IntentType.CHAT)
        classifier = DefaultIntentClassifier(brain=fake)

        req = ReasoningRequest(content="specific content")
        classifier.classify(req)

        assert fake.last_request is req

    def test_classify_preserves_confidence_from_brain(self) -> None:
        fake = _FakeBrain(IntentType.CHAT, confidence=0.72)
        classifier = DefaultIntentClassifier(brain=fake)

        intent = classifier.classify(ReasoningRequest(content="hello"))
        assert intent.confidence == 0.72

    def test_classify_with_null_brain_returns_chat_intent(self) -> None:
        classifier = DefaultIntentClassifier(brain=NullBrain())
        intent = classifier.classify(ReasoningRequest(content="anything"))
        assert intent.intent_type is IntentType.CHAT
