"""Unit tests for `nikola.infrastructure.brains.brain_factory`."""

from __future__ import annotations

import pytest

from nikola.domain.errors import BrainError
from nikola.infrastructure.brains.brain_factory import BrainFactory, build_default_registry
from nikola.infrastructure.brains.brain_registry import BrainRegistry
from nikola.infrastructure.brains.null_brain import NullBrain
from nikola.infrastructure.config.settings import BrainSettings


@pytest.mark.unit
class TestBuildDefaultRegistry:
    def test_returns_a_brain_registry(self) -> None:
        registry = build_default_registry()
        assert isinstance(registry, BrainRegistry)

    def test_null_provider_is_registered(self) -> None:
        registry = build_default_registry()
        assert registry.is_registered("null")

    def test_null_provider_produces_a_null_brain(self) -> None:
        registry = build_default_registry()
        brain = registry.create("null")
        assert isinstance(brain, NullBrain)


@pytest.mark.unit
class TestBrainFactory:
    def test_create_from_settings_returns_configured_provider(self) -> None:
        registry = build_default_registry()
        factory = BrainFactory(registry)
        brain = factory.create_from_settings(BrainSettings(provider="null"))
        assert isinstance(brain, NullBrain)

    def test_create_from_settings_unregistered_provider_raises_brain_error(self) -> None:
        registry = BrainRegistry()
        factory = BrainFactory(registry)
        with pytest.raises(BrainError):
            factory.create_from_settings(BrainSettings(provider="openai"))

    def test_default_provider_setting_selects_null_brain(self) -> None:
        registry = build_default_registry()
        factory = BrainFactory(registry)
        brain = factory.create_from_settings(BrainSettings())
        assert brain.provider_name == "null"
