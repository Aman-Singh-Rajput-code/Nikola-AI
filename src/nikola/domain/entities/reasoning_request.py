"""`ReasoningRequest` — the structured input handed to a `BrainPort`.

A `ReasoningRequest` is assembled by the Orchestrator (a future sprint)
from whatever the user typed or spoke, plus relevant context from Memory
and available Tool names, before being handed to the Brain for reasoning.
It is intentionally *not* a raw prompt string: keeping it structured means
each Brain adapter is responsible for its own prompt engineering, and the
rest of the application never needs to know that prompts exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["ConversationTurn", "ReasoningRequest"]


@dataclass(frozen=True, slots=True)
class ConversationTurn:
    """A single prior turn in a conversation, provided as context.

    Attributes:
        role: Who produced this turn — `"user"` or `"assistant"`.
        content: The text of the turn.
    """

    role: str
    content: str

    def __post_init__(self) -> None:
        if self.role not in ("user", "assistant", "tool"):
            raise ValueError(
                f"ConversationTurn.role must be 'user', 'assistant', or 'tool', "
                f"got {self.role!r}."
            )
        if not self.content.strip():
            raise ValueError("ConversationTurn.content must not be empty.")


@dataclass(frozen=True, slots=True)
class ReasoningRequest:
    """The structured input a `BrainPort` receives for a single reasoning cycle.

    Attributes:
        content: The raw user input — the thing the Brain is being asked
            to reason about. Must be non-empty.
        conversation_history: Prior turns in the current conversation,
            in chronological order (oldest first), provided so the Brain
            can reason in context. Empty for the first turn of a session.
        available_tools: Names (and optionally short descriptions) of
            tools the Brain may choose to invoke. Provided as plain
            strings at this stage; the Tool Registry (a later sprint)
            will supply richer schemas. Empty when no tools are available.
        system_context: An optional hint about the operational context
            (e.g. `"You are Nikola AI, a personal assistant..."`). Each
            Brain adapter may incorporate this into its provider-specific
            system prompt however it sees fit.
    """

    content: str
    conversation_history: tuple[ConversationTurn, ...] = field(default_factory=tuple)
    available_tools: tuple[str, ...] = field(default_factory=tuple)
    system_context: str | None = field(default=None)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("ReasoningRequest.content must not be empty.")
