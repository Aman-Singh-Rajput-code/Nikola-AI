"""Abstract contract for configuration providers.

This port lets the domain and application layers depend on "a thing that can
give me configuration" without knowing or caring whether that configuration
actually comes from a YAML file, environment variables, a remote config
service, or — in tests — a hand-built in-memory object.

Per the Dependency Inversion Principle, this interface is owned by the
domain layer. The concrete implementation
(`nikola.infrastructure.config.env_config_provider.EnvConfigProvider`) lives
in the infrastructure layer and is the only place allowed to know about
`.env` files, `os.environ`, or YAML parsing.

Design note: the port is intentionally narrow. It exposes the fully-typed,
already-validated settings object via `get_settings()`, plus a single
generic `get(key, default)` escape hatch for ad-hoc lookups (e.g. a future
plugin reading a key it doesn't have a dedicated typed field for). It does
NOT expose anything about *how* configuration was sourced or merged — that
is an infrastructure concern and leaking it here would violate the layer
boundary.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Imported only for type checking to avoid a hard runtime dependency from
    # domain/ on the concrete settings module's transitive imports (pydantic).
    # NOTE: domain/ is meant to be free of third-party dependencies; this
    # import is deferred and exists solely so type checkers can verify the
    # return type of get_settings(). See ARCHITECTURE.md for the rationale
    # behind keeping ports here while letting infrastructure define the
    # concrete settings shape.
    from nikola.infrastructure.config.settings import NikolaSettings


class ConfigProviderPort(ABC):
    """Port defining read access to fully-resolved, validated configuration."""

    @abstractmethod
    def get_settings(self) -> NikolaSettings:
        """Return the fully validated, strongly-typed settings object.

        Implementations must guarantee that, by the time this method can be
        called successfully, configuration has already been validated.
        Implementations should raise a `ConfigurationError` (or subclass)
        at load time, not lazily here, so failures surface as early as
        possible — see the "fail fast" requirement in the architecture.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Return a single configuration value by dotted key path.

        Example: `get("logging.level")`.

        This is an escape hatch for callers that need a value without a
        dedicated typed accessor. Prefer `get_settings()` wherever a typed
        field already exists.
        """
        raise NotImplementedError
