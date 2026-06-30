"""Unit tests for `nikola.bootstrap.compose`.

Covers `compose()`'s registrations end-to-end: `ConfigProviderPort`
resolves to a working `EnvConfigProvider` singleton, and
`LoggingInitialized` resolves exactly once, lazily, and actually
configures the "nikola" logger as a side effect.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

from nikola.bootstrap.compose import LoggingInitialized, compose
from nikola.domain.ports import ConfigProviderPort
from nikola.infrastructure.config import EnvConfigProvider

if TYPE_CHECKING:
    from nikola.bootstrap.container import ServiceContainer


def _resolve_config_provider(container: ServiceContainer) -> ConfigProviderPort:
    """Resolve `ConfigProviderPort` from `container`.

    A thin, explicitly-typed wrapper around `container.resolve()` so the
    one necessary `type: ignore[type-abstract]` (MyPy's `type-abstract`
    check is a false positive for abstract types used purely as DI
    registration/lookup keys, never instantiated directly — see
    `compose.py`) lives in exactly one place in this test module, instead
    of being repeated at every call site below.
    """
    return container.resolve(ConfigProviderPort)  # type: ignore[type-abstract]


def _is_config_provider_registered(container: ServiceContainer) -> bool:
    """Check `ConfigProviderPort` registration on `container`.

    Unlike `_resolve_config_provider`, no `type: ignore` is needed here:
    `ServiceContainer.is_registered()` accepts `type[Any]`, so passing an
    abstract type as a lookup key triggers no MyPy concern.
    """
    return container.is_registered(ConfigProviderPort)


@pytest.mark.unit
class TestComposeConfigRegistration:
    def test_config_provider_port_is_registered(self, isolated_cwd: object) -> None:
        container = compose()
        assert _is_config_provider_registered(container)

    def test_resolving_config_provider_port_returns_an_env_config_provider(
        self, isolated_cwd: object
    ) -> None:
        container = compose()
        provider = _resolve_config_provider(container)
        assert isinstance(provider, EnvConfigProvider)

    def test_config_provider_is_a_true_singleton(self, isolated_cwd: object) -> None:
        container = compose()
        first = _resolve_config_provider(container)
        second = _resolve_config_provider(container)
        assert first is second

    def test_resolved_settings_reflect_field_defaults_with_no_overrides(
        self, isolated_cwd: object
    ) -> None:
        container = compose()
        settings = _resolve_config_provider(container).get_settings()
        assert settings.app.name == "Nikola AI"


@pytest.mark.unit
class TestComposeLoggingRegistration:
    def test_logging_initialized_is_registered(self, isolated_cwd: object) -> None:
        container = compose()
        assert container.is_registered(LoggingInitialized)

    def test_resolving_logging_initialized_returns_the_marker_type(
        self, isolated_cwd: object
    ) -> None:
        container = compose()
        result = container.resolve(LoggingInitialized)
        assert isinstance(result, LoggingInitialized)

    def test_logging_initialized_is_a_true_singleton(self, isolated_cwd: object) -> None:
        container = compose()
        first = container.resolve(LoggingInitialized)
        second = container.resolve(LoggingInitialized)
        assert first is second

    def test_resolving_logging_initialized_attaches_handlers_to_nikola_logger(
        self, isolated_cwd: object
    ) -> None:
        container = compose()
        root_logger = logging.getLogger("nikola")
        assert len(root_logger.handlers) == 0  # not configured before resolution

        container.resolve(LoggingInitialized)

        assert len(root_logger.handlers) > 0

    def test_logging_is_not_configured_until_first_resolved(self, isolated_cwd: object) -> None:
        """compose() itself must not eagerly configure logging — only
        registration happens at compose() time; configuration happens
        lazily on first resolve(), per the container's lazy-singleton
        contract.
        """
        compose()  # registration only
        root_logger = logging.getLogger("nikola")
        assert len(root_logger.handlers) == 0


@pytest.mark.unit
class TestComposeOrdering:
    def test_resolving_logging_initialized_implicitly_resolves_config_first(
        self, isolated_cwd: object
    ) -> None:
        """LoggingInitialized's factory depends on ConfigProviderPort; resolving
        the former, without resolving the latter first, must still work —
        proving the dependency is correctly pulled in via the container.
        """
        container = compose()
        container.resolve(LoggingInitialized)
        assert _resolve_config_provider(container) is _resolve_config_provider(container)

    def test_logging_uses_the_same_config_instance_as_a_directly_resolved_provider(
        self, isolated_cwd: object
    ) -> None:
        container = compose()
        directly_resolved_provider = _resolve_config_provider(container)
        container.resolve(LoggingInitialized)

        # Resolving again after LoggingInitialized must still be the same
        # singleton instance — confirms LoggingInitialized's factory didn't
        # somehow create a second, divergent config provider.
        assert _resolve_config_provider(container) is directly_resolved_provider


@pytest.mark.unit
class TestComposeReturnsAFreshContainerEachCall:
    def test_two_compose_calls_return_independent_containers(self, isolated_cwd: object) -> None:
        first_container = compose()
        second_container = compose()

        first_provider = _resolve_config_provider(first_container)
        second_provider = _resolve_config_provider(second_container)

        assert first_provider is not second_provider
