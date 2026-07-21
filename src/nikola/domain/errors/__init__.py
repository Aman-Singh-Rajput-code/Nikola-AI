"""Domain-specific exception hierarchy.

Sprint 2: configuration errors. Sprint 4: command/execution errors.
Sprint 5: DI errors. Sprint 6: BrainError. Sprint 7: ConversationError,
MessageValidationError. Sprint 8: MemoryError.
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
    MemoryError,
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
    "MemoryError",
]
