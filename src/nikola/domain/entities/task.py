"""`Task` — tracks the execution lifecycle of a single `Command`.

Unlike `Command` and `Response`, a `Task` is intentionally mutable: its
entire purpose is to record how a command's execution progresses over
time, from `PENDING` through to a terminal state. State transitions are
only ever performed through this class's own methods (`start()`,
`complete()`, `fail()`, `cancel()`) so that invalid transitions — for
example, completing a task that was never started — are rejected at the
point they're attempted, rather than silently producing an inconsistent
task.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from nikola.domain.value_objects.enums import TaskStatus
from nikola.domain.value_objects.task_id import TaskId

if TYPE_CHECKING:
    from nikola.domain.value_objects.command_id import CommandId

__all__ = ["Task"]


@dataclass(slots=True)
class Task:
    """Tracks the execution lifecycle of a `Command`.

    Attributes:
        id: The task's unique identifier.
        command_id: The `Command` this task is executing.
        status: The task's current lifecycle state. Only ever changed via
            `start()`, `complete()`, `fail()`, or `cancel()` — never set
            directly.
        created_at: When the task was created, in UTC.
        started_at: When `start()` was called, or `None` if the task has
            not started yet.
        finished_at: When the task reached a terminal state
            (`COMPLETED`, `FAILED`, or `CANCELLED`), or `None` if it has
            not yet finished.
        error_message: A human-readable description of why the task
            failed, set by `fail()`. `None` unless `status` is `FAILED`.
    """

    id: TaskId
    command_id: CommandId
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None

    @classmethod
    def create(cls, *, command_id: CommandId) -> Task:
        """Construct a new, `PENDING` `Task` with a freshly generated `TaskId`."""
        return cls(id=TaskId.generate(), command_id=command_id)

    def start(self) -> None:
        """Transition this task from `PENDING` to `IN_PROGRESS`.

        Raises:
            ValueError: If the task is not currently `PENDING`.
        """
        if self.status is not TaskStatus.PENDING:
            raise ValueError(
                f"Cannot start a task in status '{self.status}'; "
                f"only a 'pending' task can be started."
            )
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now(UTC)

    def complete(self) -> None:
        """Transition this task from `IN_PROGRESS` to `COMPLETED`.

        Raises:
            ValueError: If the task is not currently `IN_PROGRESS`.
        """
        if self.status is not TaskStatus.IN_PROGRESS:
            raise ValueError(
                f"Cannot complete a task in status '{self.status}'; "
                f"only an 'in_progress' task can be completed."
            )
        self.status = TaskStatus.COMPLETED
        self.finished_at = datetime.now(UTC)

    def fail(self, error_message: str) -> None:
        """Transition this task from `IN_PROGRESS` to `FAILED`.

        Args:
            error_message: A human-readable description of the failure.
                Must be non-empty.

        Raises:
            ValueError: If the task is not currently `IN_PROGRESS`, or if
                `error_message` is empty.
        """
        if self.status is not TaskStatus.IN_PROGRESS:
            raise ValueError(
                f"Cannot fail a task in status '{self.status}'; "
                f"only an 'in_progress' task can be failed."
            )
        if not error_message.strip():
            raise ValueError("error_message must not be empty when failing a task.")
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.finished_at = datetime.now(UTC)

    def cancel(self) -> None:
        """Transition this task to `CANCELLED` from `PENDING` or `IN_PROGRESS`.

        Raises:
            ValueError: If the task is already in a terminal state
                (`COMPLETED`, `FAILED`, or `CANCELLED`).
        """
        if self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            raise ValueError(
                f"Cannot cancel a task that is already in terminal status '{self.status}'."
            )
        self.status = TaskStatus.CANCELLED
        self.finished_at = datetime.now(UTC)

    @property
    def is_terminal(self) -> bool:
        """Whether this task has reached a state it will never leave."""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
