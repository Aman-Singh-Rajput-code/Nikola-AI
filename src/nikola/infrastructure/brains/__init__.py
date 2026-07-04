"""LLM provider adapters implementing `BrainPort`.

Sprint 6 delivers:
- `NullBrain` — a deterministic, zero-external-call `BrainPort` for
  testing and safe-default wiring.
- `BrainRegistry` — maps provider name strings to factory callables.
- `BrainFactory` — reads `BrainSettings.provider` and builds the
  configured adapter via the registry.
- `build_default_registry()` — constructs a registry with all currently
  available providers pre-registered.

Concrete providers (Claude, OpenAI, Gemini, Ollama) are implemented in
later sprints; each will call `registry.register()` to add itself.
"""

from nikola.infrastructure.brains.brain_factory import BrainFactory, build_default_registry
from nikola.infrastructure.brains.brain_registry import BrainRegistry
from nikola.infrastructure.brains.null_brain import NullBrain

__all__ = [
    "NullBrain",
    "BrainRegistry",
    "BrainFactory",
    "build_default_registry",
]
