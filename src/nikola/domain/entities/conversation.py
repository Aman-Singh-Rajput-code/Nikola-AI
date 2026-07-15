"""`Conversation` — a durable record of an exchange between user and Nikola AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from nikola.domain.errors.domain_errors import ConversationError, MessageValidationError
from nikola.domain.value_objects.conversation_id import ConversationId
from nikola.domain.value_objects.enums import ConversationStatus, MessageRole

if TYPE_CHECKING:
    from nikola.domain.entities.message import Message
    from nikola.domain.entities.reasoning_request import ConversationTurn
    from nikola.domain.value_objects.session_id import SessionId

__all__ = ["Conversation"]

_BRAIN_CONTEXT_ROLES: frozenset[MessageRole] = frozenset(
    {MessageRole.USER, MessageRole.ASSISTANT, MessageRole.TOOL}
)


@dataclass(slots=True)
class Conversation:
    """A durable, ordered record of messages between a user and Nikola AI.

    Attributes:
        id: The conversation's unique identifier.
        session_id: The Session within which this conversation takes place.
        status: The conversation's current lifecycle state.
        created_at: When the conversation was created, in UTC.
        updated_at: When last mutated, in UTC.
    """

    id: ConversationId
    session_id: SessionId
    status: ConversationStatus = ConversationStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _messages: list[Message] = field(default_factory=list, repr=False)

    @classmethod
    def create(cls, *, session_id: SessionId) -> Conversation:
        """Construct a new, empty ACTIVE Conversation."""
        return cls(id=ConversationId.generate(), session_id=session_id)

    @property
    def messages(self) -> tuple[Message, ...]:
        """All messages, oldest first, as an immutable tuple."""
        return tuple(self._messages)

    @property
    def message_count(self) -> int:
        """The number of messages recorded so far."""
        return len(self._messages)

    @property
    def is_active(self) -> bool:
        """Whether this conversation is currently accepting new messages."""
        return self.status is ConversationStatus.ACTIVE

    def add_message(self, message: Message) -> None:
        """Append `message` to this conversation's history.

        Raises:
            ConversationError: If this conversation is not ACTIVE.
            MessageValidationError: If message.conversation_id doesn't match.
        """
        if self.status is not ConversationStatus.ACTIVE:
            raise ConversationError(
                f"Cannot add a message to a conversation with status "
                f"'{self.status}'. Only ACTIVE conversations accept new messages."
            )
        if message.conversation_id != self.id:
            raise MessageValidationError(
                f"Message conversation_id '{message.conversation_id}' does not "
                f"match this conversation's id '{self.id}'."
            )
        self._messages.append(message)
        self.updated_at = datetime.now(UTC)

    def archive(self) -> None:
        """Transition from ACTIVE to ARCHIVED.

        Raises:
            ConversationError: If this conversation is not ACTIVE.
        """
        if self.status is not ConversationStatus.ACTIVE:
            raise ConversationError(
                f"Cannot archive a conversation with status '{self.status}'. "
                f"Only ACTIVE conversations can be archived."
            )
        self.status = ConversationStatus.ARCHIVED
        self.updated_at = datetime.now(UTC)

    def soft_delete(self) -> None:
        """Transition to DELETED (terminal).

        Raises:
            ConversationError: If this conversation is already DELETED.
        """
        if self.status is ConversationStatus.DELETED:
            raise ConversationError("Cannot delete a conversation that is already DELETED.")
        self.status = ConversationStatus.DELETED
        self.updated_at = datetime.now(UTC)

    def get_history_for_brain(self) -> tuple[ConversationTurn, ...]:
        """Return messages as ConversationTurn objects for Brain input.

        Excludes SYSTEM messages (injected separately as system_context).
        """
        from nikola.domain.entities.reasoning_request import ConversationTurn

        return tuple(
            ConversationTurn(role=msg.role.value, content=msg.content)
            for msg in self._messages
            if msg.role in _BRAIN_CONTEXT_ROLES
        )
