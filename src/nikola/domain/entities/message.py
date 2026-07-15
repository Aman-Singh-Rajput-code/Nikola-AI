"""`Message` — an immutable record of a single turn in a `Conversation`."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from nikola.domain.errors.domain_errors import MessageValidationError
from nikola.domain.value_objects.message_id import MessageId

if TYPE_CHECKING:
    from nikola.domain.value_objects.conversation_id import ConversationId
    from nikola.domain.value_objects.enums import MessageRole

__all__ = ["Message"]


@dataclass(frozen=True, slots=True)
class Message:
    """An immutable record of a single turn in a `Conversation`.

    Attributes:
        id: The message's unique identifier.
        conversation_id: The `Conversation` this message belongs to.
        role: Who produced this message — USER, ASSISTANT, SYSTEM, or TOOL.
        content: The text of the message. Must be non-empty.
        created_at: When the message was created, in UTC.

    Raises:
        MessageValidationError: If `content` is empty or whitespace-only.
    """

    id: MessageId
    conversation_id: ConversationId
    role: MessageRole
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise MessageValidationError("Message content must not be empty or whitespace-only.")

    @classmethod
    def create(
        cls,
        *,
        conversation_id: ConversationId,
        role: MessageRole,
        content: str,
    ) -> Message:
        """Construct a new `Message` with a freshly generated `MessageId`."""
        return cls(
            id=MessageId.generate(),
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
