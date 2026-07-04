"""`NullBrain` — a fully functional, zero-external-call `BrainPort` implementation.

`NullBrain` is NOT a stub that raises `NotImplementedError`. It is a
working `BrainPort` that returns deterministic, scripted `ReasoningResponse`
objects. Its purpose is threefold:

1. **Default wiring**: the composition root registers `NullBrain` as the
   active Brain when `brain.provider = "null"` (the safe default that
   requires no API key). This means `compose()` and the DI container
   work correctly from Sprint 6 onward, with real `BrainPort.reason()`
   calls returning valid responses.

2. **Testing**: unit tests for Planner, Orchestrator, Agent, and
   IntentClassifier (future sprints) can inject `NullBrain` or a
   subclass with overridden responses to exercise their logic without
   needing an API key or network access in CI.

3. **Architecture proof**: the existence of a working `NullBrain` proves
   that the `BrainPort` contract is complete and implementable without
   any AI SDK — a concrete demonstration that the port is correctly
   designed, not just aspirational.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.domain.ports.brain_port import BrainPort
from nikola.domain.value_objects.intent import Intent, IntentType

if TYPE_CHECKING:
    from nikola.domain.entities.reasoning_request import ReasoningRequest
    from nikola.domain.entities.reasoning_response import ReasoningResponse

__all__ = ["NullBrain"]


class NullBrain(BrainPort):
    """A deterministic, no-network `BrainPort` implementation.

    `NullBrain` always returns a `ReasoningResponse` with:
    - `intent_type = IntentType.CHAT` and `confidence = 1.0`
    - `content` echoing back the request content prefixed with a marker
    - `model_used = "null"`
    - `finish_reason = "stop"`
    - No tool invocation (`tool_name = None`, `tool_args = None`)

    This deterministic behavior makes test assertions straightforward:
    given a known `ReasoningRequest.content`, the response is fully
    predictable without mocking.
    """

    @property
    def provider_name(self) -> str:
        return "null"

    def reason(self, request: ReasoningRequest) -> ReasoningResponse:
        """Return a deterministic CHAT response echoing the request content.

        Args:
            request: The reasoning input. Its `content` is echoed in the
                response so test assertions can verify the request
                round-tripped correctly.

        Returns:
            A `ReasoningResponse` with `intent_type = CHAT`, no tool
            invocation, and `model_used = "null"`.
        """
        from nikola.domain.entities.reasoning_response import ReasoningResponse

        return ReasoningResponse(
            content=f"[NullBrain] {request.content}",
            intent=Intent(intent_type=IntentType.CHAT, confidence=1.0),
            model_used="null",
            tool_name=None,
            tool_args=None,
            finish_reason="stop",
        )
