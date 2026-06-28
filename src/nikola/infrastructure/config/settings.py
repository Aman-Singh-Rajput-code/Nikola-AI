"""Typed configuration schema for Nikola AI, built on Pydantic Settings.

This module defines *what* configuration looks like. It contains no
filesystem or environment-variable reading logic of its own beyond what
`pydantic-settings` provides natively — the orchestration of "merge
config/default.yaml, then .env, then real environment variables, in that
priority order" lives in `nikola.infrastructure.config.loader`, kept
deliberately separate from the schema itself.

Why nested sub-models instead of one flat settings class
----------------------------------------------------------
The architecture calls for configuration sections covering many concerns
(brain provider, logging, permissions, scheduler, memory backend, ...).
Sprint 2 only has real content for two of those sections — `app` and
`logging` — but modeling `NikolaSettings` as a container of nested
sub-models from the start means later sprints add a new sub-model (e.g.
`BrainSettings`) without reshaping anything that already exists. Flattening
now and nesting later would be a breaking change for every piece of code
that reads configuration by then.

Why environment variables use a nested delimiter
----------------------------------------------------
With `pydantic-settings`, nested models are addressable from environment
variables using a delimiter, configured below as `__` (double underscore).
This makes `NIKOLA_LOGGING__LEVEL=DEBUG` map to `settings.logging.level`,
which keeps the flat env-var namespace unambiguous even as more nested
sections are added in later sprints.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path  # noqa: TC003 (Pydantic needs this at runtime to build the model)

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

__all__ = [
    "Environment",
    "LogLevel",
    "AppSettings",
    "LoggingSettings",
    "NikolaSettings",
]


class Environment(StrEnum):
    """The deployment environment Nikola AI is running in.

    Used today only for descriptive/validation purposes (Sprint 2 does not
    yet branch behavior on this value anywhere). Future sprints may use it
    to, for example, default to stricter permission policies in production.
    """

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    """Supported logging verbosity levels.

    Mirrors Python's standard `logging` module level names. Modeled as an
    explicit enum (rather than accepting any string) so an invalid value
    such as `LOGGING__LEVEL=VERBOSE` fails configuration validation
    immediately, with a clear message, rather than failing later and
    confusingly inside the logging subsystem once it's implemented.
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AppSettings(BaseModel):
    """General application identity and environment metadata."""

    name: str = Field(
        default="Nikola AI",
        description="Human-readable application name, used in logs and CLI banners.",
        min_length=1,
    )
    version: str = Field(
        default="0.1.0",
        description="Application version string.",
        min_length=1,
    )
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Deployment environment.",
    )
    debug: bool = Field(
        default=False,
        description="Enables verbose, developer-oriented behavior across the app.",
    )


class LoggingSettings(BaseModel):
    """Structured logging configuration.

    Sprint 2 introduced `level` and `json_format`. Sprint 3 (Structured
    Logging Framework) adds `console_enabled` and `file_path` to support
    console and file logging destinations without changing the meaning or
    defaults of the existing fields — an existing `.env` or
    `config/default.yaml` with only `level`/`json_format` set continues to
    work unchanged, since both new fields have safe defaults
    (console-only, no file).
    """

    level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Minimum severity level that will be emitted.",
    )
    json_format: bool = Field(
        default=True,
        description=(
            "Emit logs as structured JSON (production-friendly) rather than "
            "plain text (more readable during local development)."
        ),
    )
    console_enabled: bool = Field(
        default=True,
        description="Emit log records to the console (stdout).",
    )
    file_path: Path | None = Field(
        default=None,
        description=(
            "Optional filesystem path to write log records to, in addition "
            "to (or instead of) the console. If unset, no file handler is "
            "attached and only console logging (if enabled) occurs."
        ),
    )

    @field_validator("level", mode="before")
    @classmethod
    def _normalize_level_case(cls, value: object) -> object:
        """Allow `level: info` in YAML/env as well as `level: INFO`.

        Configuration authors should not have to remember exact casing for
        an enum like this; we normalize before Pydantic's enum validation
        runs, rather than asking every config source to get the case right.
        """
        if isinstance(value, str):
            return value.upper()
        return value


class NikolaSettings(BaseSettings):
    """Root configuration object for Nikola AI.

    Resolution priority (highest wins), per Sprint 2 requirements:

        1. Real environment variables   (e.g. `export NIKOLA_APP__DEBUG=true`)
        2. Values from a `.env` file
        3. Values from `config/default.yaml`
        4. Field defaults declared on the models above

    The YAML layer is not a built-in `pydantic-settings` source, so it is
    spliced into the resolution chain via `settings_customise_sources`
    below, using `YamlConfigSettingsSource` from
    `nikola.infrastructure.config.yaml_source`.

    This class is intentionally NOT instantiated directly by application
    code. Use `nikola.infrastructure.config.loader.load_settings()`, which
    wires in the YAML source path and wraps validation failures in a
    domain `ConfigurationError`. Instantiating `NikolaSettings()` directly
    (e.g. in tests) is fine and supported, but skips the friendly error
    wrapping the loader provides.
    """

    model_config = SettingsConfigDict(
        env_prefix="NIKOLA_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
    )

    app: AppSettings = Field(default_factory=AppSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Define the layered source priority described in the class docstring.

        `pydantic-settings` resolves sources in the order returned here,
        where EARLIER entries take priority over LATER ones. We import the
        YAML source lazily, inside this method, to keep this module's
        top-level imports limited to `pydantic`/`pydantic_settings` — the
        YAML source's file-path configuration is injected by the loader
        (see `nikola.infrastructure.config.loader`), not hardcoded here.
        """
        from nikola.infrastructure.config.yaml_source import YamlConfigSettingsSource

        yaml_settings = YamlConfigSettingsSource(settings_cls)

        return (
            init_settings,
            env_settings,
            dotenv_settings,
            yaml_settings,
            file_secret_settings,
        )
