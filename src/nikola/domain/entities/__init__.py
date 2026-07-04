"""Domain entities.

Sprint 4 adds `Command`, `Task`, `Response`, and `Session` — the core
entities modeling a single request/execution/outcome cycle within an
interaction context. Sprint 6 adds `ReasoningRequest`, `ReasoningResponse`,
and `ConversationTurn` — the structured data shapes crossing the BrainPort
boundary. Plan, Step, ToolCall, Permission, MemoryItem, AgentProfile, and
Policy are implemented in later sprints.
"""

from nikola.domain.entities.command import Command
from nikola.domain.entities.reasoning_request import ConversationTurn, ReasoningRequest
from nikola.domain.entities.reasoning_response import ReasoningResponse
from nikola.domain.entities.response import Response
from nikola.domain.entities.session import Session
from nikola.domain.entities.task import Task

__all__ = [
    "Command",
    "Task",
    "Response",
    "Session",
    "ReasoningRequest",
    "ReasoningResponse",
    "ConversationTurn",
]
