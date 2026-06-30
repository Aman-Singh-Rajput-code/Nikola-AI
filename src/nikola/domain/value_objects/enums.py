"""Domain enums for the core entities: `TaskStatus`, `CommandType`, `ResponseType`.

Modeled as `StrEnum` (matching the convention already established by
`Environment`/`LogLevel` in the configuration layer) so that values
serialize cleanly to plain strings and read naturally in logs, error
messages, and any future persistence layer, without needing a separate
`.value` access everywhere.

Each enum's members are deliberately scoped to what currently exists in
the domain model — they are not pre-populated with values for systems
(Planner, Tool Registry, Brain) that have not been implemented yet.
"""

from __future__ import annotations

from enum import StrEnum

__all__ = ["TaskStatus", "CommandType", "ResponseType"]


class TaskStatus(StrEnum):
    """The lifecycle state of a `Task`.

    A task progresses from `PENDING` to `IN_PROGRESS`, and then to exactly
    one terminal state: `COMPLETED`, `FAILED`, or `CANCELLED`. `Task`
    itself is responsible for enforcing that only valid transitions occur
    (see `nikola.domain.entities.task.Task`); this enum only defines the
    set of states that exist.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandType(StrEnum):
    """The kind of request a `Command` represents.

    `CHAT` is a conversational, natural-language request with no specific
    tool targeted. `TOOL_INVOCATION` is a request to run a specific named
    tool. Both are already implied by the architecture's information-flow
    design even though the Tool Registry and Brain that would act on a
    `CommandType` do not exist yet as of Sprint 4.
    """

    CHAT = "chat"
    TOOL_INVOCATION = "tool_invocation"


class ResponseType(StrEnum):
    """The kind of outcome a `Response` represents.

    `TEXT` is a successful, natural-language reply. `ERROR` indicates
    that something went wrong while producing a response to a `Command`.
    """

    TEXT = "text"
    ERROR = "error"
