"""Unit tests for InMemoryToolRegistry."""

from __future__ import annotations

import pytest

from nikola.domain.entities.tool import Tool
from nikola.domain.errors import ToolAlreadyRegisteredError, ToolNotFoundError
from nikola.domain.ports.tool_registry_port import ToolRegistryPort
from nikola.domain.value_objects.tool_id import ToolId
from nikola.infrastructure.tool_registry import InMemoryToolRegistry


def _tid(name: str = "test.tool") -> ToolId:
    return ToolId(value=name)


def _tool(name: str = "test.tool", description: str = "A test tool") -> Tool:
    return Tool.create(_tid(name), description=description)


@pytest.mark.unit
class TestInMemoryToolRegistryIsAPort:
    def test_is_a_tool_registry_port(self) -> None:
        assert isinstance(InMemoryToolRegistry(), ToolRegistryPort)


@pytest.mark.unit
class TestInMemoryToolRegistryEmpty:
    def test_empty_registry_count_is_zero(self) -> None:
        assert InMemoryToolRegistry().count() == 0

    def test_empty_registry_list_tools_returns_empty_tuple(self) -> None:
        assert InMemoryToolRegistry().list_tools() == ()

    def test_empty_registry_contains_returns_false(self) -> None:
        assert InMemoryToolRegistry().contains(_tid()) is False


@pytest.mark.unit
class TestInMemoryToolRegistryRegister:
    def test_register_increases_count(self) -> None:
        reg = InMemoryToolRegistry()
        reg.register(_tool())
        assert reg.count() == 1

    def test_register_and_get_round_trips(self) -> None:
        reg = InMemoryToolRegistry()
        tool = _tool()
        reg.register(tool)
        assert reg.get(tool.id) == tool

    def test_register_makes_contains_true(self) -> None:
        reg = InMemoryToolRegistry()
        tool = _tool()
        reg.register(tool)
        assert reg.contains(tool.id) is True

    def test_register_multiple_tools(self) -> None:
        reg = InMemoryToolRegistry()
        reg.register(_tool("a.tool"))
        reg.register(_tool("b.tool"))
        assert reg.count() == 2

    def test_duplicate_registration_raises(self) -> None:
        reg = InMemoryToolRegistry()
        tool = _tool()
        reg.register(tool)
        with pytest.raises(ToolAlreadyRegisteredError):
            reg.register(tool)

    def test_duplicate_registration_does_not_overwrite(self) -> None:
        reg = InMemoryToolRegistry()
        original = Tool.create(_tid(), description="original")
        duplicate = Tool.create(_tid(), description="replacement")
        reg.register(original)
        with pytest.raises(ToolAlreadyRegisteredError):
            reg.register(duplicate)
        assert reg.get(_tid()).description == "original"


@pytest.mark.unit
class TestInMemoryToolRegistryGet:
    def test_get_registered_tool(self) -> None:
        reg = InMemoryToolRegistry()
        tool = _tool()
        reg.register(tool)
        assert reg.get(tool.id) is tool

    def test_get_missing_tool_raises(self) -> None:
        reg = InMemoryToolRegistry()
        with pytest.raises(ToolNotFoundError):
            reg.get(_tid("missing.tool"))

    def test_get_error_message_mentions_tool_id(self) -> None:
        reg = InMemoryToolRegistry()
        with pytest.raises(ToolNotFoundError, match="no.such"):
            reg.get(_tid("no.such"))


@pytest.mark.unit
class TestInMemoryToolRegistryContains:
    def test_contains_existing_tool_returns_true(self) -> None:
        reg = InMemoryToolRegistry()
        tool = _tool()
        reg.register(tool)
        assert reg.contains(tool.id) is True

    def test_contains_missing_tool_returns_false(self) -> None:
        reg = InMemoryToolRegistry()
        assert reg.contains(_tid("missing")) is False

    def test_contains_does_not_raise_for_missing(self) -> None:
        reg = InMemoryToolRegistry()
        reg.contains(_tid("absent"))  # must not raise


@pytest.mark.unit
class TestInMemoryToolRegistryListTools:
    def test_list_returns_all_registered_tools(self) -> None:
        reg = InMemoryToolRegistry()
        t1, t2 = _tool("a.tool"), _tool("b.tool")
        reg.register(t1)
        reg.register(t2)
        listed = reg.list_tools()
        assert t1 in listed and t2 in listed

    def test_list_returns_immutable_tuple(self) -> None:
        reg = InMemoryToolRegistry()
        reg.register(_tool())
        result = reg.list_tools()
        assert isinstance(result, tuple)

    def test_list_does_not_expose_internal_state(self) -> None:
        reg = InMemoryToolRegistry()
        reg.register(_tool("a.tool"))
        snapshot = reg.list_tools()
        # Cannot corrupt the registry through the snapshot
        assert len(snapshot) == 1
        assert reg.count() == 1


@pytest.mark.unit
class TestInMemoryToolRegistryUnregister:
    def test_unregister_removes_tool(self) -> None:
        reg = InMemoryToolRegistry()
        tool = _tool()
        reg.register(tool)
        reg.unregister(tool.id)
        assert reg.contains(tool.id) is False

    def test_unregister_decreases_count(self) -> None:
        reg = InMemoryToolRegistry()
        tool = _tool()
        reg.register(tool)
        reg.unregister(tool.id)
        assert reg.count() == 0

    def test_unregister_missing_tool_raises(self) -> None:
        reg = InMemoryToolRegistry()
        with pytest.raises(ToolNotFoundError):
            reg.unregister(_tid("absent"))

    def test_unregister_then_reregister_succeeds(self) -> None:
        reg = InMemoryToolRegistry()
        tool = _tool()
        reg.register(tool)
        reg.unregister(tool.id)
        reg.register(tool)  # must not raise
        assert reg.count() == 1


@pytest.mark.unit
class TestInMemoryToolRegistryIsolation:
    def test_two_registries_are_independent(self) -> None:
        r1, r2 = InMemoryToolRegistry(), InMemoryToolRegistry()
        r1.register(_tool())
        assert r2.count() == 0
