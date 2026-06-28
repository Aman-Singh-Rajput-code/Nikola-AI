"""Domain-specific exception hierarchy (PermissionDeniedError, InvalidPlanError, etc.).

Sprint 2 adds the base `NikolaError` hierarchy and configuration-specific
errors. Further subtypes are added in later sprints as each layer needs them.
"""

from nikola.domain.errors.domain_errors import (
    ConfigFileNotFoundError,
    ConfigurationError,
    ConfigValidationError,
    NikolaError,
)

__all__ = [
    "NikolaError",
    "ConfigurationError",
    "ConfigFileNotFoundError",
    "ConfigValidationError",
]
