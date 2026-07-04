"""`IntentType` and `Intent` — the Brain's classification of a request.

When the Brain processes a `ReasoningRequest` it does two things: produces
a reply (captured in `ReasoningResponse.content`) and classifies *what kind
of action the request implies* (captured as an `Intent`). The `Intent` is
what the Planner and Agent use to decide where to route execution next.

Both types are pure domain value objects: immutable, zero infrastructure
dependencies, comparable by value.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

__all__ = ["IntentType", "Intent"]


class IntentType(StrEnum):
    """The category of action a `ReasoningRequest` implies.

    - `CHAT`: the user wants a conversational reply with no external action.
    - `TOOL_INVOCATION`: the Brain determined that a specific tool should
      be called to satisfy the request.
    - `CLARIFICATION_NEEDED`: the request is ambiguous; the Brain needs
      more information before it can reason about it meaningfully.
    - `OUT_OF_SCOPE`: the request is something Nikola AI cannot or should
      not handle (e.g. a request that violates permissions policy).
    """

    CHAT = "chat"
    TOOL_INVOCATION = "tool_invocation"
    CLARIFICATION_NEEDED = "clarification_needed"
    OUT_OF_SCOPE = "out_of_scope"


@dataclass(frozen=True, slots=True)
class Intent:
    """The Brain's classification of what a `ReasoningRequest` intends.

    An `Intent` is produced as part of a `ReasoningResponse` — it is the
    Brain's answer to the question "what kind of action does this request
    imply?" rather than the actual content of the reply.

    Attributes:
        intent_type: The coarse category of action the request implies.
        confidence: The Brain's self-reported confidence in this
            classification, in the range [0.0, 1.0]. A value of 1.0
            means fully certain; 0.0 means no confidence at all.
            Defaults to 1.0 for deterministic/non-probabilistic Brains
            (e.g. `NullBrain`).
        reasoning: An optional, human-readable explanation of why the
            Brain classified the request this way. Used for
            explainability and audit logging.
    """

    intent_type: IntentType
    confidence: float = field(default=1.0)
    reasoning: str | None = field(default=None)

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Intent.confidence must be in [0.0, 1.0], got {self.confidence!r}.")
