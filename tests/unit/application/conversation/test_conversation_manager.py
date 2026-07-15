"""Unit tests for `nikola.application.conversation.ConversationManager`."""

from __future__ import annotations

import pytest

from nikola.application.conversation.conversation_manager import ConversationManager
from nikola.application.conversation.conversation_service import ConversationService
from nikola.domain.entities.message import Message
from nikola.domain.value_objects.enums import ConversationStatus, MessageRole
from nikola.domain.value_objects.session_id import SessionId
from nikola.infrastructure.persistence.in_memory import InMemoryConversationRepository


def _manager() -> ConversationManager:
    repo = InMemoryConversationRepository()
    svc = ConversationService(repository=repo)
    return ConversationManager(service=svc)


@pytest.mark.unit
class TestConversationManagerGetOrCreate:
    def test_creates_conversation_when_none_exists(self) -> None:
        mgr = _manager()
        conv = mgr.get_or_create_active_conversation(SessionId.generate())
        assert conv.status is ConversationStatus.ACTIVE

    def test_returns_existing_active_conversation(self) -> None:
        mgr = _manager()
        sid = SessionId.generate()
        first = mgr.get_or_create_active_conversation(sid)
        second = mgr.get_or_create_active_conversation(sid)
        assert first.id == second.id

    def test_creates_new_when_only_archived_exists(self) -> None:
        repo = InMemoryConversationRepository()
        svc = ConversationService(repository=repo)
        mgr = ConversationManager(service=svc)

        sid = SessionId.generate()
        conv = mgr.get_or_create_active_conversation(sid)
        svc.archive_conversation(conv.id)

        new_conv = mgr.get_or_create_active_conversation(sid)
        assert new_conv.id != conv.id
        assert new_conv.status is ConversationStatus.ACTIVE


@pytest.mark.unit
class TestConversationManagerAddMessages:
    def test_add_user_message_uses_user_role(self) -> None:
        mgr = _manager()
        conv = mgr.get_or_create_active_conversation(SessionId.generate())
        msg = mgr.add_user_message(conv.id, "hello")
        assert isinstance(msg, Message)
        assert msg.role is MessageRole.USER

    def test_add_assistant_message_uses_assistant_role(self) -> None:
        mgr = _manager()
        conv = mgr.get_or_create_active_conversation(SessionId.generate())
        msg = mgr.add_assistant_message(conv.id, "reply")
        assert msg.role is MessageRole.ASSISTANT

    def test_add_tool_result_uses_tool_role(self) -> None:
        mgr = _manager()
        conv = mgr.get_or_create_active_conversation(SessionId.generate())
        msg = mgr.add_tool_result(conv.id, "file content")
        assert msg.role is MessageRole.TOOL


@pytest.mark.unit
class TestConversationManagerGetBrainContext:
    def test_returns_ordered_turns(self) -> None:
        mgr = _manager()
        sid = SessionId.generate()
        conv = mgr.get_or_create_active_conversation(sid)
        mgr.add_user_message(conv.id, "hello")
        mgr.add_assistant_message(conv.id, "hi there")
        history = mgr.get_brain_context(conv.id)
        assert len(history) == 2
        assert history[0].role == "user"
        assert history[1].role == "assistant"

    def test_empty_conversation_returns_empty_tuple(self) -> None:
        mgr = _manager()
        conv = mgr.get_or_create_active_conversation(SessionId.generate())
        assert mgr.get_brain_context(conv.id) == ()
