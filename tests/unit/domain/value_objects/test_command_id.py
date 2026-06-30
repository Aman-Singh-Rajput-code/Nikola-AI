"""Unit tests for `nikola.domain.value_objects.command_id.CommandId`."""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.command_id import CommandId


@pytest.mark.unit
class TestCommandIdGeneration:
    def test_generate_returns_a_command_id(self) -> None:
        command_id = CommandId.generate()
        assert isinstance(command_id, CommandId)

    def test_generate_produces_unique_values(self) -> None:
        first = CommandId.generate()
        second = CommandId.generate()
        assert first != second
        assert first.value != second.value


@pytest.mark.unit
class TestCommandIdEquality:
    def test_equal_values_are_equal(self) -> None:
        assert CommandId(value="abc-123") == CommandId(value="abc-123")

    def test_different_values_are_not_equal(self) -> None:
        assert CommandId(value="abc-123") != CommandId(value="xyz-789")

    def test_is_hashable_and_usable_in_a_set(self) -> None:
        ids = {CommandId(value="a"), CommandId(value="a"), CommandId(value="b")}
        assert len(ids) == 2


@pytest.mark.unit
class TestCommandIdImmutability:
    def test_value_cannot_be_reassigned(self) -> None:
        command_id = CommandId(value="abc-123")
        with pytest.raises(AttributeError):
            command_id.value = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestCommandIdValidation:
    def test_empty_string_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            CommandId(value="")


@pytest.mark.unit
class TestCommandIdStringRepresentation:
    def test_str_returns_the_underlying_value(self) -> None:
        command_id = CommandId(value="abc-123")
        assert str(command_id) == "abc-123"
