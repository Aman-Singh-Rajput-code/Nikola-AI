"""Unit tests for ToolRegistryService."""

from __future__ import annotations

import pytest

from nikola.application.tool_registry.tool_registry_service import ToolRegistryService
from nikola.domain.entities.tool import Tool
from nikola.domain.errors import ToolAlreadyRegisteredError, ToolNotFoundError
from nikola.domain.value_objects.tool_id import ToolId
from nikola.infrastructure.tool_registry import InMemoryToolRegistry


def _svc() -> ToolRegistryService:
    return ToolRegistryService(registry=InMemoryToolRegistry())


def _tool(name: str = "test.tool") -> Tool:
    return Tool.create(ToolId(value=name), description="desc")


@pytest.mark.unit
class TestToolRegistryServiceRegister:
    def test_register_then_contains(self) -> None:
        svc = _svc()
        tool = _tool()
        svc.register(tool)
        assert svc.contains(tool.id) is True

    def test_register_duplicate_raises(self) -> None:
        svc = _svc()
        tool = _tool()
        svc.register(tool)
        with pytest.raises(ToolAlreadyRegisteredError):
            svc.register(tool)


@pytest.mark.unit
class TestToolRegistryServiceGet:
    def test_get_registered_tool(self) -> None:
        svc = _svc()
        tool = _tool()
        svc.register(tool)
        assert svc.get(tool.id) == tool

    def test_get_missing_raises(self) -> None:
        svc = _svc()
        with pytest.raises(ToolNotFoundError):
            svc.get(ToolId(value="no.such"))


@pytest.mark.unit
class TestToolRegistryServiceContains:
    def test_contains_existing(self) -> None:
        svc = _svc()
        tool = _tool()
        svc.register(tool)
        assert svc.contains(tool.id) is True

    def test_contains_missing_returns_false(self) -> None:
        assert _svc().contains(ToolId(value="absent")) is False


@pytest.mark.unit
class TestToolRegistryServiceListTools:
    def test_list_returns_registered_tools(self) -> None:
        svc = _svc()
        t1, t2 = _tool("a.b"), _tool("c.d")
        svc.register(t1)
        svc.register(t2)
        listed = svc.list_tools()
        assert t1 in listed and t2 in listed

    def test_list_empty_registry(self) -> None:
        assert _svc().list_tools() == ()


@pytest.mark.unit
class TestToolRegistryServiceUnregister:
    def test_unregister_removes_tool(self) -> None:
        svc = _svc()
        tool = _tool()
        svc.register(tool)
        svc.unregister(tool.id)
        assert svc.contains(tool.id) is False

    def test_unregister_missing_raises(self) -> None:
        svc = _svc()
        with pytest.raises(ToolNotFoundError):
            svc.unregister(ToolId(value="absent"))


@pytest.mark.unit
class TestToolRegistryServiceCount:
    def test_count_after_operations(self) -> None:
        svc = _svc()
        assert svc.count() == 0
        svc.register(_tool("a.b"))
        assert svc.count() == 1
        svc.register(_tool("c.d"))
        assert svc.count() == 2
        svc.unregister(ToolId(value="a.b"))
        assert svc.count() == 1
