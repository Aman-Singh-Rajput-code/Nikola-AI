"""Domain-specific exception hierarchy.

All exceptions raised intentionally by Nikola AI's own code (as opposed to
exceptions raised by third-party libraries) should ultimately inherit from
`NikolaError`. This gives calling code one place to catch "something Nikola
itself decided was wrong" versus an unexpected third-party failure, and lets
each layer's own error subtype carry the specific context that layer cares
about.

Sprint 2 introduces the first concrete errors: configuration failures. Later
sprints (Planner, Permissions, Tool Registry, etc.) will add their own
subtrees here without needing to change this base.
"""

from __future__ import annotations


class NikolaError(Exception):
    """Base class for all exceptions raised intentionally by Nikola AI."""


class ConfigurationError(NikolaError):
    """Raised when configuration cannot be loaded or fails validation.

    This is the error type that crosses the infrastructure -> application
    boundary when configuration is invalid. Infrastructure-layer code
    (the config loader) is responsible for catching lower-level exceptions
    such as `pydantic.ValidationError` or `yaml.YAMLError` and re-raising
    them as a `ConfigurationError` (or one of its subclasses below) with a
    clear, human-readable message — callers above the infrastructure layer
    should never need to know that Pydantic or PyYAML exist.
    """


class ConfigFileNotFoundError(ConfigurationError):
    """Raised when a required configuration file is missing.

    Reserved for cases where a config file is mandatory. Sprint 2 currently
    only requires `config/default.yaml`. Note: this is deliberately NOT
    named to shadow the Python built-in `FileNotFoundError`; it inherits
    from `ConfigurationError`, not from `OSError`, since a missing config
    file is a configuration problem, not a generic I/O problem, from the
    point of view of code that depends on this port.
    """


class ConfigValidationError(ConfigurationError):
    """Raised when configuration values fail schema validation.

    Carries a pre-formatted, human-readable message describing every
    invalid field at once (not just the first one), so a person fixing
    their configuration sees the whole picture in a single failed run
    instead of fixing one error only to immediately hit the next.
    """
