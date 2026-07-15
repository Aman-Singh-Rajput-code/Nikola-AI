"""`ConversationManager` — session-level coordinator for conversations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.application.conversation.conversation_service import ConversationService  # noqa: TC001
from nikola.domain.value_objects.enums import MessageRole

if TYPE_CHECKING:
    from nikola.domain.entities.conversation import Conversation
    from nikola.domain.entities.message import Message
    from nikola.domain.entities.reasoning_request import ConversationTurn
    from nikola.domain.value_objects.conversation_id import ConversationId
    from nikola.domain.value_objects.session_id import SessionId

__all__ = ["ConversationManager"]


class ConversationManager:
    """Coordinates conversation lifecycle at the session level.

    The primary entry point for the Orchestrator (future sprints).
    Provides the find-or-create pattern and role-specific message helpers.
    """

    def __init__(self, service: ConversationService) -> None:
        self._service = service

    def get_or_create_active_conversation(self, session_id: SessionId) -> Conversation:
        """Return the current active conversation, creating one if needed.

        If the session has active conversations, returns the most recently
        updated. Otherwise creates a fresh one.
        """
        active = self._service.list_active_for_session(session_id)
        if active:
            return max(active, key=lambda c: c.updated_at)
        return self._service.create_conversation(session_id)

    def add_user_message(self, conversation_id: ConversationId, content: str) -> Message:
        """Add a USER-role message to the conversation."""
        return self._service.add_message(conversation_id, MessageRole.USER, content)

    def add_assistant_message(self, conversation_id: ConversationId, content: str) -> Message:
        """Add an ASSISTANT-role message to the conversation."""
        return self._service.add_message(conversation_id, MessageRole.ASSISTANT, content)

    def add_tool_result(self, conversation_id: ConversationId, content: str) -> Message:
        """Add a TOOL-role message (tool result) to the conversation."""
        return self._service.add_message(conversation_id, MessageRole.TOOL, content)

    def get_brain_context(self, conversation_id: ConversationId) -> tuple[ConversationTurn, ...]:
        """Return conversation history as Brain-ready ConversationTurn objects."""
        return self._service.get_history_for_brain(conversation_id)
