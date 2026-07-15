"""Unit tests for `nikola.domain.entities.conversation.Conversation`."""

from __future__ import annotations

import pytest

from nikola.domain.entities.conversation import Conversation
from nikola.domain.entities.message import Message
from nikola.domain.errors import ConversationError, MessageValidationError
from nikola.domain.value_objects.conversation_id import ConversationId
from nikola.domain.value_objects.enums import ConversationStatus, MessageRole
from nikola.domain.value_objects.session_id import SessionId


def _session() -> SessionId:
    return SessionId.generate()


def _conversation() -> Conversation:
    return Conversation.create(session_id=_session())


def _message(conv: Conversation, role: MessageRole, content: str) -> Message:
    return Message.create(conversation_id=conv.id, role=role, content=content)


@pytest.mark.unit
class TestConversationCreate:
    def test_create_sets_a_conversation_id(self) -> None:
        assert isinstance(_conversation().id, ConversationId)

    def test_create_status_is_active(self) -> None:
        assert _conversation().status is ConversationStatus.ACTIVE

    def test_create_starts_with_no_messages(self) -> None:
        assert _conversation().message_count == 0

    def test_create_is_active(self) -> None:
        assert _conversation().is_active is True

    def test_two_created_conversations_have_different_ids(self) -> None:
        sid = _session()
        a = Conversation.create(session_id=sid)
        b = Conversation.create(session_id=sid)
        assert a.id != b.id


@pytest.mark.unit
class TestConversationAddMessage:
    def test_add_message_appends_to_messages(self) -> None:
        conv = _conversation()
        msg = _message(conv, MessageRole.USER, "hello")
        conv.add_message(msg)
        assert conv.message_count == 1
        assert conv.messages[0] is msg

    def test_add_message_preserves_order(self) -> None:
        conv = _conversation()
        m1 = _message(conv, MessageRole.USER, "first")
        m2 = _message(conv, MessageRole.ASSISTANT, "second")
        conv.add_message(m1)
        conv.add_message(m2)
        assert conv.messages[0].content == "first"
        assert conv.messages[1].content == "second"

    def test_add_message_updates_updated_at(self) -> None:
        conv = _conversation()
        before = conv.updated_at
        conv.add_message(_message(conv, MessageRole.USER, "hi"))
        assert conv.updated_at >= before

    def test_add_message_to_archived_conversation_raises(self) -> None:
        conv = _conversation()
        conv.archive()
        with pytest.raises(ConversationError, match="ACTIVE"):
            conv.add_message(_message(conv, MessageRole.USER, "hi"))

    def test_add_message_to_deleted_conversation_raises(self) -> None:
        conv = _conversation()
        conv.soft_delete()
        with pytest.raises(ConversationError, match="ACTIVE"):
            conv.add_message(_message(conv, MessageRole.USER, "hi"))

    def test_add_message_with_wrong_conversation_id_raises(self) -> None:
        conv = _conversation()
        other_conv = _conversation()
        msg = _message(other_conv, MessageRole.USER, "wrong conv")
        with pytest.raises(MessageValidationError, match="conversation_id"):
            conv.add_message(msg)

    def test_messages_property_returns_immutable_tuple(self) -> None:
        conv = _conversation()
        conv.add_message(_message(conv, MessageRole.USER, "hi"))
        assert isinstance(conv.messages, tuple)


@pytest.mark.unit
class TestConversationArchive:
    def test_archive_sets_status_to_archived(self) -> None:
        conv = _conversation()
        conv.archive()
        assert conv.status is ConversationStatus.ARCHIVED

    def test_archive_non_active_conversation_raises(self) -> None:
        conv = _conversation()
        conv.archive()
        with pytest.raises(ConversationError, match="ACTIVE"):
            conv.archive()

    def test_archive_deleted_conversation_raises(self) -> None:
        conv = _conversation()
        conv.soft_delete()
        with pytest.raises(ConversationError):
            conv.archive()


@pytest.mark.unit
class TestConversationSoftDelete:
    def test_soft_delete_sets_status_to_deleted(self) -> None:
        conv = _conversation()
        conv.soft_delete()
        assert conv.status is ConversationStatus.DELETED

    def test_soft_delete_archived_conversation_succeeds(self) -> None:
        conv = _conversation()
        conv.archive()
        conv.soft_delete()
        assert conv.status is ConversationStatus.DELETED

    def test_soft_delete_already_deleted_raises(self) -> None:
        conv = _conversation()
        conv.soft_delete()
        with pytest.raises(ConversationError, match="already DELETED"):
            conv.soft_delete()


@pytest.mark.unit
class TestConversationGetHistoryForBrain:
    def test_includes_user_and_assistant_messages(self) -> None:
        conv = _conversation()
        conv.add_message(_message(conv, MessageRole.USER, "hello"))
        conv.add_message(_message(conv, MessageRole.ASSISTANT, "hi!"))
        history = conv.get_history_for_brain()
        assert len(history) == 2

    def test_excludes_system_messages(self) -> None:
        conv = _conversation()
        conv.add_message(_message(conv, MessageRole.SYSTEM, "you are nikola"))
        conv.add_message(_message(conv, MessageRole.USER, "hello"))
        history = conv.get_history_for_brain()
        assert len(history) == 1
        assert history[0].role == "user"

    def test_includes_tool_messages(self) -> None:
        conv = _conversation()
        conv.add_message(_message(conv, MessageRole.USER, "read file"))
        conv.add_message(_message(conv, MessageRole.TOOL, "file content here"))
        history = conv.get_history_for_brain()
        assert len(history) == 2
        assert history[1].role == "tool"

    def test_returns_tuple_of_conversation_turns(self) -> None:
        from nikola.domain.entities.reasoning_request import ConversationTurn

        conv = _conversation()
        conv.add_message(_message(conv, MessageRole.USER, "hi"))
        history = conv.get_history_for_brain()
        assert isinstance(history, tuple)
        assert isinstance(history[0], ConversationTurn)

    def test_empty_conversation_returns_empty_tuple(self) -> None:
        assert _conversation().get_history_for_brain() == ()
