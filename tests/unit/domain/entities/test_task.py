"""Unit tests for `nikola.domain.entities.task.Task`.

Covers the task lifecycle state machine in detail: every valid
transition, every invalid transition (which must raise `ValueError`
rather than silently corrupting state), and the `is_terminal` helper.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from nikola.domain.entities.task import Task
from nikola.domain.value_objects.command_id import CommandId
from nikola.domain.value_objects.enums import TaskStatus
from nikola.domain.value_objects.task_id import TaskId


def _new_task() -> Task:
    return Task.create(command_id=CommandId.generate())


@pytest.mark.unit
class TestTaskCreate:
    def test_create_starts_in_pending_status(self) -> None:
        task = _new_task()
        assert task.status == TaskStatus.PENDING

    def test_create_generates_a_task_id(self) -> None:
        task = _new_task()
        assert isinstance(task.id, TaskId)

    def test_create_sets_created_at(self) -> None:
        task = _new_task()
        assert isinstance(task.created_at, datetime)

    def test_create_leaves_started_and_finished_at_unset(self) -> None:
        task = _new_task()
        assert task.started_at is None
        assert task.finished_at is None

    def test_create_leaves_error_message_unset(self) -> None:
        task = _new_task()
        assert task.error_message is None


@pytest.mark.unit
class TestTaskStart:
    def test_start_transitions_to_in_progress(self) -> None:
        task = _new_task()
        task.start()
        assert task.status == TaskStatus.IN_PROGRESS

    def test_start_sets_started_at(self) -> None:
        task = _new_task()
        task.start()
        assert task.started_at is not None

    def test_starting_a_non_pending_task_raises(self) -> None:
        task = _new_task()
        task.start()
        with pytest.raises(ValueError, match="only a 'pending' task can be started"):
            task.start()


@pytest.mark.unit
class TestTaskComplete:
    def test_complete_transitions_to_completed(self) -> None:
        task = _new_task()
        task.start()
        task.complete()
        assert task.status == TaskStatus.COMPLETED

    def test_complete_sets_finished_at(self) -> None:
        task = _new_task()
        task.start()
        task.complete()
        assert task.finished_at is not None

    def test_completing_a_pending_task_raises(self) -> None:
        task = _new_task()
        with pytest.raises(ValueError, match="only an 'in_progress' task can be completed"):
            task.complete()

    def test_completing_an_already_completed_task_raises(self) -> None:
        task = _new_task()
        task.start()
        task.complete()
        with pytest.raises(ValueError):
            task.complete()


@pytest.mark.unit
class TestTaskFail:
    def test_fail_transitions_to_failed(self) -> None:
        task = _new_task()
        task.start()
        task.fail("something broke")
        assert task.status == TaskStatus.FAILED

    def test_fail_records_the_error_message(self) -> None:
        task = _new_task()
        task.start()
        task.fail("something broke")
        assert task.error_message == "something broke"

    def test_fail_sets_finished_at(self) -> None:
        task = _new_task()
        task.start()
        task.fail("something broke")
        assert task.finished_at is not None

    def test_failing_a_pending_task_raises(self) -> None:
        task = _new_task()
        with pytest.raises(ValueError, match="only an 'in_progress' task can be failed"):
            task.fail("oops")

    def test_failing_with_empty_message_raises(self) -> None:
        task = _new_task()
        task.start()
        with pytest.raises(ValueError, match="error_message must not be empty"):
            task.fail("")

    def test_failing_with_whitespace_only_message_raises(self) -> None:
        task = _new_task()
        task.start()
        with pytest.raises(ValueError, match="error_message must not be empty"):
            task.fail("   ")


@pytest.mark.unit
class TestTaskCancel:
    def test_cancel_from_pending_transitions_to_cancelled(self) -> None:
        task = _new_task()
        task.cancel()
        assert task.status == TaskStatus.CANCELLED

    def test_cancel_from_in_progress_transitions_to_cancelled(self) -> None:
        task = _new_task()
        task.start()
        task.cancel()
        assert task.status == TaskStatus.CANCELLED

    def test_cancel_sets_finished_at(self) -> None:
        task = _new_task()
        task.cancel()
        assert task.finished_at is not None

    @pytest.mark.parametrize("setup", ["complete", "fail", "cancel"])
    def test_cancelling_a_terminal_task_raises(self, setup: str) -> None:
        task = _new_task()
        task.start()
        if setup == "complete":
            task.complete()
        elif setup == "fail":
            task.fail("oops")
        else:
            task.cancel()

        with pytest.raises(ValueError, match="already in terminal status"):
            task.cancel()


@pytest.mark.unit
class TestTaskIsTerminal:
    def test_pending_is_not_terminal(self) -> None:
        assert _new_task().is_terminal is False

    def test_in_progress_is_not_terminal(self) -> None:
        task = _new_task()
        task.start()
        assert task.is_terminal is False

    def test_completed_is_terminal(self) -> None:
        task = _new_task()
        task.start()
        task.complete()
        assert task.is_terminal is True

    def test_failed_is_terminal(self) -> None:
        task = _new_task()
        task.start()
        task.fail("oops")
        assert task.is_terminal is True

    def test_cancelled_is_terminal(self) -> None:
        task = _new_task()
        task.cancel()
        assert task.is_terminal is True
