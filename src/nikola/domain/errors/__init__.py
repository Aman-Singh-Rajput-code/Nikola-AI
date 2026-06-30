"""Domain-specific exception hierarchy.

Sprint 2 added the base `NikolaError` hierarchy and configuration-specific
errors. Sprint 4 adds the command/execution error vocabulary
(`InvalidCommandError`, `ToolUnavailableError`, `CommandExecutionError`).
Further subtypes are added in later sprints as each layer needs them.
"""

from nikola.domain.errors.domain_errors import (
    CommandExecutionError,
    ConfigFileNotFoundError,
    ConfigurationError,
    ConfigValidationError,
    InvalidCommandError,
    NikolaError,
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
]
