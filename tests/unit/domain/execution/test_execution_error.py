"""Unit tests for ExecutionError in the domain error hierarchy."""

from __future__ import annotations

import pytest

from nikola.domain.errors import ExecutionError, NikolaError


@pytest.mark.unit
class TestExecutionError:
    def test_is_nikola_error(self) -> None:
        assert issubclass(ExecutionError, NikolaError)

    def test_catchable_as_nikola_error(self) -> None:
        with pytest.raises(NikolaError):
            raise ExecutionError("execution failed")

    def test_carries_message(self) -> None:
        assert "execution failed" in str(ExecutionError("execution failed"))
