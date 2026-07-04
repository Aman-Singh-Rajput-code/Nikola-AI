"""`BrainFactory` — reads the active Brain provider from config and builds it.

`BrainFactory` is the bridge between the configuration system (which says
*which* provider to use) and the `BrainRegistry` (which knows *how* to
build each provider). `compose()` uses `BrainFactory` to build the
`BrainPort` singleton that the rest of the application resolves.

This separation matters:
- `BrainRegistry` is provider-knowledge (what exists and how to build it).
- `BrainFactory` is wiring-knowledge (which one did the operator choose).
- Neither concerns the DI container or the composition root directly —
  the composition root just calls `BrainFactory.create_from_config()`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.infrastructure.brains.brain_registry import BrainRegistry
from nikola.infrastructure.brains.null_brain import NullBrain

if TYPE_CHECKING:
    from nikola.domain.ports.brain_port import BrainPort
    from nikola.infrastructure.config.settings import BrainSettings

__all__ = ["BrainFactory", "build_default_registry"]


def build_default_registry() -> BrainRegistry:
    """Build a `BrainRegistry` with all currently available providers registered.

    Sprint 6 registers only `"null"`. Future sprints add their concrete
    adapters here without changing this function's signature or the
    composition root that calls it.

    Returns:
        A `BrainRegistry` with the `"null"` provider registered, ready to
        be passed to `BrainFactory`.
    """
    registry = BrainRegistry()
    registry.register("null", NullBrain)
    return registry


class BrainFactory:
    """Selects and builds the configured `BrainPort` implementation.

    Reads `BrainSettings.provider` from the application's configuration
    and delegates construction to the `BrainRegistry`. The factory holds
    no state after construction — it is a one-shot building service.

    Attributes:
        _registry: The provider registry to look up factories from.
    """

    def __init__(self, registry: BrainRegistry) -> None:
        self._registry = registry

    def create_from_settings(self, settings: BrainSettings) -> BrainPort:
        """Build the `BrainPort` configured in `settings`.

        Args:
            settings: The `BrainSettings` section of the application's
                `NikolaSettings`, carrying the `provider` name to use.

        Returns:
            A fresh `BrainPort` instance for the configured provider.

        Raises:
            nikola.domain.errors.BrainError: If `settings.provider` is
                not registered in the registry.
        """
        return self._registry.create(settings.provider)
