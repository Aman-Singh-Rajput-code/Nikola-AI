"""Unit tests for `nikola.application.conversation.ConversationService`."""

from __future__ import annotations

import pytest

from nikola.application.conversation.conversation_service import ConversationService
from nikola.domain.entities.conversation import Conversation
from nikola.domain.entities.message import Message
from nikola.domain.errors import ConversationError, MessageValidationError
from nikola.domain.value_objects.enums import ConversationStatus, MessageRole
from nikola.domain.value_objects.session_id import SessionId
from nikola.infrastructure.persistence.in_memory import InMemoryConversationRepository


def _service() -> tuple[ConversationService, InMemoryConversationRepository]:
    repo = InMemoryConversationRepository()
    return ConversationService(repository=repo), repo


@pytest.mark.unit
class TestConversationServiceCreate:
    def test_create_returns_a_conversation(self) -> None:
        svc, _ = _service()
        conv = svc.create_conversation(SessionId.generate())
        assert isinstance(conv, Conversation)

    def test_create_persists_the_conversation(self) -> None:
        svc, repo = _service()
        conv = svc.create_conversation(SessionId.generate())
        assert repo.get(conv.id) is conv

    def test_create_status_is_active(self) -> None:
        svc, _ = _service()
        conv = svc.create_conversation(SessionId.generate())
        assert conv.status is ConversationStatus.ACTIVE


@pytest.mark.unit
class TestConversationServiceAddMessage:
    def test_add_message_returns_a_message(self) -> None:
        svc, _ = _service()
        conv = svc.create_conversation(SessionId.generate())
        msg = svc.add_message(conv.id, MessageRole.USER, "hello")
        assert isinstance(msg, Message)

    def test_add_message_appends_to_conversation(self) -> None:
        svc, _ = _service()
        conv = svc.create_conversation(SessionId.generate())
        svc.add_message(conv.id, MessageRole.USER, "hello")
        assert svc.get_conversation(conv.id).message_count == 1

    def test_add_message_to_unknown_conversation_raises(self) -> None:
        from nikola.domain.value_objects.conversation_id import ConversationId

        svc, _ = _service()
        with pytest.raises(ConversationError):
            svc.add_message(ConversationId.generate(), MessageRole.USER, "hi")

    def test_add_message_empty_content_raises(self) -> None:
        svc, _ = _service()
        conv = svc.create_conversation(SessionId.generate())
        with pytest.raises(MessageValidationError):
            svc.add_message(conv.id, MessageRole.USER, "")

    def test_add_message_system_role_raises(self) -> None:
        svc, _ = _service()
        conv = svc.create_conversation(SessionId.generate())
        with pytest.raises(MessageValidationError, match="SYSTEM"):
            svc.add_message(conv.id, MessageRole.SYSTEM, "context")


@pytest.mark.unit
class TestConversationServiceGetConversation:
    def test_get_returns_existing_conversation(self) -> None:
        svc, _ = _service()
        conv = svc.create_conversation(SessionId.generate())
        assert svc.get_conversation(conv.id) is conv

    def test_get_unknown_conversation_raises(self) -> None:
        from nikola.domain.value_objects.conversation_id import ConversationId

        svc, _ = _service()
        with pytest.raises(ConversationError):
            svc.get_conversation(ConversationId.generate())


@pytest.mark.unit
class TestConversationServiceGetHistoryForBrain:
    def test_returns_conversation_turns(self) -> None:
        svc, _ = _service()
        conv = svc.create_conversation(SessionId.generate())
        svc.add_message(conv.id, MessageRole.USER, "hello")
        svc.add_message(conv.id, MessageRole.ASSISTANT, "hi!")
        history = svc.get_history_for_brain(conv.id)
        assert len(history) == 2

    def test_system_messages_excluded_from_brain_history(self) -> None:
        from nikola.domain.entities.message import Message

        svc, _ = _service()
        conv = svc.create_conversation(SessionId.generate())
        # Directly add a SYSTEM message bypassing the validator (system injection)
        sys_msg = Message.create(
            conversation_id=conv.id, role=MessageRole.SYSTEM, content="you are nikola"
        )
        conv.add_message(sys_msg)
        svc._repository.save(conv)
        svc.add_message(conv.id, MessageRole.USER, "hi")
        history = svc.get_history_for_brain(conv.id)
        assert len(history) == 1
        assert history[0].role == "user"


@pytest.mark.unit
class TestConversationServiceArchive:
    def test_archive_sets_status(self) -> None:
        svc, _ = _service()
        conv = svc.create_conversation(SessionId.generate())
        svc.archive_conversation(conv.id)
        assert svc.get_conversation(conv.id).status is ConversationStatus.ARCHIVED

    def test_archive_unknown_conversation_raises(self) -> None:
        from nikola.domain.value_objects.conversation_id import ConversationId

        svc, _ = _service()
        with pytest.raises(ConversationError):
            svc.archive_conversation(ConversationId.generate())


@pytest.mark.unit
class TestConversationServiceListActiveForSession:
    def test_returns_only_active_conversations(self) -> None:
        svc, _ = _service()
        sid = SessionId.generate()
        active = svc.create_conversation(sid)
        archived = svc.create_conversation(sid)
        svc.archive_conversation(archived.id)
        result = svc.list_active_for_session(sid)
        assert active in result
        assert archived not in result

    def test_returns_empty_list_for_session_with_no_conversations(self) -> None:
        svc, _ = _service()
        assert svc.list_active_for_session(SessionId.generate()) == []
