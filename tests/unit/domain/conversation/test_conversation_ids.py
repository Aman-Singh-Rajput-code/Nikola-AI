"""Unit tests for `ConversationId` and `MessageId` value objects."""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.conversation_id import ConversationId
from nikola.domain.value_objects.message_id import MessageId


@pytest.mark.unit
class TestConversationId:
    def test_generate_returns_a_conversation_id(self) -> None:
        assert isinstance(ConversationId.generate(), ConversationId)

    def test_generate_produces_unique_values(self) -> None:
        assert ConversationId.generate() != ConversationId.generate()

    def test_equal_values_are_equal(self) -> None:
        assert ConversationId(value="abc") == ConversationId(value="abc")

    def test_different_values_are_not_equal(self) -> None:
        assert ConversationId(value="abc") != ConversationId(value="xyz")

    def test_is_hashable(self) -> None:
        s = {ConversationId(value="a"), ConversationId(value="a"), ConversationId(value="b")}
        assert len(s) == 2

    def test_empty_value_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            ConversationId(value="")

    def test_str_returns_value(self) -> None:
        assert str(ConversationId(value="abc")) == "abc"

    def test_is_immutable(self) -> None:
        cid = ConversationId(value="abc")
        with pytest.raises(AttributeError):
            cid.value = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestMessageId:
    def test_generate_returns_a_message_id(self) -> None:
        assert isinstance(MessageId.generate(), MessageId)

    def test_generate_produces_unique_values(self) -> None:
        assert MessageId.generate() != MessageId.generate()

    def test_equal_values_are_equal(self) -> None:
        assert MessageId(value="abc") == MessageId(value="abc")

    def test_empty_value_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            MessageId(value="")

    def test_str_returns_value(self) -> None:
        assert str(MessageId(value="abc")) == "abc"

    def test_is_immutable(self) -> None:
        mid = MessageId(value="abc")
        with pytest.raises(AttributeError):
            mid.value = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestConversationIdAndMessageIdAreDistinct:
    def test_same_value_different_types_are_not_equal(self) -> None:
        same = "same-value"
        assert ConversationId(value=same) != MessageId(value=same)  # type: ignore[comparison-overlap]
