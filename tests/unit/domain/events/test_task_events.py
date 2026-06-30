"""Unit tests for `nikola.domain.events.task_events`."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from nikola.domain.events.task_events import TaskCompleted, TaskStarted
from nikola.domain.value_objects.enums import TaskStatus
from nikola.domain.value_objects.task_id import TaskId


@pytest.mark.unit
class TestTaskStarted:
    def test_holds_the_given_task_id_and_timestamp(self) -> None:
        task_id = TaskId.generate()
        timestamp = datetime.now(UTC)

        event = TaskStarted(task_id=task_id, started_at=timestamp)

        assert event.task_id == task_id
        assert event.started_at == timestamp

    def test_is_immutable(self) -> None:
        event = TaskStarted(task_id=TaskId.generate(), started_at=datetime.now(UTC))
        with pytest.raises(AttributeError):
            event.started_at = datetime.now(UTC)  # type: ignore[misc]

    def test_equal_events_compare_equal(self) -> None:
        task_id = TaskId.generate()
        timestamp = datetime.now(UTC)
        assert TaskStarted(task_id=task_id, started_at=timestamp) == TaskStarted(
            task_id=task_id, started_at=timestamp
        )


@pytest.mark.unit
class TestTaskCompleted:
    def test_holds_the_given_fields(self) -> None:
        task_id = TaskId.generate()
        timestamp = datetime.now(UTC)

        event = TaskCompleted(task_id=task_id, completed_at=timestamp, status=TaskStatus.COMPLETED)

        assert event.task_id == task_id
        assert event.completed_at == timestamp
        assert event.status == TaskStatus.COMPLETED

    def test_is_immutable(self) -> None:
        event = TaskCompleted(
            task_id=TaskId.generate(), completed_at=datetime.now(UTC), status=TaskStatus.COMPLETED
        )
        with pytest.raises(AttributeError):
            event.status = TaskStatus.FAILED  # type: ignore[misc]

    def test_equal_events_compare_equal(self) -> None:
        task_id = TaskId.generate()
        timestamp = datetime.now(UTC)
        assert TaskCompleted(
            task_id=task_id, completed_at=timestamp, status=TaskStatus.COMPLETED
        ) == TaskCompleted(task_id=task_id, completed_at=timestamp, status=TaskStatus.COMPLETED)
