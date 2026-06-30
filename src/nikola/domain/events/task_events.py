"""`TaskStarted` and `TaskCompleted` — domain events for the `Task` lifecycle.

Both are immutable, pure-data records of something that happened to a
`Task`. Sprint 4 defines their shape only; no event bus or publishing
mechanism exists yet to actually dispatch them — that is introduced by a
later, infrastructure-layer sprint (see `EventBusPort` in the
architecture). Nothing in this module constructs or fires these events
automatically; a future application-layer use case is expected to do so
when it calls `Task.start()` / `Task.complete()`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from nikola.domain.value_objects.enums import TaskStatus
    from nikola.domain.value_objects.task_id import TaskId

__all__ = ["TaskStarted", "TaskCompleted"]


@dataclass(frozen=True, slots=True)
class TaskStarted:
    """Recorded when a `Task` transitions from `PENDING` to `IN_PROGRESS`.

    Attributes:
        task_id: The task that started.
        started_at: When the transition occurred, in UTC.
    """

    task_id: TaskId
    started_at: datetime


@dataclass(frozen=True, slots=True)
class TaskCompleted:
    """Recorded when a `Task` successfully reaches `COMPLETED`.

    Scoped strictly to the successful-completion path: a task that ends
    in `FAILED` or `CANCELLED` is a different outcome and is not
    represented by this event. A future sprint may introduce dedicated
    `TaskFailed` / `TaskCancelled` events if that distinction proves
    useful to subscribers.

    Attributes:
        task_id: The task that completed.
        completed_at: When the task reached `COMPLETED`, in UTC.
        status: The task's final status. Always `TaskStatus.COMPLETED`
            for this event; included for convenience so subscribers do
            not need a separate lookup to confirm it.
    """

    task_id: TaskId
    completed_at: datetime
    status: TaskStatus
