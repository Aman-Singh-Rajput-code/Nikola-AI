"""`Command` — an immutable record of a single incoming request.

A command represents what was asked, not what happened as a result of
asking it — execution and outcome tracking belong to `Task` and `Response`
respectively. Once issued, a command is a historical fact: it is never
mutated, only superseded by later commands.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from nikola.domain.errors.domain_errors import InvalidCommandError
from nikola.domain.value_objects.command_id import CommandId

if TYPE_CHECKING:
    from nikola.domain.value_objects.enums import CommandType
    from nikola.domain.value_objects.session_id import SessionId

__all__ = ["Command"]


@dataclass(frozen=True, slots=True)
class Command:
    """An immutable request issued within a `Session`.

    Attributes:
        id: The command's unique identifier.
        session_id: The `Session` this command was issued within.
        command_type: Whether this is a conversational `CHAT` request or
            a `TOOL_INVOCATION` request for a specific tool.
        content: The raw text or payload of the request. Must be
            non-empty — a command with no content is meaningless and is
            rejected at construction time.
        created_at: When the command was issued, in UTC.

    Raises:
        InvalidCommandError: If `content` is empty or whitespace-only.
    """

    id: CommandId
    session_id: SessionId
    command_type: CommandType
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise InvalidCommandError("Command content must not be empty.")

    @classmethod
    def create(
        cls,
        *,
        session_id: SessionId,
        command_type: CommandType,
        content: str,
    ) -> Command:
        """Construct a new `Command` with a freshly generated `CommandId`.

        Preferred over calling the constructor directly for new commands,
        since it removes the need for callers to generate a `CommandId`
        themselves.
        """
        return cls(
            id=CommandId.generate(),
            session_id=session_id,
            command_type=command_type,
            content=content,
        )
