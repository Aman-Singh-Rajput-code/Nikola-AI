"""Unit tests for Tool Registry errors in the domain error hierarchy."""

from __future__ import annotations

import pytest

from nikola.domain.errors import (
    NikolaError,
    ToolAlreadyRegisteredError,
    ToolNotFoundError,
    ToolRegistryError,
)


@pytest.mark.unit
class TestToolRegistryErrors:
    def test_tool_registry_error_is_nikola_error(self) -> None:
        assert issubclass(ToolRegistryError, NikolaError)

    def test_tool_not_found_error_is_registry_error(self) -> None:
        assert issubclass(ToolNotFoundError, ToolRegistryError)

    def test_tool_already_registered_error_is_registry_error(self) -> None:
        assert issubclass(ToolAlreadyRegisteredError, ToolRegistryError)

    def test_both_catchable_as_nikola_error(self) -> None:
        for cls in (ToolNotFoundError, ToolAlreadyRegisteredError):
            with pytest.raises(NikolaError):
                raise cls("test")

    def test_carry_messages(self) -> None:
        assert "missing" in str(ToolNotFoundError("missing"))
        assert "duplicate" in str(ToolAlreadyRegisteredError("duplicate"))
