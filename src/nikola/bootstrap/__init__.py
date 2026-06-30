"""Composition root: dependency injection wiring, application factory, plugin discovery.

The only layer allowed to import concrete classes from every other layer
together. Sprint 5 implements the dependency injection system:

- `container.py` — the generic, Nikola-agnostic DI mechanism:
  `ServiceContainer`, `ServiceLifetime` (Singleton, Factory, Transient),
  and `ServiceDescriptor`.
- `compose.py` — `compose()`, the actual composition root that registers
  Nikola AI's real services (configuration, logging) into a
  `ServiceContainer`.

`app_factory.py` (building the fully wired *application*, beyond just its
service registrations) and `plugin_discovery.py` are implemented in later
sprints.
"""

from nikola.bootstrap.compose import LoggingInitialized, compose
from nikola.bootstrap.container import ServiceContainer, ServiceDescriptor, ServiceLifetime

__all__ = [
    "ServiceContainer",
    "ServiceLifetime",
    "ServiceDescriptor",
    "compose",
    "LoggingInitialized",
]
