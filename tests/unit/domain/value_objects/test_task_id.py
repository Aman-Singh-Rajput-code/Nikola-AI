"""Unit tests for `nikola.domain.value_objects.task_id.TaskId`."""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.task_id import TaskId


@pytest.mark.unit
class TestTaskIdGeneration:
    def test_generate_returns_a_task_id(self) -> None:
        task_id = TaskId.generate()
        assert isinstance(task_id, TaskId)

    def test_generate_produces_unique_values(self) -> None:
        first = TaskId.generate()
        second = TaskId.generate()
        assert first != second
        assert first.value != second.value


@pytest.mark.unit
class TestTaskIdEquality:
    def test_equal_values_are_equal(self) -> None:
        assert TaskId(value="abc-123") == TaskId(value="abc-123")

    def test_different_values_are_not_equal(self) -> None:
        assert TaskId(value="abc-123") != TaskId(value="xyz-789")

    def test_is_hashable_and_usable_in_a_set(self) -> None:
        ids = {TaskId(value="a"), TaskId(value="a"), TaskId(value="b")}
        assert len(ids) == 2


@pytest.mark.unit
class TestTaskIdImmutability:
    def test_value_cannot_be_reassigned(self) -> None:
        task_id = TaskId(value="abc-123")
        with pytest.raises(AttributeError):
            task_id.value = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestTaskIdValidation:
    def test_empty_string_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            TaskId(value="")


@pytest.mark.unit
class TestTaskIdStringRepresentation:
    def test_str_returns_the_underlying_value(self) -> None:
        task_id = TaskId(value="abc-123")
        assert str(task_id) == "abc-123"
