"""Domain-specific exception hierarchy.

All exceptions raised intentionally by Nikola AI's own code (as opposed to
exceptions raised by third-party libraries) should ultimately inherit from
`NikolaError`. This gives calling code one place to catch "something Nikola
itself decided was wrong" versus an unexpected third-party failure, and lets
each layer's own error subtype carry the specific context that layer cares
about.

Sprint 2 introduced the first concrete errors: configuration failures.
Sprint 4 added the core command/execution error vocabulary
(`InvalidCommandError`, `ToolUnavailableError`, `CommandExecutionError`).
Sprint 5 added the dependency-injection error vocabulary
(`ServiceNotRegisteredError`, `CircularDependencyError`).
Sprint 6 adds the Brain-layer error vocabulary (`BrainError`). Later
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


class InvalidCommandError(NikolaError):
    """Raised when a `Command` is malformed and cannot be processed.

    A validation-time error: the command never reaches execution because
    its shape or content is invalid (e.g. empty content). Distinct from
    `CommandExecutionError`, which covers failures that occur while a
    well-formed command is actually being carried out.
    """


class ToolUnavailableError(NikolaError):
    """Raised when a `Command` requests a tool that is not available.

    The Tool Registry that would actually raise this in practice does not
    exist until a later sprint; this exception is defined now as part of
    the domain's vocabulary so that future infrastructure code has a
    stable, already-agreed type to raise and callers have a stable type
    to catch.
    """


class CommandExecutionError(NikolaError):
    """Raised when a well-formed `Command` fails while being executed.

    Covers execution-time failures not already covered by the more
    specific `InvalidCommandError` (malformed before execution started)
    or `ToolUnavailableError` (the requested tool does not exist). Use
    this for failures that occur once execution is genuinely underway.
    """


class ServiceNotRegisteredError(NikolaError):
    """Raised when `ServiceContainer.resolve()` is asked for an unregistered type.

    Distinguishes "this dependency was never wired up" from a generic
    `KeyError`, so calling code (and humans reading a traceback) can tell
    at a glance that the problem is a missing service registration in the
    composition root, not an unrelated dictionary lookup failure.
    """


class CircularDependencyError(NikolaError):
    """Raised when resolving a service would require resolving itself.

    Detected during constructor-injected (transient) resolution, when the
    chain of types currently being resolved is asked to resolve a type
    already in that same chain. Raised instead of allowing infinite
    recursion to exhaust the call stack with a much less informative
    `RecursionError`.
    """


class BrainError(NikolaError):
    """Raised when the Brain fails to produce a valid reasoning response.

    The concrete infrastructure adapters (Claude, OpenAI, Ollama, etc.)
    are responsible for catching their own SDK/network exceptions and
    re-raising them as `BrainError` (or a future subclass) so that
    calling code — Planner, Orchestrator, Agent — only ever needs to
    catch `BrainError`, regardless of which provider is active.

    Examples of conditions that should raise `BrainError`:
    - A provider's context window is exceeded
    - A provider returns a malformed or unparseable response
    - A provider rate-limits the request
    - The selected provider is not available or misconfigured

    Note: `BrainError` is defined in the domain layer so that domain and
    application code can reference it without importing anything from
    `infrastructure/`. The concrete adapters that raise it are
    deliberately in `infrastructure/brains/`.
    """


class ConversationError(NikolaError):
    """Base class for failures originating in the conversation layer.

    Covers invalid state transitions (e.g. adding a message to a
    deleted conversation), missing conversations, and other conversation-
    lifecycle violations. Callers that need to handle any conversation
    problem uniformly can catch this base class.
    """


class MessageValidationError(NikolaError):
    """Raised when a `Message` or message-addition request is invalid.

    Distinct from `ConversationError` (which covers conversation-level
    state problems) — `MessageValidationError` covers problems with the
    message itself: empty content, invalid role, or a `conversation_id`
    that does not match the target conversation.
    """
