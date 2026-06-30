"""A lightweight, explicit, framework-independent dependency injection container.

This module contains the generic DI mechanism only — `ServiceLifetime`,
`ServiceDescriptor`, and `ServiceContainer`. It has no knowledge of
anything Nikola-specific (no imports from `infrastructure/`, `domain/`
entities, or configuration); the actual wiring of Nikola's real services
(`ConfigProviderPort`, logging) lives in `nikola.bootstrap.compose`, which
is the composition root that imports both this module and the concrete
services it registers.

Keeping this split is deliberate: `container.py` is a small, reusable
mechanism that could be lifted into any Python project; `compose.py` is
where Nikola AI's specific dependency graph is actually described.

No third-party DI library is used, per the architecture's preference for
explicit, auditable wiring over framework magic. The container intentionally
does not support thread-safety/locking — it is built and used synchronously
at application startup, before any concurrent execution exists in the
codebase; this is a deliberate, documented scope limit rather than an
oversight.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, TypeVar, get_type_hints

from nikola.domain.errors import CircularDependencyError, ServiceNotRegisteredError

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["ServiceLifetime", "ServiceDescriptor", "ServiceContainer"]

T = TypeVar("T")


class ServiceLifetime(StrEnum):
    """How long a registered service's constructed instance is reused.

    - `SINGLETON`: constructed once, lazily, on first `resolve()`. The
      same instance is returned on every subsequent resolution.
    - `FACTORY`: the registered factory callable is re-invoked on every
      `resolve()` call. Use this for arbitrary construction logic (e.g.
      choosing between concrete types at resolution time) that doesn't
      fit a plain constructor-injection shape.
    - `TRANSIENT`: a new instance is constructed on every `resolve()`
      call via constructor injection — the container inspects the
      registered class's `__init__` type hints and automatically
      resolves any parameters that are themselves registered services.
    """

    SINGLETON = "singleton"
    FACTORY = "factory"
    TRANSIENT = "transient"


@dataclass(slots=True)
class ServiceDescriptor:
    """Internal record of how a single service registration should be built.

    One `ServiceDescriptor` exists per registered service key, stored in
    the `ServiceContainer`'s internal registry. Application code does not
    construct these directly — use `ServiceContainer.register_singleton`,
    `.register_factory`, or `.register_transient` instead, which build and
    store the appropriate descriptor.

    Attributes:
        service_type: The type (typically a port/abstract type, or a
            concrete class for `TRANSIENT` registrations) used as the
            lookup key for this registration.
        lifetime: How instances of this service are constructed and reused.
        implementation: For `SINGLETON`/`FACTORY`, the factory callable
            `Callable[[ServiceContainer], Any]` used to construct an
            instance. For `TRANSIENT`, the concrete class itself, whose
            constructor is invoked via automatic constructor injection.
        instance: The cached instance for a `SINGLETON` registration, set
            on first resolution. Always `None` for `FACTORY`/`TRANSIENT`
            registrations, which never cache.
    """

    service_type: type[Any]
    lifetime: ServiceLifetime
    implementation: Any
    instance: Any = field(default=None)


class ServiceContainer:
    """A minimal registry mapping service types to how they should be built.

    Typical usage, performed once in a composition root such as
    `nikola.bootstrap.compose.compose()`:

        container = ServiceContainer()
        container.register_singleton(
            ConfigProviderPort, factory=lambda c: EnvConfigProvider()
        )
        ...
        settings_provider = container.resolve(ConfigProviderPort)

    The container is intentionally not a global/ambient singleton itself —
    `ServiceContainer()` is a plain object an application explicitly
    constructs, passes around, and resolves from. This keeps dependency
    wiring visible and testable rather than hidden behind module-level
    global state.
    """

    def __init__(self) -> None:
        self._registry: dict[type[Any], ServiceDescriptor] = {}
        self._resolution_stack: list[type[Any]] = []

    def register_singleton(
        self, service_type: type[T], *, factory: Callable[[ServiceContainer], T]
    ) -> None:
        """Register `service_type` to be built once, lazily, and reused.

        Args:
            service_type: The type used as the lookup key — typically a
                port/abstract type (e.g. `ConfigProviderPort`).
            factory: A callable that builds the single shared instance,
                given the container (so it can resolve its own
                dependencies). Invoked at most once, on first `resolve()`.
        """
        self._registry[service_type] = ServiceDescriptor(
            service_type=service_type,
            lifetime=ServiceLifetime.SINGLETON,
            implementation=factory,
        )

    def register_factory(
        self, service_type: type[T], *, factory: Callable[[ServiceContainer], T]
    ) -> None:
        """Register `service_type` to be (re)built by `factory` on every resolution.

        Args:
            service_type: The type used as the lookup key.
            factory: A callable that builds a new instance, given the
                container. Invoked anew on every `resolve()` call — no
                caching occurs.
        """
        self._registry[service_type] = ServiceDescriptor(
            service_type=service_type,
            lifetime=ServiceLifetime.FACTORY,
            implementation=factory,
        )

    def register_transient(self, service_type: type[T]) -> None:
        """Register `service_type` to be constructed via automatic constructor injection.

        On every `resolve()` call, a new instance of `service_type` is
        constructed by inspecting its `__init__` type hints: for each
        parameter whose annotated type is itself registered in this
        container, the container resolves and supplies it automatically.
        Parameters not registered must have a default value, or
        construction will fail with a `TypeError` from Python itself
        (the container does not silently pass `None` for unresolvable
        parameters).

        Args:
            service_type: The concrete class to register and construct.
                Used as both the lookup key and the thing constructed.
        """
        self._registry[service_type] = ServiceDescriptor(
            service_type=service_type,
            lifetime=ServiceLifetime.TRANSIENT,
            implementation=service_type,
        )

    def resolve(self, service_type: type[T]) -> T:
        """Return an instance of `service_type`, per its registered lifetime.

        Args:
            service_type: The type previously passed to one of the
                `register_*` methods.

        Returns:
            An instance of `service_type` (or, in practice, of whatever
            concrete type the registered factory/class produces).

        Raises:
            ServiceNotRegisteredError: If `service_type` was never
                registered.
            CircularDependencyError: If resolving `service_type` requires
                (directly or transitively) resolving `service_type` again,
                detected during transient constructor injection.

        Note:
            Internally, the registry stores descriptors as
            `dict[type[Any], ServiceDescriptor]` — making it fully generic
            over `T` would add real complexity for a container this small,
            so the three return paths below are deliberately
            `# type: ignore[no-any-return]`. The `-> T` signature is a
            documented contract callers can rely on (the registered
            factory/class for `service_type` is responsible for actually
            producing a `T`), not something the internal storage can prove
            statically.
        """
        descriptor = self._registry.get(service_type)
        if descriptor is None:
            raise ServiceNotRegisteredError(
                f"No service is registered for type '{service_type.__name__}'. "
                f"Register it with register_singleton(), register_factory(), "
                f"or register_transient() before resolving it."
            )

        if descriptor.lifetime is ServiceLifetime.SINGLETON:
            return self._resolve_singleton(descriptor)  # type: ignore[no-any-return]
        if descriptor.lifetime is ServiceLifetime.FACTORY:
            return descriptor.implementation(self)  # type: ignore[no-any-return]
        return self._resolve_transient(descriptor)  # type: ignore[no-any-return]

    def is_registered(self, service_type: type[Any]) -> bool:
        """Return whether `service_type` has a registration in this container."""
        return service_type in self._registry

    def _resolve_singleton(self, descriptor: ServiceDescriptor) -> Any:
        if descriptor.instance is None:
            descriptor.instance = descriptor.implementation(self)
        return descriptor.instance

    def _resolve_transient(self, descriptor: ServiceDescriptor) -> Any:
        service_type = descriptor.service_type
        if service_type in self._resolution_stack:
            chain = " -> ".join(t.__name__ for t in (*self._resolution_stack, service_type))
            raise CircularDependencyError(
                f"Circular dependency detected while resolving "
                f"'{service_type.__name__}': {chain}"
            )

        self._resolution_stack.append(service_type)
        try:
            implementation_type = descriptor.implementation
            kwargs = self._resolve_constructor_dependencies(implementation_type)
            return implementation_type(**kwargs)
        finally:
            self._resolution_stack.pop()

    def _resolve_constructor_dependencies(self, implementation_type: type[Any]) -> dict[str, Any]:
        """Inspect `implementation_type.__init__` and auto-resolve registered parameters.

        Only parameters whose annotated type is itself registered in this
        container are supplied. All other parameters are left out of the
        returned kwargs entirely, so they fall back to their own default
        value (or raise Python's own `TypeError` if no default exists and
        the parameter is required) — the container never guesses a value
        for a dependency it doesn't know how to build.
        """
        signature = inspect.signature(implementation_type.__init__)
        try:
            type_hints = get_type_hints(implementation_type.__init__)
        except NameError:
            # A forward-referenced annotation that can't be resolved here
            # (e.g. defined under `if TYPE_CHECKING`) simply can't be
            # auto-injected; such parameters must have their own default.
            type_hints = {}

        kwargs: dict[str, Any] = {}
        for name, parameter in signature.parameters.items():
            if name == "self":
                continue
            annotated_type = type_hints.get(name, parameter.annotation)
            if isinstance(annotated_type, type) and self.is_registered(annotated_type):
                kwargs[name] = self.resolve(annotated_type)
        return kwargs
