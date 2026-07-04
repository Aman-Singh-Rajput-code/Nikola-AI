"""Unit tests for `nikola.infrastructure.brains.brain_registry.BrainRegistry`."""

from __future__ import annotations

import pytest

from nikola.domain.errors import BrainError
from nikola.infrastructure.brains.brain_registry import BrainRegistry
from nikola.infrastructure.brains.null_brain import NullBrain


@pytest.mark.unit
class TestBrainRegistryRegistration:
    def test_register_and_is_registered(self) -> None:
        registry = BrainRegistry()
        registry.register("null", NullBrain)
        assert registry.is_registered("null")

    def test_unregistered_name_is_not_registered(self) -> None:
        registry = BrainRegistry()
        assert not registry.is_registered("claude")

    def test_registered_names_returns_sorted_list(self) -> None:
        registry = BrainRegistry()
        registry.register("openai", NullBrain)
        registry.register("claude", NullBrain)
        assert registry.registered_names() == ["claude", "openai"]

    def test_re_registering_same_name_overwrites_factory(self) -> None:
        registry = BrainRegistry()
        registry.register("test", NullBrain)
        call_count = 0

        def second_factory() -> NullBrain:
            nonlocal call_count
            call_count += 1
            return NullBrain()

        registry.register("test", second_factory)
        registry.create("test")
        assert call_count == 1


@pytest.mark.unit
class TestBrainRegistryCreate:
    def test_create_returns_a_brain_port_instance(self) -> None:
        from nikola.domain.ports.brain_port import BrainPort

        registry = BrainRegistry()
        registry.register("null", NullBrain)
        brain = registry.create("null")
        assert isinstance(brain, BrainPort)

    def test_create_invokes_the_factory_each_time(self) -> None:
        registry = BrainRegistry()
        registry.register("null", NullBrain)
        first = registry.create("null")
        second = registry.create("null")
        assert first is not second

    def test_create_unregistered_name_raises_brain_error(self) -> None:
        registry = BrainRegistry()
        with pytest.raises(BrainError, match="not registered"):
            registry.create("claude")

    def test_error_message_lists_available_providers(self) -> None:
        registry = BrainRegistry()
        registry.register("null", NullBrain)
        with pytest.raises(BrainError, match="null"):
            registry.create("openai")
