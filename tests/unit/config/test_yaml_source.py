"""Unit tests for `nikola.infrastructure.config.yaml_source.YamlConfigSettingsSource`.

These tests target the YAML source's path-resolution rules in isolation
(explicit path > NIKOLA_CONFIG_FILE env var > default path), independent of
the full `load_settings()` orchestration covered in `test_loader.py`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from nikola.infrastructure.config.settings import NikolaSettings
from nikola.infrastructure.config.yaml_source import (
    DEFAULT_YAML_CONFIG_PATH,
    YAML_CONFIG_PATH_ENV_VAR,
    YamlConfigSettingsSource,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.config.conftest import YamlWriter


@pytest.mark.unit
class TestYamlConfigSettingsSourcePathResolution:
    def test_defaults_to_config_default_yaml(self) -> None:
        source = YamlConfigSettingsSource(NikolaSettings)
        assert source._yaml_file == DEFAULT_YAML_CONFIG_PATH

    def test_explicit_path_takes_priority(self, isolated_cwd: Path) -> None:
        explicit = isolated_cwd / "custom.yaml"
        source = YamlConfigSettingsSource(NikolaSettings, yaml_file=explicit)
        assert source._yaml_file == explicit

    def test_env_var_override_used_when_no_explicit_path(
        self, isolated_cwd: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        env_path = isolated_cwd / "env_override.yaml"
        monkeypatch.setenv(YAML_CONFIG_PATH_ENV_VAR, str(env_path))

        source = YamlConfigSettingsSource(NikolaSettings)
        assert source._yaml_file == env_path

    def test_explicit_path_wins_over_env_var(
        self, isolated_cwd: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(YAML_CONFIG_PATH_ENV_VAR, str(isolated_cwd / "from_env.yaml"))
        explicit = isolated_cwd / "explicit.yaml"

        source = YamlConfigSettingsSource(NikolaSettings, yaml_file=explicit)
        assert source._yaml_file == explicit


@pytest.mark.unit
class TestYamlConfigSettingsSourceReading:
    def test_returns_empty_dict_when_file_missing(self, isolated_cwd: Path) -> None:
        source = YamlConfigSettingsSource(NikolaSettings, yaml_file=isolated_cwd / "missing.yaml")
        assert source() == {}

    def test_returns_parsed_mapping(self, isolated_cwd: Path, yaml_writer: YamlWriter) -> None:
        yaml_file = yaml_writer(
            isolated_cwd / "present.yaml",
            'app:\n  name: "Parsed Name"\n',
        )
        source = YamlConfigSettingsSource(NikolaSettings, yaml_file=yaml_file)
        assert source() == {"app": {"name": "Parsed Name"}}

    def test_empty_file_returns_empty_dict(
        self, isolated_cwd: Path, yaml_writer: YamlWriter
    ) -> None:
        yaml_file = yaml_writer(isolated_cwd / "empty.yaml", "")
        source = YamlConfigSettingsSource(NikolaSettings, yaml_file=yaml_file)
        assert source() == {}

    def test_non_mapping_top_level_raises_value_error(
        self, isolated_cwd: Path, yaml_writer: YamlWriter
    ) -> None:
        yaml_file = yaml_writer(isolated_cwd / "scalar.yaml", "just a string")
        source = YamlConfigSettingsSource(NikolaSettings, yaml_file=yaml_file)
        with pytest.raises(ValueError, match="mapping"):
            source()

    def test_repr_includes_resolved_path(self, isolated_cwd: Path) -> None:
        yaml_file = isolated_cwd / "repr_test.yaml"
        source = YamlConfigSettingsSource(NikolaSettings, yaml_file=yaml_file)
        assert str(yaml_file) in repr(source)
