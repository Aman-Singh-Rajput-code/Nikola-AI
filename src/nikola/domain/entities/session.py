"""`Session` — groups a sequence of `Task`s under one interaction context.

A session is mutable: its purpose is to accumulate tasks as a
conversation/interaction progresses, so `add_task()` is the only way
tasks are added — there is no way to remove or replace a task once
recorded, since a session's history should not be rewritable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from nikola.domain.value_objects.session_id import SessionId

if TYPE_CHECKING:
    from nikola.domain.entities.task import Task

__all__ = ["Session"]


@dataclass(slots=True)
class Session:
    """An interaction context that accumulates `Task`s over its lifetime.

    Attributes:
        id: The session's unique identifier.
        created_at: When the session was created, in UTC.
        tasks: The tasks recorded so far in this session, in the order
            they were added. Treat as read-only from outside this class;
            use `add_task()` to append.
    """

    id: SessionId
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    tasks: list[Task] = field(default_factory=list)

    @classmethod
    def create(cls) -> Session:
        """Construct a new, empty `Session` with a freshly generated `SessionId`."""
        return cls(id=SessionId.generate())

    def add_task(self, task: Task) -> None:
        """Append `task` to this session's history.

        Args:
            task: The task to record. Its `command_id` is expected to
                reference a `Command` that was issued within this
                session, though this is not (and cannot be, at this
                layer) enforced without a repository to look the command
                up — that enforcement belongs to a future application-
                layer use case.
        """
        self.tasks.append(task)

    @property
    def task_count(self) -> int:
        """The number of tasks recorded in this session so far."""
        return len(self.tasks)
