"""`Response` — an immutable record of the outcome produced for a `Command`.

Like `Command`, a `Response` is a historical fact once created: it
represents what was returned to the caller and is never edited after the
fact. If a new attempt is needed, a new `Response` (for a new `Command`,
or associated with a re-run `Task`) is created rather than mutating an
existing one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from nikola.domain.value_objects.enums import ResponseType

if TYPE_CHECKING:
    from nikola.domain.value_objects.command_id import CommandId

__all__ = ["Response"]


@dataclass(frozen=True, slots=True)
class Response:
    """An immutable outcome produced for a `Command`.

    Attributes:
        command_id: The `Command` this response answers.
        response_type: Whether this is a successful `TEXT` reply or an
            `ERROR` outcome.
        content: The response body — the reply text, or a description of
            the error.
        created_at: When the response was produced, in UTC.
    """

    command_id: CommandId
    response_type: ResponseType
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def text(cls, *, command_id: CommandId, content: str) -> Response:
        """Construct a successful, `TEXT`-typed `Response`."""
        return cls(command_id=command_id, response_type=ResponseType.TEXT, content=content)

    @classmethod
    def error(cls, *, command_id: CommandId, content: str) -> Response:
        """Construct an `ERROR`-typed `Response` describing what went wrong."""
        return cls(command_id=command_id, response_type=ResponseType.ERROR, content=content)

    @property
    def is_error(self) -> bool:
        """Whether this response represents an error outcome."""
        return self.response_type is ResponseType.ERROR
