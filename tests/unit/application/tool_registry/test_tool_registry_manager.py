"""Unit tests for ToolRegistryManager."""

from __future__ import annotations

import pytest

from nikola.application.tool_registry.tool_registry_manager import ToolRegistryManager
from nikola.application.tool_registry.tool_registry_service import ToolRegistryService
from nikola.domain.entities.tool import Tool
from nikola.domain.errors import ToolAlreadyRegisteredError, ToolNotFoundError
from nikola.domain.value_objects.tool_id import ToolId
from nikola.infrastructure.tool_registry import InMemoryToolRegistry


def _mgr() -> ToolRegistryManager:
    return ToolRegistryManager(service=ToolRegistryService(registry=InMemoryToolRegistry()))


def _tool(name: str = "test.tool") -> Tool:
    return Tool.create(ToolId(value=name), description="desc")


@pytest.mark.unit
class TestToolRegistryManagerDelegates:
    def test_register_and_get(self) -> None:
        mgr = _mgr()
        tool = _tool()
        mgr.register(tool)
        assert mgr.get(tool.id) == tool

    def test_contains_after_register(self) -> None:
        mgr = _mgr()
        tool = _tool()
        mgr.register(tool)
        assert mgr.contains(tool.id) is True

    def test_contains_missing_returns_false(self) -> None:
        assert _mgr().contains(ToolId(value="absent")) is False

    def test_list_tools(self) -> None:
        mgr = _mgr()
        t1, t2 = _tool("a.b"), _tool("c.d")
        mgr.register(t1)
        mgr.register(t2)
        listed = mgr.list_tools()
        assert t1 in listed and t2 in listed

    def test_unregister(self) -> None:
        mgr = _mgr()
        tool = _tool()
        mgr.register(tool)
        mgr.unregister(tool.id)
        assert mgr.contains(tool.id) is False

    def test_count(self) -> None:
        mgr = _mgr()
        assert mgr.count() == 0
        mgr.register(_tool())
        assert mgr.count() == 1


@pytest.mark.unit
class TestToolRegistryManagerErrorPropagation:
    def test_duplicate_registration_raises(self) -> None:
        mgr = _mgr()
        tool = _tool()
        mgr.register(tool)
        with pytest.raises(ToolAlreadyRegisteredError):
            mgr.register(tool)

    def test_get_missing_raises(self) -> None:
        with pytest.raises(ToolNotFoundError):
            _mgr().get(ToolId(value="absent"))

    def test_unregister_missing_raises(self) -> None:
        with pytest.raises(ToolNotFoundError):
            _mgr().unregister(ToolId(value="absent"))
