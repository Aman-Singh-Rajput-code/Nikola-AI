"""Unit tests for `nikola.bootstrap.container`.

Covers `ServiceLifetime`, `ServiceDescriptor`, and the three resolution
behaviors `ServiceContainer` must support: singleton caching, factory
re-invocation, and transient construction with automatic constructor
injection — plus the error paths (unregistered type, circular dependency).
"""

from __future__ import annotations

import pytest

from nikola.bootstrap.container import ServiceContainer, ServiceDescriptor, ServiceLifetime
from nikola.domain.errors import CircularDependencyError, ServiceNotRegisteredError

# --- Fixtures: small plain classes used across multiple test groups --------


class Engine:
    """A dependency-free class, used to test transient construction."""


class Car:
    """A class with one constructor-injectable dependency: Engine."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine


class Wheel:
    """A class with no registered dependency and no default — must fail
    construction cleanly if its dependency isn't registered."""

    def __init__(self, size_inches: int) -> None:
        self.size_inches = size_inches


class NodeA:
    """Half of a deliberately circular dependency pair, with NodeB."""

    def __init__(self, b: NodeB) -> None:
        self.b = b


class NodeB:
    """The other half of the circular dependency pair, with NodeA."""

    def __init__(self, a: NodeA) -> None:
        self.a = a


class HasUnresolvableAnnotation:
    """A class whose constructor parameter type cannot be resolved at
    runtime by `typing.get_type_hints()` — simulates a forward reference
    to a name that only exists under `TYPE_CHECKING` (or any other name
    not present in this module's runtime namespace). Used to exercise the
    container's `NameError` fallback: such a parameter must not be
    auto-injected, and must instead rely on its own default value.
    """

    def __init__(
        self,
        value: UndefinedAtRuntime = "default",  # type: ignore[name-defined] # noqa: F821
    ) -> None:
        self.value = value


@pytest.mark.unit
class TestServiceLifetime:
    def test_has_exactly_three_members(self) -> None:
        assert {member.value for member in ServiceLifetime} == {
            "singleton",
            "factory",
            "transient",
        }

    def test_is_a_str_subclass(self) -> None:
        assert isinstance(ServiceLifetime.SINGLETON, str)


@pytest.mark.unit
class TestServiceDescriptor:
    def test_holds_the_given_fields(self) -> None:
        descriptor = ServiceDescriptor(
            service_type=Engine,
            lifetime=ServiceLifetime.TRANSIENT,
            implementation=Engine,
        )
        assert descriptor.service_type is Engine
        assert descriptor.lifetime is ServiceLifetime.TRANSIENT
        assert descriptor.implementation is Engine

    def test_instance_defaults_to_none(self) -> None:
        descriptor = ServiceDescriptor(
            service_type=Engine, lifetime=ServiceLifetime.SINGLETON, implementation=lambda _c: None
        )
        assert descriptor.instance is None


@pytest.mark.unit
class TestRegisterSingleton:
    def test_resolve_returns_the_factory_built_instance(self) -> None:
        container = ServiceContainer()
        container.register_singleton(Engine, factory=lambda _c: Engine())

        engine = container.resolve(Engine)

        assert isinstance(engine, Engine)

    def test_resolve_returns_the_same_instance_every_time(self) -> None:
        container = ServiceContainer()
        container.register_singleton(Engine, factory=lambda _c: Engine())

        first = container.resolve(Engine)
        second = container.resolve(Engine)

        assert first is second

    def test_factory_is_invoked_exactly_once(self) -> None:
        call_count = 0

        def factory(c: ServiceContainer) -> Engine:
            nonlocal call_count
            call_count += 1
            return Engine()

        container = ServiceContainer()
        container.register_singleton(Engine, factory=factory)

        container.resolve(Engine)
        container.resolve(Engine)
        container.resolve(Engine)

        assert call_count == 1

    def test_factory_is_not_invoked_at_registration_time(self) -> None:
        """Construction must be lazy: registering alone must not build anything."""
        call_count = 0

        def factory(c: ServiceContainer) -> Engine:
            nonlocal call_count
            call_count += 1
            return Engine()

        container = ServiceContainer()
        container.register_singleton(Engine, factory=factory)

        assert call_count == 0

    def test_singleton_factory_can_resolve_other_registered_services(self) -> None:
        container = ServiceContainer()
        container.register_singleton(Engine, factory=lambda _c: Engine())
        container.register_singleton(Car, factory=lambda c: Car(engine=c.resolve(Engine)))

        car = container.resolve(Car)

        assert isinstance(car.engine, Engine)


@pytest.mark.unit
class TestRegisterFactory:
    def test_resolve_returns_a_built_instance(self) -> None:
        container = ServiceContainer()
        container.register_factory(Engine, factory=lambda _c: Engine())

        engine = container.resolve(Engine)

        assert isinstance(engine, Engine)

    def test_factory_is_invoked_on_every_resolve(self) -> None:
        call_count = 0

        def factory(c: ServiceContainer) -> Engine:
            nonlocal call_count
            call_count += 1
            return Engine()

        container = ServiceContainer()
        container.register_factory(Engine, factory=factory)

        container.resolve(Engine)
        container.resolve(Engine)
        container.resolve(Engine)

        assert call_count == 3

    def test_each_resolution_returns_a_distinct_instance(self) -> None:
        container = ServiceContainer()
        container.register_factory(Engine, factory=lambda _c: Engine())

        first = container.resolve(Engine)
        second = container.resolve(Engine)

        assert first is not second

    def test_factory_receives_the_container_and_can_resolve_dependencies(self) -> None:
        container = ServiceContainer()
        container.register_singleton(Engine, factory=lambda _c: Engine())
        container.register_factory(Car, factory=lambda c: Car(engine=c.resolve(Engine)))

        car = container.resolve(Car)

        assert isinstance(car.engine, Engine)


@pytest.mark.unit
class TestRegisterTransient:
    def test_resolve_returns_an_instance_of_the_registered_type(self) -> None:
        container = ServiceContainer()
        container.register_transient(Engine)

        engine = container.resolve(Engine)

        assert isinstance(engine, Engine)

    def test_each_resolution_returns_a_distinct_instance(self) -> None:
        container = ServiceContainer()
        container.register_transient(Engine)

        first = container.resolve(Engine)
        second = container.resolve(Engine)

        assert first is not second

    def test_constructor_injection_supplies_registered_dependencies(self) -> None:
        container = ServiceContainer()
        container.register_transient(Engine)
        container.register_transient(Car)

        car = container.resolve(Car)

        assert isinstance(car, Car)
        assert isinstance(car.engine, Engine)

    def test_constructor_injection_produces_fresh_dependencies_each_time(self) -> None:
        container = ServiceContainer()
        container.register_transient(Engine)
        container.register_transient(Car)

        first_car = container.resolve(Car)
        second_car = container.resolve(Car)

        assert first_car.engine is not second_car.engine

    def test_unregistered_required_parameter_raises_type_error(self) -> None:
        """Wheel.size_inches is an int (never registered) with no default.

        The container must not guess a value — Python's own constructor
        call should fail with a TypeError for the missing required arg.
        """
        container = ServiceContainer()
        container.register_transient(Wheel)

        with pytest.raises(TypeError):
            container.resolve(Wheel)

    def test_unresolvable_forward_reference_falls_back_to_its_default(self) -> None:
        """A parameter annotated with a name that cannot be resolved at
        runtime (e.g. only defined under TYPE_CHECKING) must not crash
        resolution — it simply isn't auto-injected, and its own default
        value is used instead, exactly as if it were any other
        non-registered parameter with a default.
        """
        container = ServiceContainer()
        container.register_transient(HasUnresolvableAnnotation)

        instance = container.resolve(HasUnresolvableAnnotation)

        assert instance.value == "default"


@pytest.mark.unit
class TestResolveUnregisteredType:
    def test_raises_service_not_registered_error(self) -> None:
        container = ServiceContainer()
        with pytest.raises(ServiceNotRegisteredError, match="Engine"):
            container.resolve(Engine)

    def test_error_message_mentions_registration_methods(self) -> None:
        container = ServiceContainer()
        with pytest.raises(ServiceNotRegisteredError, match="register_singleton"):
            container.resolve(Engine)


@pytest.mark.unit
class TestCircularDependencyDetection:
    def test_raises_circular_dependency_error(self) -> None:
        container = ServiceContainer()
        container.register_transient(NodeA)
        container.register_transient(NodeB)

        with pytest.raises(CircularDependencyError):
            container.resolve(NodeA)

    def test_error_message_describes_the_cycle(self) -> None:
        container = ServiceContainer()
        container.register_transient(NodeA)
        container.register_transient(NodeB)

        with pytest.raises(CircularDependencyError, match="NodeA -> NodeB -> NodeA"):
            container.resolve(NodeA)

    def test_container_remains_usable_after_a_circular_dependency_error(self) -> None:
        """The resolution stack must be cleaned up even when resolution fails,
        so a subsequent, unrelated resolve() call still works correctly.
        """
        container = ServiceContainer()
        container.register_transient(NodeA)
        container.register_transient(NodeB)
        container.register_transient(Engine)

        with pytest.raises(CircularDependencyError):
            container.resolve(NodeA)

        engine = container.resolve(Engine)
        assert isinstance(engine, Engine)


@pytest.mark.unit
class TestIsRegistered:
    def test_returns_true_for_a_registered_type(self) -> None:
        container = ServiceContainer()
        container.register_transient(Engine)
        assert container.is_registered(Engine) is True

    def test_returns_false_for_an_unregistered_type(self) -> None:
        container = ServiceContainer()
        assert container.is_registered(Engine) is False


@pytest.mark.unit
class TestReRegistration:
    def test_registering_the_same_type_twice_replaces_the_first_registration(self) -> None:
        container = ServiceContainer()
        container.register_singleton(Engine, factory=lambda _c: Engine())
        first_instance = container.resolve(Engine)

        container.register_factory(Engine, factory=lambda _c: Engine())
        second_instance = container.resolve(Engine)
        third_instance = container.resolve(Engine)

        assert second_instance is not first_instance
        assert second_instance is not third_instance  # now factory-lifetime, not cached
