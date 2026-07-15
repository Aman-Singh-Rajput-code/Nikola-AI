"""`ConversationRepositoryPort` — abstract persistence contract for `Conversation`."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.entities.conversation import Conversation
    from nikola.domain.value_objects.conversation_id import ConversationId
    from nikola.domain.value_objects.session_id import SessionId

__all__ = ["ConversationRepositoryPort"]


class ConversationRepositoryPort(ABC):
    """Abstract persistence interface for `Conversation` entities."""

    @abstractmethod
    def save(self, conversation: Conversation) -> None:
        """Persist `conversation`, creating or updating it as necessary."""
        raise NotImplementedError

    @abstractmethod
    def get(self, conversation_id: ConversationId) -> Conversation | None:
        """Return the `Conversation` with `conversation_id`, or `None`."""
        raise NotImplementedError

    @abstractmethod
    def list_by_session(self, session_id: SessionId) -> list[Conversation]:
        """Return all `Conversation`s belonging to `session_id`."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, conversation_id: ConversationId) -> None:
        """Remove the conversation with `conversation_id`; no-op if absent."""
        raise NotImplementedError
