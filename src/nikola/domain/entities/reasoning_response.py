"""`ReasoningResponse` — the structured output produced by a `BrainPort`.

A `ReasoningResponse` is what the Brain returns after processing a
`ReasoningRequest`. It carries both the natural-language content of the
reply (if any) and the Brain's classification of what should happen next
(the `Intent`). Downstream code — Planner, Agent, Orchestrator — uses
the `Intent` to decide what to do next without having to parse free-form
text themselves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.value_objects.intent import Intent

__all__ = ["ReasoningResponse"]


@dataclass(frozen=True, slots=True)
class ReasoningResponse:
    """The structured output produced by a `BrainPort` for a single reasoning cycle.

    Attributes:
        content: The Brain's natural-language reply. May be empty when
            the Brain produced only a tool invocation request (i.e.
            `intent.intent_type is IntentType.TOOL_INVOCATION` and there
            is no accompanying explanation text).
        intent: The Brain's classification of what this response implies
            should happen next (chat reply, tool call, etc.).
        tool_name: The name of the tool the Brain wants to invoke, when
            `intent.intent_type is IntentType.TOOL_INVOCATION`. `None`
            for all other intent types. Unvalidated at this layer — the
            Tool Registry (a later sprint) validates tool existence.
        tool_args: The arguments the Brain wants to pass to `tool_name`,
            as a plain dict of raw values. `None` when no tool is
            requested. Schema validation is deferred to the Tool
            Registry, which owns the tool manifests.
        model_used: A human-readable identifier for the model that
            produced this response (e.g. `"null"`, `"claude-3-5-sonnet"`,
            `"gpt-4o"`). Used for audit logging and observability.
        finish_reason: Why the Brain stopped generating — e.g. `"stop"`
            (natural end), `"length"` (context limit hit), `"tool_call"`
            (invoking a tool). Adapter-defined; `"stop"` is the standard
            value for a normally completed response.
    """

    content: str
    intent: Intent
    model_used: str
    tool_name: str | None = field(default=None)
    tool_args: dict[str, object] | None = field(default=None)
    finish_reason: str = field(default="stop")

    def __post_init__(self) -> None:
        from nikola.domain.value_objects.intent import IntentType

        if self.tool_name is not None and not self.tool_name.strip():
            raise ValueError("ReasoningResponse.tool_name must not be blank when set.")

        if self.intent.intent_type is IntentType.TOOL_INVOCATION and self.tool_name is None:
            raise ValueError(
                "ReasoningResponse.tool_name must be set when " "intent_type is TOOL_INVOCATION."
            )
