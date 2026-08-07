"""Unit tests for PlanningError in the domain error hierarchy."""

from __future__ import annotations

import pytest

from nikola.domain.errors import NikolaError, PlanningError


@pytest.mark.unit
class TestPlanningError:
    def test_is_a_nikola_error(self) -> None:
        assert issubclass(PlanningError, NikolaError)

    def test_catchable_as_nikola_error(self) -> None:
        with pytest.raises(NikolaError):
            raise PlanningError("plan failed")

    def test_carries_message(self) -> None:
        assert "plan failed" in str(PlanningError("plan failed"))
