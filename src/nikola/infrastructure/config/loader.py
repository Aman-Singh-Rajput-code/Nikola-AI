"""Configuration loading and fail-fast validation.

This module is the single entry point application code should use to obtain
validated configuration: `load_settings()`. It exists separately from
`settings.py` (the schema) and `yaml_source.py` (the YAML source mechanics)
so that "how do we construct settings and what happens when it fails" is one
clearly testable place.

Fail-fast contract
-------------------
`load_settings()` either returns a fully valid `NikolaSettings` instance, or
raises a `nikola.domain.errors.ConfigurationError` subclass with a message
that lists every invalid field at once. It never returns a partially valid
or partially defaulted object, and it never lets a raw `pydantic.ValidationError`
or `yaml.YAMLError` escape to the caller — those are implementation details
of *how* configuration happens to be validated/parsed today, not something
calling code (or future Brain/Planner/Agent code) should need to know about
or catch directly.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from nikola.domain.errors import ConfigFileNotFoundError, ConfigValidationError
from nikola.infrastructure.config.settings import NikolaSettings
from nikola.infrastructure.config.yaml_source import DEFAULT_YAML_CONFIG_PATH

__all__ = ["load_settings"]


def load_settings(
    *,
    yaml_path: str | Path | None = None,
    require_yaml_file: bool = False,
) -> NikolaSettings:
    """Load, merge, and validate Nikola AI configuration.

    Resolution priority (highest wins): environment variables > `.env` file
    > YAML file (`config/default.yaml` by default) > field defaults. The
    actual source-priority wiring lives on `NikolaSettings` itself
    (`settings_customise_sources`); this function's job is orchestration and
    error handling around that.

    Args:
        yaml_path: Explicit path to a YAML config file, overriding the
            default `config/default.yaml` lookup. Primarily intended for
            tests that want to load a fixture file without mutating
            environment variables or the real default config.
        require_yaml_file: If True, raise `ConfigFileNotFoundError` when the
            resolved YAML path does not exist. Defaults to False because
            field defaults alone produce a valid configuration; callers
            that want to guarantee an explicit, checked-in config file is
            present (e.g. the CLI at real startup) should pass True.

    Returns:
        A fully validated `NikolaSettings` instance.

    Raises:
        ConfigFileNotFoundError: If `require_yaml_file` is True and the
            resolved YAML file does not exist.
        ConfigValidationError: If the merged configuration fails schema
            validation, or if the YAML file exists but is not valid YAML /
            not a top-level mapping.
    """
    resolved_yaml_path = Path(yaml_path) if yaml_path is not None else DEFAULT_YAML_CONFIG_PATH

    if require_yaml_file and not resolved_yaml_path.is_file():
        raise ConfigFileNotFoundError(
            f"Required configuration file not found: '{resolved_yaml_path}'. "
            f"Expected a YAML file at this path (relative to the current "
            f"working directory unless an absolute path was given)."
        )

    try:
        return _build_settings(resolved_yaml_path)
    except ValidationError as exc:
        raise ConfigValidationError(_format_validation_error(exc, resolved_yaml_path)) from exc
    except yaml.YAMLError as exc:
        raise ConfigValidationError(
            f"Configuration file '{resolved_yaml_path}' contains invalid YAML " f"syntax: {exc}"
        ) from exc
    except ValueError as exc:
        # Raised by YamlConfigSettingsSource when the YAML file's top-level
        # structure isn't a mapping (e.g. a YAML list or scalar).
        raise ConfigValidationError(str(exc)) from exc


def _build_settings(yaml_path: Path) -> NikolaSettings:
    """Construct `NikolaSettings`, pointed at the given YAML path.

    `NikolaSettings.settings_customise_sources` constructs its own
    `YamlConfigSettingsSource` without knowing the caller's desired path (it
    falls back to `config/default.yaml` or the `NIKOLA_CONFIG_FILE`
    environment variable — see `yaml_source.py`). To honor an explicit
    `yaml_path` argument passed to `load_settings()` without changing that
    default-resolution logic, we temporarily set the override environment
    variable for the duration of construction, then restore it. This keeps
    the override mechanism in exactly one place (the environment variable
    already defined in `yaml_source.py`) rather than threading a path
    parameter through Pydantic's source-construction machinery, which does
    not have a clean extension point for extra constructor arguments.
    """
    import os

    from nikola.infrastructure.config.yaml_source import YAML_CONFIG_PATH_ENV_VAR

    previous_value = os.environ.get(YAML_CONFIG_PATH_ENV_VAR)
    os.environ[YAML_CONFIG_PATH_ENV_VAR] = str(yaml_path)
    try:
        return NikolaSettings()
    finally:
        if previous_value is None:
            os.environ.pop(YAML_CONFIG_PATH_ENV_VAR, None)
        else:
            os.environ[YAML_CONFIG_PATH_ENV_VAR] = previous_value


def _format_validation_error(exc: ValidationError, yaml_path: Path) -> str:
    """Render a `pydantic.ValidationError` as one human-readable message.

    Lists every invalid field on its own line, with its location and the
    underlying problem, so a person fixing a broken configuration sees the
    full picture in one run rather than fixing one field only to immediately
    hit the next. This is the concrete mechanism behind the "fail fast with
    meaningful errors" requirement.
    """
    lines = [
        f"Invalid configuration ({len(exc.errors())} issue(s) found; "
        f"checked environment variables, .env, and '{yaml_path}'):"
    ]
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"]) or "<root>"
        lines.append(f"  - {location}: {error['msg']}")
    return "\n".join(lines)
