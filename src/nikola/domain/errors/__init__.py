"""Domain-specific exception hierarchy.

Sprint 2 added the base `NikolaError` hierarchy and configuration-specific
errors. Sprint 4 added command/execution errors. Sprint 5 added DI errors.
Sprint 6 added `BrainError`. Sprint 7 adds `ConversationError` and
`MessageValidationError`. Further subtypes are added in later sprints.
"""

from nikola.domain.errors.domain_errors import (
    BrainError,
    CircularDependencyError,
    CommandExecutionError,
    ConfigFileNotFoundError,
    ConfigurationError,
    ConfigValidationError,
    ConversationError,
    InvalidCommandError,
    MessageValidationError,
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
    "ConversationError",
    "MessageValidationError",
]
