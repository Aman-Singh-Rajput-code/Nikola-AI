"""Unit tests for `nikola.domain.entities.message.Message`."""

from __future__ import annotations

from datetime import datetime

import pytest

from nikola.domain.entities.message import Message
from nikola.domain.errors import MessageValidationError
from nikola.domain.value_objects.conversation_id import ConversationId
from nikola.domain.value_objects.enums import MessageRole
from nikola.domain.value_objects.message_id import MessageId


def _cid() -> ConversationId:
    return ConversationId.generate()


@pytest.mark.unit
class TestMessageCreate:
    def test_create_generates_a_message_id(self) -> None:
        msg = Message.create(conversation_id=_cid(), role=MessageRole.USER, content="hi")
        assert isinstance(msg.id, MessageId)

    def test_create_preserves_given_fields(self) -> None:
        cid = _cid()
        msg = Message.create(conversation_id=cid, role=MessageRole.ASSISTANT, content="reply")
        assert msg.conversation_id == cid
        assert msg.role is MessageRole.ASSISTANT
        assert msg.content == "reply"

    def test_create_sets_created_at(self) -> None:
        msg = Message.create(conversation_id=_cid(), role=MessageRole.USER, content="hi")
        assert isinstance(msg.created_at, datetime)

    def test_two_messages_have_different_ids(self) -> None:
        cid = _cid()
        a = Message.create(conversation_id=cid, role=MessageRole.USER, content="a")
        b = Message.create(conversation_id=cid, role=MessageRole.USER, content="b")
        assert a.id != b.id


@pytest.mark.unit
class TestMessageValidation:
    def test_empty_content_is_rejected(self) -> None:
        with pytest.raises(MessageValidationError):
            Message.create(conversation_id=_cid(), role=MessageRole.USER, content="")

    def test_whitespace_only_content_is_rejected(self) -> None:
        with pytest.raises(MessageValidationError):
            Message.create(conversation_id=_cid(), role=MessageRole.USER, content="   ")

    def test_direct_construction_also_validates(self) -> None:
        with pytest.raises(MessageValidationError):
            Message(
                id=MessageId.generate(),
                conversation_id=_cid(),
                role=MessageRole.USER,
                content="",
            )


@pytest.mark.unit
class TestMessageImmutability:
    def test_content_cannot_be_reassigned(self) -> None:
        msg = Message.create(conversation_id=_cid(), role=MessageRole.USER, content="hi")
        with pytest.raises(AttributeError):
            msg.content = "mutated"  # type: ignore[misc]

    def test_all_four_roles_are_accepted(self) -> None:
        cid = _cid()
        for role in MessageRole:
            msg = Message.create(conversation_id=cid, role=role, content="content")
            assert msg.role is role
