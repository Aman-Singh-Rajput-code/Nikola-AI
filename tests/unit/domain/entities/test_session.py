"""Unit tests for `nikola.domain.entities.session.Session`."""

from __future__ import annotations

from datetime import datetime

import pytest

from nikola.domain.entities.session import Session
from nikola.domain.entities.task import Task
from nikola.domain.value_objects.command_id import CommandId
from nikola.domain.value_objects.session_id import SessionId


@pytest.mark.unit
class TestSessionCreate:
    def test_create_generates_a_session_id(self) -> None:
        session = Session.create()
        assert isinstance(session.id, SessionId)

    def test_create_sets_created_at(self) -> None:
        session = Session.create()
        assert isinstance(session.created_at, datetime)

    def test_create_starts_with_no_tasks(self) -> None:
        session = Session.create()
        assert session.tasks == []
        assert session.task_count == 0

    def test_two_created_sessions_have_different_ids(self) -> None:
        assert Session.create().id != Session.create().id


@pytest.mark.unit
class TestSessionAddTask:
    def test_add_task_appends_to_tasks(self) -> None:
        session = Session.create()
        task = Task.create(command_id=CommandId.generate())

        session.add_task(task)

        assert session.tasks == [task]

    def test_add_task_increments_task_count(self) -> None:
        session = Session.create()
        session.add_task(Task.create(command_id=CommandId.generate()))
        session.add_task(Task.create(command_id=CommandId.generate()))

        assert session.task_count == 2

    def test_tasks_preserve_insertion_order(self) -> None:
        session = Session.create()
        first = Task.create(command_id=CommandId.generate())
        second = Task.create(command_id=CommandId.generate())

        session.add_task(first)
        session.add_task(second)

        assert session.tasks == [first, second]


@pytest.mark.unit
class TestSessionMutability:
    def test_session_id_cannot_be_reassigned_via_normal_attribute_access_misuse(self) -> None:
        """Session itself is mutable (slots-based dataclass, not frozen).

        This test exists to document that mutability is intentional for
        Session as a whole (it accumulates tasks), while individual
        fields can still technically be reassigned directly — callers are
        expected to use add_task() rather than appending to .tasks or
        reassigning .id directly, but nothing at this layer enforces that
        beyond convention, since Session is not frozen.
        """
        session = Session.create()
        new_id = SessionId.generate()
        session.id = new_id  # not raising confirms Session is mutable, as designed
        assert session.id == new_id
