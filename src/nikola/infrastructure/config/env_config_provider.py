"""Concrete `ConfigProviderPort` adapter backed by the layered settings loader.

This is the infrastructure-layer implementation of the port defined in
`nikola.domain.ports.config_provider_port`. It is the only place outside
`loader.py`/`settings.py`/`yaml_source.py` that knows configuration is
sourced from environment variables, `.env`, and YAML — application and
domain code interact with `ConfigProviderPort` only, never with this class's
concrete name, so a future alternative implementation (e.g. fetching config
from a remote service) can be swapped in without touching any caller.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nikola.domain.ports.config_provider_port import ConfigProviderPort
from nikola.infrastructure.config.loader import load_settings

if TYPE_CHECKING:
    from pathlib import Path

    from nikola.infrastructure.config.settings import NikolaSettings


class EnvConfigProvider(ConfigProviderPort):
    """Loads and exposes configuration sourced from env vars, `.env`, and YAML.

    Configuration is loaded once, at construction time — not lazily on
    first access — so that a `ConfigurationError` is raised as early as
    possible (at provider construction, which a future bootstrap/composition
    root will perform at application startup), rather than on whatever
    first call happens to touch configuration deep inside a request.
    """

    def __init__(
        self,
        *,
        yaml_path: str | Path | None = None,
        require_yaml_file: bool = False,
    ) -> None:
        """Construct the provider, eagerly loading and validating settings.

        Args:
            yaml_path: Optional explicit path to a YAML config file,
                forwarded to `load_settings`. Defaults to
                `config/default.yaml` when not given.
            require_yaml_file: Forwarded to `load_settings`. See its
                docstring for details.

        Raises:
            nikola.domain.errors.ConfigurationError: If configuration fails
                to load or validate. Raised immediately, here, during
                construction.
        """
        self._settings: NikolaSettings = load_settings(
            yaml_path=yaml_path,
            require_yaml_file=require_yaml_file,
        )

    def get_settings(self) -> NikolaSettings:
        return self._settings

    def get(self, key: str, default: Any = None) -> Any:
        """Look up a single value by dotted key path, e.g. `"logging.level"`.

        Traverses nested settings models attribute-by-attribute. Returns
        `default` if any segment along the path does not exist, rather than
        raising — this method is meant as a forgiving convenience accessor,
        not a substitute for the typed access `get_settings()` provides.
        """
        value: Any = self._settings
        for segment in key.split("."):
            if not hasattr(value, segment):
                return default
            value = getattr(value, segment)
        return value
