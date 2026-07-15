"""Unit tests for `MessageRole` and `ConversationStatus` enums."""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.enums import ConversationStatus, MessageRole


@pytest.mark.unit
class TestMessageRole:
    def test_has_expected_members(self) -> None:
        assert {m.value for m in MessageRole} == {"user", "assistant", "system", "tool"}

    def test_is_str_subclass(self) -> None:
        assert isinstance(MessageRole.USER, str)

    def test_members_equal_their_string_values(self) -> None:
        assert MessageRole.USER == "user"  # type: ignore[comparison-overlap]
        assert MessageRole.ASSISTANT == "assistant"  # type: ignore[comparison-overlap]


@pytest.mark.unit
class TestConversationStatus:
    def test_has_expected_members(self) -> None:
        assert {m.value for m in ConversationStatus} == {"active", "archived", "deleted"}

    def test_is_str_subclass(self) -> None:
        assert isinstance(ConversationStatus.ACTIVE, str)
