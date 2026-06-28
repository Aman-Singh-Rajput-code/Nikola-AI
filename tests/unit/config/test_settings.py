"""Unit tests for `nikola.infrastructure.config.settings`.

These tests exercise the Pydantic schema in isolation — defaults, field
validation, and the case-insensitive log-level normalizer — without
involving the YAML source or the loader's error-wrapping. Source-priority
behavior (YAML vs .env vs real env vars) is covered separately in
`test_loader.py`, since that is where the actual merging happens.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from nikola.infrastructure.config.settings import (
    AppSettings,
    Environment,
    LoggingSettings,
    LogLevel,
    NikolaSettings,
)


@pytest.mark.unit
class TestAppSettingsDefaults:
    def test_default_values(self) -> None:
        settings = AppSettings()
        assert settings.name == "Nikola AI"
        assert settings.version == "0.1.0"
        assert settings.environment == Environment.DEVELOPMENT
        assert settings.debug is False

    def test_empty_name_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AppSettings(name="")

    def test_invalid_environment_value_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AppSettings(environment="not-a-real-environment")  # type: ignore[arg-type]


@pytest.mark.unit
class TestLoggingSettingsDefaults:
    def test_default_values(self) -> None:
        settings = LoggingSettings()
        assert settings.level == LogLevel.INFO
        assert settings.json_format is True
        assert settings.console_enabled is True
        assert settings.file_path is None

    def test_file_path_accepts_a_path_string(self) -> None:
        settings = LoggingSettings(file_path="logs/nikola.log")  # type: ignore[arg-type]
        assert settings.file_path == Path("logs/nikola.log")

    def test_console_enabled_can_be_disabled(self) -> None:
        settings = LoggingSettings(console_enabled=False)
        assert settings.console_enabled is False

    def test_invalid_level_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            LoggingSettings(level="VERBOSE")  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        ("given", "expected"),
        [
            ("debug", LogLevel.DEBUG),
            ("Debug", LogLevel.DEBUG),
            ("DEBUG", LogLevel.DEBUG),
            ("warning", LogLevel.WARNING),
        ],
    )
    def test_level_is_case_insensitive(self, given: str, expected: LogLevel) -> None:
        settings = LoggingSettings(level=given)  # type: ignore[arg-type]
        assert settings.level == expected

    def test_level_accepts_enum_member_directly(self) -> None:
        """Passing an already-valid LogLevel enum must work.

        `LogLevel` is a `StrEnum`, so an enum member IS a `str` instance —
        it takes the same "uppercase a string" branch as a plain string
        input, just as a no-op (it's already uppercase). This confirms
        that path doesn't break enum-typed input.
        """
        settings = LoggingSettings(level=LogLevel.CRITICAL)
        assert settings.level == LogLevel.CRITICAL

    def test_non_string_level_is_passed_through_to_enum_validation(self) -> None:
        """A genuinely non-string input must skip the uppercase step.

        Exercises the normalizer's non-string passthrough branch (the
        `isinstance(value, str)` check is False), then lets Pydantic's own
        enum validation reject the value with its standard error — the
        normalizer's job is only to fix casing, never to validate.
        """
        with pytest.raises(ValidationError):
            LoggingSettings(level=123)  # type: ignore[arg-type]


@pytest.mark.unit
class TestNikolaSettingsDefaults:
    def test_constructs_with_no_arguments_when_no_config_sources_present(
        self, isolated_cwd: object
    ) -> None:
        """With no YAML file, no .env, and no env vars, defaults must hold.

        Uses `isolated_cwd` (from conftest.py) so this test does not
        accidentally read the real repository's config/default.yaml.
        """
        settings = NikolaSettings()
        assert settings.app.name == "Nikola AI"
        assert settings.logging.level == LogLevel.INFO

    def test_unknown_top_level_key_is_rejected(self, isolated_cwd: object) -> None:
        """`extra="forbid"` must reject unrecognized top-level config keys.

        This is a deliberate "fail fast" guard: a typo'd section name (e.g.
        `loggin:` instead of `logging:`) must be caught at validation time,
        not silently ignored.
        """
        with pytest.raises(ValidationError):
            NikolaSettings(unknown_section={"foo": "bar"})  # type: ignore[call-arg]
