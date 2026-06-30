"""Unit tests for `nikola.domain.value_objects.session_id.SessionId`."""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.session_id import SessionId


@pytest.mark.unit
class TestSessionIdGeneration:
    def test_generate_returns_a_session_id(self) -> None:
        session_id = SessionId.generate()
        assert isinstance(session_id, SessionId)

    def test_generate_produces_unique_values(self) -> None:
        first = SessionId.generate()
        second = SessionId.generate()
        assert first != second
        assert first.value != second.value


@pytest.mark.unit
class TestSessionIdEquality:
    def test_equal_values_are_equal(self) -> None:
        assert SessionId(value="abc-123") == SessionId(value="abc-123")

    def test_different_values_are_not_equal(self) -> None:
        assert SessionId(value="abc-123") != SessionId(value="xyz-789")

    def test_is_hashable_and_usable_in_a_set(self) -> None:
        ids = {SessionId(value="a"), SessionId(value="a"), SessionId(value="b")}
        assert len(ids) == 2


@pytest.mark.unit
class TestSessionIdImmutability:
    def test_value_cannot_be_reassigned(self) -> None:
        session_id = SessionId(value="abc-123")
        with pytest.raises(AttributeError):
            session_id.value = "mutated"  # type: ignore[misc]


@pytest.mark.unit
class TestSessionIdValidation:
    def test_empty_string_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            SessionId(value="")


@pytest.mark.unit
class TestSessionIdStringRepresentation:
    def test_str_returns_the_underlying_value(self) -> None:
        session_id = SessionId(value="abc-123")
        assert str(session_id) == "abc-123"
