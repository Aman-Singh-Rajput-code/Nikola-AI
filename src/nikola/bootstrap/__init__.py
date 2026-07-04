"""Composition root: dependency injection wiring, application factory, plugin discovery.

The only layer allowed to import concrete classes from every other layer
together. Sprint 5 implemented the DI mechanism; Sprint 6 adds `BrainPort`
to the composition root's registrations:

- `container.py` — the generic, Nikola-agnostic DI mechanism:
  `ServiceContainer`, `ServiceLifetime` (Singleton, Factory, Transient),
  and `ServiceDescriptor`.
- `compose.py` — `compose()`, which now registers configuration, logging,
  and the AI Brain (`BrainPort` → `NullBrain` by default, switchable by
  config to any registered provider).

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
