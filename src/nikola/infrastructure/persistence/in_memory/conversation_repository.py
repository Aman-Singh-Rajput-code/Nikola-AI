"""`InMemoryConversationRepository` — dict-backed `ConversationRepositoryPort`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.domain.ports.conversation_repository_port import ConversationRepositoryPort

if TYPE_CHECKING:
    from nikola.domain.entities.conversation import Conversation
    from nikola.domain.value_objects.conversation_id import ConversationId
    from nikola.domain.value_objects.session_id import SessionId

__all__ = ["InMemoryConversationRepository"]


class InMemoryConversationRepository(ConversationRepositoryPort):
    """In-process, dict-backed conversation repository.

    Sprint 7's sole persistence adapter. Data exists only for the lifetime
    of the process. Thread-unsafe by design — single-threaded startup context.
    """

    def __init__(self) -> None:
        self._store: dict[str, Conversation] = {}

    def save(self, conversation: Conversation) -> None:
        """Persist `conversation`, creating or updating it in the store."""
        self._store[conversation.id.value] = conversation

    def get(self, conversation_id: ConversationId) -> Conversation | None:
        """Return the conversation with `conversation_id`, or `None`."""
        return self._store.get(conversation_id.value)

    def list_by_session(self, session_id: SessionId) -> list[Conversation]:
        """Return all conversations whose `session_id` matches."""
        return [c for c in self._store.values() if c.session_id == session_id]

    def delete(self, conversation_id: ConversationId) -> None:
        """Remove the conversation; no-op if absent."""
        self._store.pop(conversation_id.value, None)

    @property
    def count(self) -> int:
        """Number of conversations currently in the store."""
        return len(self._store)
