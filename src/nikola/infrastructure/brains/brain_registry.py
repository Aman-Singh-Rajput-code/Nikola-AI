"""`BrainRegistry` — maps provider name strings to `BrainPort` factory callables.

The registry is the extension point for adding new Brain providers. Each
provider adapter, when it exists, registers itself here with a short name
that matches the `brain.provider` config value. Sprint 6 registers only
`"null"` (the `NullBrain`). Future sprints add `"claude"`, `"openai"`,
`"gemini"`, `"ollama"` as their adapters are implemented.

The registry stores *factories* (`Callable[[], BrainPort]`), not
pre-built instances, so each `BrainFactory.create()` call gets a fresh
adapter instance. Singleton lifecycle is the DI container's responsibility
(via `compose()`'s `register_singleton`), not the registry's.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.domain.errors import BrainError

if TYPE_CHECKING:
    from collections.abc import Callable

    from nikola.domain.ports.brain_port import BrainPort

__all__ = ["BrainRegistry"]


class BrainRegistry:
    """A mutable registry mapping provider names to `BrainPort` factory callables.

    Typical usage (in `bootstrap/compose.py` or an adapter's own module):

        registry = BrainRegistry()
        registry.register("null", NullBrain)
        brain = registry.create("null")  # -> NullBrain()

    Each registered factory is a zero-argument callable that produces a
    fresh `BrainPort` instance. This keeps the registry itself stateless
    with respect to Brain instances — lifetime management is delegated to
    the DI container in `compose()`.
    """

    def __init__(self) -> None:
        self._factories: dict[str, Callable[[], BrainPort]] = {}

    def register(self, name: str, factory: Callable[[], BrainPort]) -> None:
        """Register `factory` under `name`.

        Args:
            name: The short provider identifier that `brain.provider` in
                config must match to select this Brain (e.g. `"null"`,
                `"claude"`, `"openai"`). Case-sensitive; use lowercase
                by convention.
            factory: A zero-argument callable that constructs and returns
                a fresh `BrainPort` instance.
        """
        self._factories[name] = factory

    def create(self, name: str) -> BrainPort:
        """Construct and return a `BrainPort` for provider `name`.

        Args:
            name: The provider name to look up (must have been previously
                registered with `register()`).

        Returns:
            A fresh `BrainPort` instance produced by the registered factory.

        Raises:
            BrainError: If `name` is not registered. The error message
                lists all available registered names to help diagnose a
                misconfigured `brain.provider` value.
        """
        factory = self._factories.get(name)
        if factory is None:
            available = sorted(self._factories.keys())
            raise BrainError(
                f"Brain provider '{name}' is not registered. "
                f"Available providers: {available}. "
                f"Check the 'brain.provider' configuration value."
            )
        return factory()

    def registered_names(self) -> list[str]:
        """Return a sorted list of all currently registered provider names."""
        return sorted(self._factories.keys())

    def is_registered(self, name: str) -> bool:
        """Return whether `name` has a registered factory."""
        return name in self._factories
