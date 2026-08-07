"""Domain-specific exception hierarchy. Sprint 9 adds PlanningError."""

from nikola.domain.errors.domain_errors import (
    BrainError,
    CircularDependencyError,
    CommandExecutionError,
    ConfigFileNotFoundError,
    ConfigurationError,
    ConfigValidationError,
    ConversationError,
    InvalidCommandError,
    MemoryError,
    MessageValidationError,
    NikolaError,
    PlanningError,
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
    "MemoryError",
    "PlanningError",
]
