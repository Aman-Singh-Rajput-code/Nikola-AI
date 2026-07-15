"""`ConversationService` — primary use-case service for conversation operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.application.conversation.conversation_validator import ConversationValidator
from nikola.domain.entities.conversation import Conversation
from nikola.domain.entities.message import Message
from nikola.domain.value_objects.enums import ConversationStatus, MessageRole

if TYPE_CHECKING:
    from nikola.domain.entities.reasoning_request import ConversationTurn
    from nikola.domain.ports.conversation_repository_port import ConversationRepositoryPort
    from nikola.domain.value_objects.conversation_id import ConversationId
    from nikola.domain.value_objects.session_id import SessionId

__all__ = ["ConversationService"]


class ConversationService:
    """Orchestrates conversation lifecycle: creation, message addition, retrieval.

    Depends on ConversationRepositoryPort for persistence and
    ConversationValidator for stateless rule enforcement.
    """

    def __init__(self, repository: ConversationRepositoryPort) -> None:
        self._repository = repository
        self._validator = ConversationValidator()

    def create_conversation(self, session_id: SessionId) -> Conversation:
        """Create and persist a new ACTIVE conversation for `session_id`."""
        conversation = Conversation.create(session_id=session_id)
        self._repository.save(conversation)
        return conversation

    def add_message(
        self,
        conversation_id: ConversationId,
        role: MessageRole,
        content: str,
    ) -> Message:
        """Add a new message to an existing conversation.

        Raises:
            ConversationError: If the conversation doesn't exist or isn't ACTIVE.
            MessageValidationError: If content is empty or role is SYSTEM.
        """
        conversation = self._validator.validate_conversation_exists(
            self._repository.get(conversation_id),
            conversation_id,
        )
        self._validator.validate_can_add_message(conversation, role, content)
        message = Message.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        conversation.add_message(message)
        self._repository.save(conversation)
        return message

    def get_conversation(self, conversation_id: ConversationId) -> Conversation:
        """Return the conversation with `conversation_id`.

        Raises:
            ConversationError: If no conversation with that id exists.
        """
        return self._validator.validate_conversation_exists(
            self._repository.get(conversation_id),
            conversation_id,
        )

    def get_history_for_brain(
        self, conversation_id: ConversationId
    ) -> tuple[ConversationTurn, ...]:
        """Return conversation history as ConversationTurn objects for Brain input."""
        conversation = self.get_conversation(conversation_id)
        return conversation.get_history_for_brain()

    def archive_conversation(self, conversation_id: ConversationId) -> None:
        """Archive the conversation, making it read-only.

        Raises:
            ConversationError: If conversation doesn't exist or isn't ACTIVE.
        """
        conversation = self._validator.validate_conversation_exists(
            self._repository.get(conversation_id),
            conversation_id,
        )
        conversation.archive()
        self._repository.save(conversation)

    def list_active_for_session(self, session_id: SessionId) -> list[Conversation]:
        """Return all ACTIVE conversations belonging to `session_id`."""
        all_conversations = self._repository.list_by_session(session_id)
        return [c for c in all_conversations if c.status is ConversationStatus.ACTIVE]
