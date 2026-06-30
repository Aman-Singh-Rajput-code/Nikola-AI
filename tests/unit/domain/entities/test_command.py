"""Unit tests for `nikola.domain.entities.command.Command`."""

from __future__ import annotations

from datetime import datetime

import pytest

from nikola.domain.entities.command import Command
from nikola.domain.errors import InvalidCommandError
from nikola.domain.value_objects.command_id import CommandId
from nikola.domain.value_objects.enums import CommandType
from nikola.domain.value_objects.session_id import SessionId


@pytest.mark.unit
class TestCommandCreate:
    def test_create_generates_a_command_id(self) -> None:
        command = Command.create(
            session_id=SessionId.generate(),
            command_type=CommandType.CHAT,
            content="hello",
        )
        assert isinstance(command.id, CommandId)

    def test_create_sets_the_given_session_id(self) -> None:
        session_id = SessionId.generate()
        command = Command.create(
            session_id=session_id, command_type=CommandType.CHAT, content="hello"
        )
        assert command.session_id == session_id

    def test_create_sets_the_given_command_type_and_content(self) -> None:
        command = Command.create(
            session_id=SessionId.generate(),
            command_type=CommandType.TOOL_INVOCATION,
            content="run the thing",
        )
        assert command.command_type == CommandType.TOOL_INVOCATION
        assert command.content == "run the thing"

    def test_create_sets_a_created_at_timestamp(self) -> None:
        command = Command.create(
            session_id=SessionId.generate(), command_type=CommandType.CHAT, content="hello"
        )
        assert isinstance(command.created_at, datetime)

    def test_two_created_commands_have_different_ids(self) -> None:
        session_id = SessionId.generate()
        first = Command.create(session_id=session_id, command_type=CommandType.CHAT, content="a")
        second = Command.create(session_id=session_id, command_type=CommandType.CHAT, content="b")
        assert first.id != second.id


@pytest.mark.unit
class TestCommandValidation:
    def test_empty_content_is_rejected(self) -> None:
        with pytest.raises(InvalidCommandError):
            Command.create(
                session_id=SessionId.generate(), command_type=CommandType.CHAT, content=""
            )

    def test_whitespace_only_content_is_rejected(self) -> None:
        with pytest.raises(InvalidCommandError):
            Command.create(
                session_id=SessionId.generate(), command_type=CommandType.CHAT, content="   "
            )

    def test_rejection_also_applies_to_direct_construction(self) -> None:
        """__post_init__ validation must fire regardless of how the command is built."""
        with pytest.raises(InvalidCommandError):
            Command(
                id=CommandId.generate(),
                session_id=SessionId.generate(),
                command_type=CommandType.CHAT,
                content="",
            )


@pytest.mark.unit
class TestCommandImmutability:
    def test_content_cannot_be_reassigned(self) -> None:
        command = Command.create(
            session_id=SessionId.generate(), command_type=CommandType.CHAT, content="hello"
        )
        with pytest.raises(AttributeError):
            command.content = "mutated"  # type: ignore[misc]
