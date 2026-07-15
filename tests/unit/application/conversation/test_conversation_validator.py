"""Unit tests for `nikola.application.conversation.ConversationValidator`."""

from __future__ import annotations

import pytest

from nikola.application.conversation.conversation_validator import ConversationValidator
from nikola.domain.entities.conversation import Conversation
from nikola.domain.errors import ConversationError, MessageValidationError
from nikola.domain.value_objects.enums import MessageRole
from nikola.domain.value_objects.session_id import SessionId


def _active_conversation() -> Conversation:
    return Conversation.create(session_id=SessionId.generate())


@pytest.mark.unit
class TestConversationValidatorCanAddMessage:
    def test_valid_user_message_passes(self) -> None:
        conv = _active_conversation()
        validator = ConversationValidator()
        validator.validate_can_add_message(conv, MessageRole.USER, "hello")  # must not raise

    def test_valid_assistant_message_passes(self) -> None:
        conv = _active_conversation()
        ConversationValidator().validate_can_add_message(conv, MessageRole.ASSISTANT, "reply")

    def test_valid_tool_message_passes(self) -> None:
        conv = _active_conversation()
        ConversationValidator().validate_can_add_message(conv, MessageRole.TOOL, "result")

    def test_archived_conversation_raises_conversation_error(self) -> None:
        conv = _active_conversation()
        conv.archive()
        with pytest.raises(ConversationError, match="ACTIVE"):
            ConversationValidator().validate_can_add_message(conv, MessageRole.USER, "hi")

    def test_deleted_conversation_raises_conversation_error(self) -> None:
        conv = _active_conversation()
        conv.soft_delete()
        with pytest.raises(ConversationError, match="ACTIVE"):
            ConversationValidator().validate_can_add_message(conv, MessageRole.USER, "hi")

    def test_empty_content_raises_message_validation_error(self) -> None:
        conv = _active_conversation()
        with pytest.raises(MessageValidationError, match="empty"):
            ConversationValidator().validate_can_add_message(conv, MessageRole.USER, "")

    def test_whitespace_content_raises_message_validation_error(self) -> None:
        conv = _active_conversation()
        with pytest.raises(MessageValidationError):
            ConversationValidator().validate_can_add_message(conv, MessageRole.USER, "   ")

    def test_system_role_raises_message_validation_error(self) -> None:
        conv = _active_conversation()
        with pytest.raises(MessageValidationError, match="SYSTEM"):
            ConversationValidator().validate_can_add_message(
                conv, MessageRole.SYSTEM, "system prompt"
            )


@pytest.mark.unit
class TestConversationValidatorExists:
    def test_non_none_conversation_is_returned_unchanged(self) -> None:
        conv = _active_conversation()
        result = ConversationValidator().validate_conversation_exists(conv, conv.id)
        assert result is conv

    def test_none_raises_conversation_error(self) -> None:
        cid = "some-id"
        with pytest.raises(ConversationError, match=str(cid)):
            ConversationValidator().validate_conversation_exists(None, cid)
