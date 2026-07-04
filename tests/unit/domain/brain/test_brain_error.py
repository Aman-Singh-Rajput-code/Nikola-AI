"""Unit tests for `BrainError` in the domain error hierarchy."""

from __future__ import annotations

import pytest

from nikola.domain.errors import BrainError, NikolaError


@pytest.mark.unit
class TestBrainErrorHierarchy:
    def test_brain_error_is_a_nikola_error(self) -> None:
        assert issubclass(BrainError, NikolaError)

    def test_brain_error_is_catchable_as_nikola_error(self) -> None:
        with pytest.raises(NikolaError):
            raise BrainError("provider timed out")

    def test_brain_error_carries_its_message(self) -> None:
        err = BrainError("context window exceeded")
        assert "context window exceeded" in str(err)
