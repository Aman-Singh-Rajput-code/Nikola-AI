"""Unit tests for `nikola.infrastructure.persistence.in_memory.InMemoryConversationRepository`."""

from __future__ import annotations

import pytest

from nikola.domain.entities.conversation import Conversation
from nikola.domain.ports.conversation_repository_port import ConversationRepositoryPort
from nikola.domain.value_objects.conversation_id import ConversationId
from nikola.domain.value_objects.session_id import SessionId
from nikola.infrastructure.persistence.in_memory import InMemoryConversationRepository


def _session() -> SessionId:
    return SessionId.generate()


def _conversation(session_id: SessionId | None = None) -> Conversation:
    return Conversation.create(session_id=session_id or _session())


@pytest.mark.unit
class TestInMemoryConversationRepositoryIsAPort:
    def test_is_a_conversation_repository_port(self) -> None:
        assert isinstance(InMemoryConversationRepository(), ConversationRepositoryPort)


@pytest.mark.unit
class TestInMemoryConversationRepositorySave:
    def test_save_stores_a_conversation(self) -> None:
        repo = InMemoryConversationRepository()
        conv = _conversation()
        repo.save(conv)
        assert repo.count == 1

    def test_save_is_idempotent_for_same_id(self) -> None:
        repo = InMemoryConversationRepository()
        conv = _conversation()
        repo.save(conv)
        repo.save(conv)
        assert repo.count == 1

    def test_save_updates_existing_conversation(self) -> None:
        from nikola.domain.entities.message import Message
        from nikola.domain.value_objects.enums import MessageRole

        repo = InMemoryConversationRepository()
        conv = _conversation()
        repo.save(conv)

        msg = Message.create(conversation_id=conv.id, role=MessageRole.USER, content="hi")
        conv.add_message(msg)
        repo.save(conv)

        retrieved = repo.get(conv.id)
        assert retrieved is not None
        assert retrieved.message_count == 1


@pytest.mark.unit
class TestInMemoryConversationRepositoryGet:
    def test_get_returns_saved_conversation(self) -> None:
        repo = InMemoryConversationRepository()
        conv = _conversation()
        repo.save(conv)
        assert repo.get(conv.id) is conv

    def test_get_returns_none_for_unknown_id(self) -> None:
        repo = InMemoryConversationRepository()
        assert repo.get(ConversationId.generate()) is None


@pytest.mark.unit
class TestInMemoryConversationRepositoryListBySession:
    def test_returns_conversations_for_session(self) -> None:
        repo = InMemoryConversationRepository()
        sid = _session()
        c1 = _conversation(sid)
        c2 = _conversation(sid)
        other = _conversation()
        for c in (c1, c2, other):
            repo.save(c)

        result = repo.list_by_session(sid)
        assert len(result) == 2
        assert other not in result

    def test_returns_empty_list_for_unknown_session(self) -> None:
        repo = InMemoryConversationRepository()
        assert repo.list_by_session(_session()) == []


@pytest.mark.unit
class TestInMemoryConversationRepositoryDelete:
    def test_delete_removes_conversation(self) -> None:
        repo = InMemoryConversationRepository()
        conv = _conversation()
        repo.save(conv)
        repo.delete(conv.id)
        assert repo.get(conv.id) is None
        assert repo.count == 0

    def test_delete_unknown_id_is_a_no_op(self) -> None:
        repo = InMemoryConversationRepository()
        repo.delete(ConversationId.generate())  # must not raise
