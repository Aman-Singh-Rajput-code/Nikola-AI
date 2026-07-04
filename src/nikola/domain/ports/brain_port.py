"""`BrainPort` — the provider-agnostic reasoning interface.

This is the single contract that all Brain adapters (Claude, OpenAI,
Gemini, Ollama, local models, `NullBrain`) must satisfy. The rest of
Nikola AI — Planner, Agent, Orchestrator, `IntentClassifier` — depends
only on this port, never on any concrete adapter. This means:

- Swapping the active provider requires only a config change
  (`NIKOLA_BRAIN__PROVIDER=claude`), not a code change.
- Unit tests can inject any implementation that satisfies this port
  (typically `NullBrain` or a hand-rolled fake) without needing API keys.
- The port itself has zero third-party dependencies — it imports only
  pure domain types.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.entities.reasoning_request import ReasoningRequest
    from nikola.domain.entities.reasoning_response import ReasoningResponse

__all__ = ["BrainPort"]


class BrainPort(ABC):
    """Abstract interface that all AI reasoning backends must implement.

    A `BrainPort` implementation receives a fully structured
    `ReasoningRequest` — assembled from user input, conversation history,
    memory context, and available tool names — and returns a
    `ReasoningResponse` carrying the natural-language reply, the
    classified `Intent`, and any tool the Brain wants to invoke.

    Implementations are responsible for:
    - Translating the provider-agnostic `ReasoningRequest` into their
      provider's specific API format (prompt, messages array, etc.).
    - Translating the provider's response back into a `ReasoningResponse`.
    - Handling provider-specific errors (rate limits, timeouts, malformed
      responses) and re-raising them as `BrainError`.

    Implementations are explicitly NOT responsible for:
    - Prompt engineering beyond the minimum needed to translate the
      structured request (use `system_context` if needed).
    - Filesystem access, browser automation, or terminal execution.
    - Any action other than reasoning and returning a structured response.
    """

    @abstractmethod
    def reason(self, request: ReasoningRequest) -> ReasoningResponse:
        """Process `request` and return a structured reasoning response.

        This is the sole method all Brain adapters must implement. The
        caller guarantees that `request` has already been validated (it
        is a frozen dataclass with non-empty `content`). The
        implementation must either return a valid `ReasoningResponse` or
        raise `BrainError`.

        Args:
            request: The structured, immutable reasoning input assembled
                by the Orchestrator or a use-case service.

        Returns:
            A `ReasoningResponse` carrying the reply content, the
            classified `Intent`, and any tool invocation request.

        Raises:
            nikola.domain.errors.BrainError: If the Brain fails to
                produce a response for any reason (provider error,
                context window exceeded, malformed response, etc.).
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """A short, human-readable identifier for this Brain's provider.

        Used in `ReasoningResponse.model_used`, logs, and the
        `BrainRegistry` key. Examples: `"null"`, `"claude"`, `"openai"`,
        `"ollama"`.
        """
        raise NotImplementedError
