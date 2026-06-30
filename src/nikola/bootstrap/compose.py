"""The composition root: builds a fully wired `ServiceContainer` for Nikola AI.

This is the one module allowed to import concrete classes from every layer
together — `ServiceContainer` (this package), `EnvConfigProvider` and
`setup_logging`/`get_logger` (infrastructure), and the domain ports they
implement. Nothing outside `bootstrap/` should import infrastructure
concrete classes directly; everything should go through `compose()` and
resolve against ports.

Sprint 5 registers exactly the two infrastructure systems that exist so
far: configuration (`ConfigProviderPort`) and logging initialization
(`LoggingInitialized`). Each future sprint that introduces a new
infrastructure adapter (a Brain provider, a persistence repository, the
event bus, ...) adds one more `container.register_*` call here — this
function is expected to grow over time, by design.
"""

from __future__ import annotations

from dataclasses import dataclass

from nikola.bootstrap.container import ServiceContainer
from nikola.domain.ports import ConfigProviderPort
from nikola.infrastructure.config import EnvConfigProvider
from nikola.infrastructure.logging import get_logger, setup_logging

__all__ = ["compose", "LoggingInitialized"]


@dataclass(frozen=True, slots=True)
class LoggingInitialized:
    """Marker returned once logging has been configured via `setup_logging()`.

    `setup_logging()` is a void-returning function, not a constructible
    service — there is no "logging object" to hand out the way there is a
    `ConfigProviderPort` implementation. Registering this marker type as a
    singleton lets logging initialization be an explicit, container-managed,
    ordered step (any other registration can declare "I depend on logging
    being set up first" by resolving `LoggingInitialized`), without forcing
    the container to special-case factories that return `None`.
    """


def compose() -> ServiceContainer:
    """Build and return a fully wired `ServiceContainer` for Nikola AI.

    Registers, as of Sprint 5:

    - `ConfigProviderPort` (singleton) -> `EnvConfigProvider`, the
      validated, layered configuration loaded once and shared everywhere.
    - `LoggingInitialized` (singleton) -> configures logging (console/file
      handlers, level, formatter) from the resolved configuration's
      `logging` section, the first time it is resolved.

    Construction is lazy: nothing in this function actually loads
    configuration or configures logging by itself — both happen on first
    `resolve()`, in the order they are first requested. Calling
    `compose()` itself only registers *how* to build each service.

    Returns:
        A `ServiceContainer` with Nikola AI's current set of
        infrastructure services registered.
    """
    container = ServiceContainer()

    # ConfigProviderPort is an abstract port (ABC) used here purely as a
    # registration/lookup key, never instantiated directly — MyPy's
    # `type-abstract` check is a false positive for this DI usage pattern,
    # where the container's `dict[type[Any], ...]` key is the type itself,
    # not something callable used to construct an instance.
    container.register_singleton(
        ConfigProviderPort,  # type: ignore[type-abstract]
        factory=lambda _c: EnvConfigProvider(),
    )

    def _initialize_logging(c: ServiceContainer) -> LoggingInitialized:
        config_provider = c.resolve(ConfigProviderPort)  # type: ignore[type-abstract]
        settings = config_provider.get_settings()
        setup_logging(settings.logging)
        get_logger(__name__).info("Logging initialized via composition root.")
        return LoggingInitialized()

    container.register_singleton(LoggingInitialized, factory=_initialize_logging)

    return container
