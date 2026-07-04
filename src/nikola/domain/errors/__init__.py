"""Domain-specific exception hierarchy.

Sprint 2 added the base `NikolaError` hierarchy and configuration-specific
errors. Sprint 4 added the command/execution error vocabulary
(`InvalidCommandError`, `ToolUnavailableError`, `CommandExecutionError`).
Sprint 5 adds the dependency-injection error vocabulary
(`ServiceNotRegisteredError`, `CircularDependencyError`). Further subtypes
are added in later sprints as each layer needs them.
"""

from nikola.domain.errors.domain_errors import (
    BrainError,
    CircularDependencyError,
    CommandExecutionError,
    ConfigFileNotFoundError,
    ConfigurationError,
    ConfigValidationError,
    InvalidCommandError,
    NikolaError,
    ServiceNotRegisteredError,
    ToolUnavailableError,
)

__all__ = [
    "NikolaError",
    "ConfigurationError",
    "ConfigFileNotFoundError",
    "ConfigValidationError",
    "InvalidCommandError",
    "ToolUnavailableError",
    "CommandExecutionError",
    "ServiceNotRegisteredError",
    "CircularDependencyError",
    "BrainError",
]
