"""Unit tests for `nikola.infrastructure.config.env_config_provider.EnvConfigProvider`.

These tests verify the adapter's contract as the concrete implementation of
`ConfigProviderPort`: eager loading at construction time (fail-fast),
typed access via `get_settings()`, and the forgiving dotted-path lookup via
`get()`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from nikola.domain.errors import ConfigValidationError
from nikola.domain.ports.config_provider_port import ConfigProviderPort
from nikola.infrastructure.config.env_config_provider import EnvConfigProvider
from nikola.infrastructure.config.settings import LogLevel

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.config.conftest import YamlWriter


@pytest.mark.unit
class TestEnvConfigProviderIsAPort:
    def test_is_an_instance_of_config_provider_port(self, isolated_cwd: Path) -> None:
        provider = EnvConfigProvider()
        assert isinstance(provider, ConfigProviderPort)


@pytest.mark.unit
class TestEnvConfigProviderGetSettings:
    def test_returns_validated_settings(self, isolated_cwd: Path, yaml_writer: YamlWriter) -> None:
        yaml_file = yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            'app:\n  name: "Provider Test App"\n',
        )
        provider = EnvConfigProvider(yaml_path=yaml_file)

        settings = provider.get_settings()
        assert settings.app.name == "Provider Test App"

    def test_loads_eagerly_at_construction_and_raises_immediately_on_bad_config(
        self, isolated_cwd: Path, yaml_writer: YamlWriter
    ) -> None:
        """Fail-fast: the error must surface at construction, not on first use."""
        yaml_file = yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            'logging:\n  level: "NOT_A_LEVEL"\n',
        )
        with pytest.raises(ConfigValidationError):
            EnvConfigProvider(yaml_path=yaml_file)


@pytest.mark.unit
class TestEnvConfigProviderGet:
    def test_get_resolves_nested_dotted_path(
        self, isolated_cwd: Path, yaml_writer: YamlWriter
    ) -> None:
        yaml_file = yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            'logging:\n  level: "DEBUG"\n',
        )
        provider = EnvConfigProvider(yaml_path=yaml_file)

        assert provider.get("logging.level") == LogLevel.DEBUG

    def test_get_returns_default_for_unknown_key(self, isolated_cwd: Path) -> None:
        provider = EnvConfigProvider()
        assert provider.get("does.not.exist", default="fallback") == "fallback"

    def test_get_returns_default_when_path_fails_partway_through(self, isolated_cwd: Path) -> None:
        """A valid first segment with an invalid second segment must still
        return the default, not raise — `app` exists, `app.nonexistent`
        does not.
        """
        provider = EnvConfigProvider()
        assert provider.get("app.nonexistent_field", default="fallback") == "fallback"

    def test_get_returns_none_default_when_unspecified(self, isolated_cwd: Path) -> None:
        provider = EnvConfigProvider()
        assert provider.get("nonexistent_section") is None

    def test_get_top_level_section_returns_submodel(self, isolated_cwd: Path) -> None:
        provider = EnvConfigProvider()
        app_settings = provider.get("app")
        assert app_settings.name == "Nikola AI"
