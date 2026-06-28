"""Configuration schema and providers implementing ConfigProviderPort.

Sprint 2 implements the full configuration layer:

- `settings.py` — typed Pydantic models (`NikolaSettings`, `AppSettings`,
  `LoggingSettings`) defining the configuration schema and layered source
  priority (env vars > .env > config/default.yaml > defaults).
- `yaml_source.py` — the custom `pydantic-settings` source that reads
  `config/default.yaml` as a settings layer.
- `loader.py` — `load_settings()`, the fail-fast entry point that builds and
  validates a `NikolaSettings` instance, wrapping failures in domain
  `ConfigurationError`s.
- `env_config_provider.py` — `EnvConfigProvider`, the concrete
  `ConfigProviderPort` implementation that application/domain code should
  depend on.
"""

from nikola.infrastructure.config.env_config_provider import EnvConfigProvider
from nikola.infrastructure.config.loader import load_settings
from nikola.infrastructure.config.settings import (
    AppSettings,
    Environment,
    LoggingSettings,
    LogLevel,
    NikolaSettings,
)

__all__ = [
    "EnvConfigProvider",
    "load_settings",
    "NikolaSettings",
    "AppSettings",
    "LoggingSettings",
    "Environment",
    "LogLevel",
]
