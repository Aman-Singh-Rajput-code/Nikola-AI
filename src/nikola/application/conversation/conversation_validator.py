"""`ConversationValidator` — stateless application-boundary validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.domain.errors import ConversationError, MessageValidationError
from nikola.domain.value_objects.enums import ConversationStatus, MessageRole

if TYPE_CHECKING:
    from nikola.domain.entities.conversation import Conversation

__all__ = ["ConversationValidator"]

_ALLOWED_ADD_ROLES: frozenset[MessageRole] = frozenset(
    {MessageRole.USER, MessageRole.ASSISTANT, MessageRole.TOOL}
)


class ConversationValidator:
    """Stateless validator for conversation-layer business rules.

    Instantiate once and reuse — this class holds no state.
    `ConversationService` owns and delegates to an instance of this class.
    """

    def validate_can_add_message(
        self,
        conversation: Conversation,
        role: MessageRole,
        content: str,
    ) -> None:
        """Assert that a message with `role` and `content` may be added.

        Raises:
            ConversationError: If the conversation is not ACTIVE.
            MessageValidationError: If content is empty or role is SYSTEM.
        """
        if conversation.status is not ConversationStatus.ACTIVE:
            raise ConversationError(
                f"Cannot add a message to a conversation with status "
                f"'{conversation.status}'. The conversation must be ACTIVE."
            )
        if not content.strip():
            raise MessageValidationError("Message content must not be empty or whitespace-only.")
        if role not in _ALLOWED_ADD_ROLES:
            raise MessageValidationError(
                f"Role '{role}' is not permitted via add_message. "
                f"SYSTEM messages are injected at conversation creation only. "
                f"Allowed roles: {sorted(r.value for r in _ALLOWED_ADD_ROLES)}."
            )

    def validate_conversation_exists(
        self,
        conversation: Conversation | None,
        conversation_id: object,
    ) -> Conversation:
        """Assert that `conversation` is not None and return it.

        Raises:
            ConversationError: If `conversation` is None.
        """
        if conversation is None:
            raise ConversationError(f"Conversation '{conversation_id}' was not found.")
        return conversation
