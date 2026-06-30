"""Cross-type tests for the identifier value objects.

Confirms `CommandId`, `TaskId`, and `SessionId` are genuinely distinct
types — not interchangeable just because they happen to wrap the same
kind of string — which is the entire reason they exist as separate
classes rather than one shared generic identifier.
"""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.command_id import CommandId
from nikola.domain.value_objects.session_id import SessionId
from nikola.domain.value_objects.task_id import TaskId


@pytest.mark.unit
class TestIdentifierTypesAreDistinct:
    def test_command_id_and_task_id_with_same_value_are_not_equal(self) -> None:
        same_value = "11111111-1111-1111-1111-111111111111"
        command_id, task_id = CommandId(value=same_value), TaskId(value=same_value)
        assert command_id != task_id  # type: ignore[comparison-overlap]

    def test_task_id_and_session_id_with_same_value_are_not_equal(self) -> None:
        same_value = "11111111-1111-1111-1111-111111111111"
        task_id, session_id = TaskId(value=same_value), SessionId(value=same_value)
        assert task_id != session_id  # type: ignore[comparison-overlap]

    def test_command_id_and_session_id_with_same_value_are_not_equal(self) -> None:
        same_value = "11111111-1111-1111-1111-111111111111"
        command_id, session_id = CommandId(value=same_value), SessionId(value=same_value)
        assert command_id != session_id  # type: ignore[comparison-overlap]

    def test_generated_ids_are_distinct_uuid_strings_across_types(self) -> None:
        command_id = CommandId.generate()
        task_id = TaskId.generate()
        session_id = SessionId.generate()

        values = {command_id.value, task_id.value, session_id.value}
        assert len(values) == 3
