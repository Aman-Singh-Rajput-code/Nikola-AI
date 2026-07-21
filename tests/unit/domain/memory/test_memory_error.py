"""Unit tests for `MemoryError` in the domain error hierarchy."""

from __future__ import annotations

import builtins

import pytest

from nikola.domain.errors import MemoryError, NikolaError

_BUILTIN_MEMORY_ERROR = builtins.MemoryError


@pytest.mark.unit
class TestMemoryErrorHierarchy:
    def test_memory_error_is_a_nikola_error(self) -> None:
        assert issubclass(MemoryError, NikolaError)

    def test_memory_error_is_catchable_as_nikola_error(self) -> None:
        with pytest.raises(NikolaError):
            raise MemoryError("entry not found")

    def test_memory_error_carries_its_message(self) -> None:
        err = MemoryError("importance out of range")
        assert "importance out of range" in str(err)

    def test_memory_error_is_not_the_builtin_memory_error(self) -> None:
        """Confirm our MemoryError is distinct from Python's built-in MemoryError."""
        assert not issubclass(MemoryError, _BUILTIN_MEMORY_ERROR)
