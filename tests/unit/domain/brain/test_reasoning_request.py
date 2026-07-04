"""Unit tests for `nikola.domain.entities.reasoning_request`."""

from __future__ import annotations

import pytest

from nikola.domain.entities.reasoning_request import ConversationTurn, ReasoningRequest


@pytest.mark.unit
class TestConversationTurn:
    def test_valid_user_turn(self) -> None:
        turn = ConversationTurn(role="user", content="hello")
        assert turn.role == "user"
        assert turn.content == "hello"

    def test_valid_assistant_turn(self) -> None:
        turn = ConversationTurn(role="assistant", content="hi there!")
        assert turn.role == "assistant"

    def test_invalid_role_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="role"):
            ConversationTurn(role="system", content="you are helpful")

    def test_empty_content_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="content"):
            ConversationTurn(role="user", content="   ")

    def test_is_immutable(self) -> None:
        turn = ConversationTurn(role="user", content="hello")
        with pytest.raises(AttributeError):
            turn.content = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestReasoningRequest:
    def test_minimal_construction_with_content_only(self) -> None:
        req = ReasoningRequest(content="what is the weather?")
        assert req.content == "what is the weather?"
        assert req.conversation_history == ()
        assert req.available_tools == ()
        assert req.system_context is None

    def test_with_conversation_history(self) -> None:
        history = (
            ConversationTurn(role="user", content="first message"),
            ConversationTurn(role="assistant", content="first reply"),
        )
        req = ReasoningRequest(content="follow-up", conversation_history=history)
        assert len(req.conversation_history) == 2

    def test_with_available_tools(self) -> None:
        tools = ("filesystem.read_file", "terminal.execute")
        req = ReasoningRequest(content="read config.yaml", available_tools=tools)
        assert "filesystem.read_file" in req.available_tools

    def test_with_system_context(self) -> None:
        req = ReasoningRequest(content="hello", system_context="You are Nikola.")
        assert req.system_context == "You are Nikola."

    def test_empty_content_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="content"):
            ReasoningRequest(content="")

    def test_whitespace_only_content_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="content"):
            ReasoningRequest(content="   ")

    def test_is_immutable(self) -> None:
        req = ReasoningRequest(content="hello")
        with pytest.raises(AttributeError):
            req.content = "mutated"  # type: ignore[misc]

    def test_two_requests_with_same_content_are_equal(self) -> None:
        a = ReasoningRequest(content="same")
        b = ReasoningRequest(content="same")
        assert a == b
