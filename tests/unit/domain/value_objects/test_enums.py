"""Unit tests for `nikola.domain.value_objects.enums`."""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.enums import CommandType, ResponseType, TaskStatus


@pytest.mark.unit
class TestTaskStatus:
    def test_has_expected_members(self) -> None:
        assert {member.value for member in TaskStatus} == {
            "pending",
            "in_progress",
            "completed",
            "failed",
            "cancelled",
        }

    def test_is_a_str_subclass(self) -> None:
        assert isinstance(TaskStatus.PENDING, str)

    def test_member_equals_its_string_value(self) -> None:
        assert TaskStatus.COMPLETED == "completed"  # type: ignore[comparison-overlap]


@pytest.mark.unit
class TestCommandType:
    def test_has_expected_members(self) -> None:
        assert {member.value for member in CommandType} == {"chat", "tool_invocation"}

    def test_is_a_str_subclass(self) -> None:
        assert isinstance(CommandType.CHAT, str)


@pytest.mark.unit
class TestResponseType:
    def test_has_expected_members(self) -> None:
        assert {member.value for member in ResponseType} == {"text", "error"}

    def test_is_a_str_subclass(self) -> None:
        assert isinstance(ResponseType.ERROR, str)
