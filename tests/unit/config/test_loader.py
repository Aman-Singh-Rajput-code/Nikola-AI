"""Unit tests for `nikola.infrastructure.config.loader.load_settings`.

This is the most important test module in Sprint 2: it proves the exact
priority order required by the architecture (environment variables > .env
> config/default.yaml > field defaults), proves that invalid configuration
fails fast with a clear, wrapped error rather than a raw Pydantic/YAML
exception, and proves the required-file behavior used at real application
startup.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from nikola.domain.errors import ConfigFileNotFoundError, ConfigValidationError
from nikola.infrastructure.config.loader import load_settings
from nikola.infrastructure.config.settings import Environment, LogLevel

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.config.conftest import YamlWriter


@pytest.mark.unit
class TestLoadSettingsDefaultsOnly:
    def test_falls_back_to_field_defaults_with_no_sources_present(self, isolated_cwd: Path) -> None:
        settings = load_settings()
        assert settings.app.name == "Nikola AI"
        assert settings.app.environment == Environment.DEVELOPMENT
        assert settings.logging.level == LogLevel.INFO

    def test_missing_yaml_file_is_not_fatal_by_default(self, isolated_cwd: Path) -> None:
        """require_yaml_file defaults to False: no file simply means no overrides."""
        settings = load_settings(yaml_path=isolated_cwd / "does_not_exist.yaml")
        assert settings.app.name == "Nikola AI"

    def test_missing_required_yaml_file_raises(self, isolated_cwd: Path) -> None:
        with pytest.raises(ConfigFileNotFoundError, match="does_not_exist.yaml"):
            load_settings(
                yaml_path=isolated_cwd / "does_not_exist.yaml",
                require_yaml_file=True,
            )


@pytest.mark.unit
class TestLoadSettingsYamlLayer:
    def test_yaml_values_override_field_defaults(
        self, isolated_cwd: Path, yaml_writer: YamlWriter
    ) -> None:
        yaml_file = yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            "app:\n"
            '  name: "Custom Name From YAML"\n'
            '  environment: "staging"\n'
            "logging:\n"
            '  level: "warning"\n',
        )
        settings = load_settings(yaml_path=yaml_file)
        assert settings.app.name == "Custom Name From YAML"
        assert settings.app.environment == Environment.STAGING
        assert settings.logging.level == LogLevel.WARNING

    def test_preexisting_config_file_env_var_is_restored_after_loading(
        self, isolated_cwd: Path, yaml_writer: YamlWriter, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An explicit yaml_path must not permanently clobber NIKOLA_CONFIG_FILE.

        `load_settings(yaml_path=...)` temporarily sets the
        `NIKOLA_CONFIG_FILE` environment variable so the YAML source picks
        up the requested path, then must restore whatever value (if any)
        was already there beforehand — otherwise a caller's own
        `NIKOLA_CONFIG_FILE` setting would leak/disappear as an unintended
        side effect of calling `load_settings` with an explicit path.
        """
        from nikola.infrastructure.config.yaml_source import YAML_CONFIG_PATH_ENV_VAR

        preexisting_path = str(isolated_cwd / "some_other_preexisting.yaml")
        monkeypatch.setenv(YAML_CONFIG_PATH_ENV_VAR, preexisting_path)

        yaml_file = yaml_writer(
            isolated_cwd / "explicit.yaml",
            'app:\n  name: "From Explicit Path"\n',
        )
        settings = load_settings(yaml_path=yaml_file)

        assert settings.app.name == "From Explicit Path"
        assert os.environ[YAML_CONFIG_PATH_ENV_VAR] == preexisting_path

    def test_empty_yaml_file_falls_back_to_defaults(
        self, isolated_cwd: Path, yaml_writer: YamlWriter
    ) -> None:
        yaml_file = yaml_writer(isolated_cwd / "config" / "default.yaml", "")
        settings = load_settings(yaml_path=yaml_file)
        assert settings.app.name == "Nikola AI"

    def test_yaml_file_must_be_a_mapping(self, isolated_cwd: Path, yaml_writer: YamlWriter) -> None:
        yaml_file = yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            "- this\n- is\n- a list, not a mapping\n",
        )
        with pytest.raises(ConfigValidationError, match="mapping"):
            load_settings(yaml_path=yaml_file)

    def test_malformed_yaml_syntax_raises_config_validation_error(self, isolated_cwd: Path) -> None:
        yaml_file = isolated_cwd / "config" / "default.yaml"
        yaml_file.parent.mkdir(parents=True, exist_ok=True)
        # Unbalanced brackets: invalid YAML syntax.
        yaml_file.write_text("app: [unbalanced", encoding="utf-8")
        with pytest.raises(ConfigValidationError, match="invalid YAML syntax"):
            load_settings(yaml_path=yaml_file)


@pytest.mark.unit
class TestLoadSettingsDotEnvLayer:
    def test_dotenv_overrides_yaml(self, isolated_cwd: Path, yaml_writer: YamlWriter) -> None:
        yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            'app:\n  name: "From YAML"\n',
        )
        (isolated_cwd / ".env").write_text('NIKOLA_APP__NAME="From DotEnv"\n', encoding="utf-8")

        settings = load_settings(yaml_path=isolated_cwd / "config" / "default.yaml")
        assert settings.app.name == "From DotEnv"


@pytest.mark.unit
class TestLoadSettingsRealEnvironmentLayer:
    def test_real_env_var_overrides_dotenv_and_yaml(
        self,
        isolated_cwd: Path,
        monkeypatch: pytest.MonkeyPatch,
        yaml_writer: YamlWriter,
    ) -> None:
        yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            'app:\n  name: "From YAML"\n',
        )
        (isolated_cwd / ".env").write_text('NIKOLA_APP__NAME="From DotEnv"\n', encoding="utf-8")
        monkeypatch.setenv("NIKOLA_APP__NAME", "From Real Env Var")

        settings = load_settings(yaml_path=isolated_cwd / "config" / "default.yaml")
        assert settings.app.name == "From Real Env Var"

    def test_full_priority_chain_env_beats_dotenv_beats_yaml_beats_default(
        self,
        isolated_cwd: Path,
        monkeypatch: pytest.MonkeyPatch,
        yaml_writer: YamlWriter,
    ) -> None:
        """Exercises all four layers on independent fields simultaneously.

        - `app.name`            is set by a real env var -> real env var wins.
        - `app.debug`           is set by .env and YAML, not by a real env
                                  var -> .env wins.
        - `logging.level`       is set only by YAML -> YAML wins over default.
        - `logging.json_format` is set nowhere -> field default holds.
        """
        yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            'app:\n  name: "From YAML"\n  debug: false\nlogging:\n  level: "error"\n',
        )
        (isolated_cwd / ".env").write_text(
            'NIKOLA_APP__NAME="From DotEnv"\nNIKOLA_APP__DEBUG=true\n',
            encoding="utf-8",
        )
        monkeypatch.setenv("NIKOLA_APP__NAME", "From Real Env Var")

        settings = load_settings(yaml_path=isolated_cwd / "config" / "default.yaml")

        assert settings.app.name == "From Real Env Var"  # env > .env > yaml
        assert settings.app.debug is True  # .env > yaml (no real env var set)
        assert settings.logging.level == LogLevel.ERROR  # yaml > default
        assert settings.logging.json_format is True  # untouched -> default


@pytest.mark.unit
class TestLoadSettingsValidationFailures:
    def test_invalid_enum_value_raises_config_validation_error_with_field_path(
        self, isolated_cwd: Path, yaml_writer: YamlWriter
    ) -> None:
        yaml_file = yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            'app:\n  environment: "not-a-real-environment"\n',
        )
        with pytest.raises(ConfigValidationError) as exc_info:
            load_settings(yaml_path=yaml_file)

        message = str(exc_info.value)
        assert "app.environment" in message

    def test_wrong_type_raises_config_validation_error(
        self, isolated_cwd: Path, yaml_writer: YamlWriter
    ) -> None:
        yaml_file = yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            # debug must be a bool; a nested mapping is not coercible.
            "app:\n  debug:\n    nested: true\n",
        )
        with pytest.raises(ConfigValidationError, match="app.debug"):
            load_settings(yaml_path=yaml_file)

    def test_multiple_errors_are_all_reported_together(
        self, isolated_cwd: Path, yaml_writer: YamlWriter
    ) -> None:
        """Fail-fast must report every invalid field in one pass, not just the first."""
        yaml_file = yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            "app:\n"
            '  environment: "not-a-real-environment"\n'
            '  name: ""\n'
            "logging:\n"
            '  level: "VERBOSE"\n',
        )
        with pytest.raises(ConfigValidationError) as exc_info:
            load_settings(yaml_path=yaml_file)

        message = str(exc_info.value)
        assert "app.environment" in message
        assert "app.name" in message
        assert "logging.level" in message

    def test_unknown_top_level_section_raises_config_validation_error(
        self, isolated_cwd: Path, yaml_writer: YamlWriter
    ) -> None:
        yaml_file = yaml_writer(
            isolated_cwd / "config" / "default.yaml",
            "totally_unknown_section:\n  foo: bar\n",
        )
        with pytest.raises(ConfigValidationError, match="totally_unknown_section"):
            load_settings(yaml_path=yaml_file)
