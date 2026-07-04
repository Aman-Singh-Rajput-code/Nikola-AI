"""Unit tests for `nikola.infrastructure.brains.null_brain.NullBrain`."""

from __future__ import annotations

import pytest

from nikola.domain.entities.reasoning_request import ReasoningRequest
from nikola.domain.ports.brain_port import BrainPort
from nikola.domain.value_objects.intent import IntentType
from nikola.infrastructure.brains.null_brain import NullBrain


@pytest.mark.unit
class TestNullBrainIsABrainPort:
    def test_null_brain_is_a_subclass_of_brain_port(self) -> None:
        assert issubclass(NullBrain, BrainPort)

    def test_null_brain_instance_is_a_brain_port(self) -> None:
        assert isinstance(NullBrain(), BrainPort)


@pytest.mark.unit
class TestNullBrainProviderName:
    def test_provider_name_is_null(self) -> None:
        assert NullBrain().provider_name == "null"


@pytest.mark.unit
class TestNullBrainReason:
    def test_returns_a_reasoning_response(self) -> None:
        from nikola.domain.entities.reasoning_response import ReasoningResponse

        brain = NullBrain()
        resp = brain.reason(ReasoningRequest(content="hello"))
        assert isinstance(resp, ReasoningResponse)

    def test_response_intent_is_always_chat(self) -> None:
        brain = NullBrain()
        resp = brain.reason(ReasoningRequest(content="run a command please"))
        assert resp.intent.intent_type is IntentType.CHAT

    def test_response_confidence_is_always_one(self) -> None:
        brain = NullBrain()
        resp = brain.reason(ReasoningRequest(content="hello"))
        assert resp.intent.confidence == 1.0

    def test_response_content_echoes_request(self) -> None:
        brain = NullBrain()
        resp = brain.reason(ReasoningRequest(content="ping"))
        assert "ping" in resp.content

    def test_response_model_used_is_null(self) -> None:
        brain = NullBrain()
        resp = brain.reason(ReasoningRequest(content="hello"))
        assert resp.model_used == "null"

    def test_response_finish_reason_is_stop(self) -> None:
        brain = NullBrain()
        resp = brain.reason(ReasoningRequest(content="hello"))
        assert resp.finish_reason == "stop"

    def test_response_has_no_tool_call(self) -> None:
        brain = NullBrain()
        resp = brain.reason(ReasoningRequest(content="hello"))
        assert resp.tool_name is None
        assert resp.tool_args is None

    def test_is_deterministic_for_same_input(self) -> None:
        brain = NullBrain()
        req = ReasoningRequest(content="same input")
        first = brain.reason(req)
        second = brain.reason(req)
        assert first.content == second.content
        assert first.intent == second.intent
