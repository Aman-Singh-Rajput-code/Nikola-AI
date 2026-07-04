"""Unit tests for `nikola.domain.entities.reasoning_response`."""

from __future__ import annotations

import pytest

from nikola.domain.entities.reasoning_response import ReasoningResponse
from nikola.domain.value_objects.intent import Intent, IntentType


def _chat_intent() -> Intent:
    return Intent(intent_type=IntentType.CHAT)


def _tool_intent() -> Intent:
    return Intent(intent_type=IntentType.TOOL_INVOCATION)


@pytest.mark.unit
class TestReasoningResponseConstruction:
    def test_minimal_chat_response(self) -> None:
        resp = ReasoningResponse(
            content="hello back",
            intent=_chat_intent(),
            model_used="null",
        )
        assert resp.content == "hello back"
        assert resp.intent.intent_type is IntentType.CHAT
        assert resp.model_used == "null"
        assert resp.tool_name is None
        assert resp.tool_args is None
        assert resp.finish_reason == "stop"

    def test_tool_invocation_response(self) -> None:
        resp = ReasoningResponse(
            content="",
            intent=_tool_intent(),
            model_used="null",
            tool_name="filesystem.read_file",
            tool_args={"path": "config.yaml"},
        )
        assert resp.tool_name == "filesystem.read_file"
        assert resp.tool_args == {"path": "config.yaml"}

    def test_custom_finish_reason(self) -> None:
        resp = ReasoningResponse(
            content="",
            intent=_tool_intent(),
            model_used="null",
            tool_name="some_tool",
            finish_reason="tool_call",
        )
        assert resp.finish_reason == "tool_call"


@pytest.mark.unit
class TestReasoningResponseValidation:
    def test_tool_invocation_without_tool_name_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="tool_name"):
            ReasoningResponse(
                content="",
                intent=_tool_intent(),
                model_used="null",
                tool_name=None,
            )

    def test_blank_tool_name_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="tool_name"):
            ReasoningResponse(
                content="",
                intent=_tool_intent(),
                model_used="null",
                tool_name="   ",
            )

    def test_chat_response_without_tool_name_is_valid(self) -> None:
        resp = ReasoningResponse(
            content="hi",
            intent=_chat_intent(),
            model_used="null",
        )
        assert resp.tool_name is None


@pytest.mark.unit
class TestReasoningResponseImmutability:
    def test_content_cannot_be_reassigned(self) -> None:
        resp = ReasoningResponse(
            content="hi",
            intent=_chat_intent(),
            model_used="null",
        )
        with pytest.raises(AttributeError):
            resp.content = "mutated"  # type: ignore[misc]
