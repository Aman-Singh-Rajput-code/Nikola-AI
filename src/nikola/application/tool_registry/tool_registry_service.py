"""`ToolRegistryService` — primary use-case service for Tool Registry operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.entities.tool import Tool
    from nikola.domain.ports.tool_registry_port import ToolRegistryPort
    from nikola.domain.value_objects.tool_id import ToolId

__all__ = ["ToolRegistryService"]


class ToolRegistryService:
    """Use-case boundary for Tool Registry operations.

    Depends on `ToolRegistryPort` (injected), never on a concrete
    implementation. Provides the application-level interface for
    registering, retrieving, listing, and removing tools.

    Does NOT execute tools. Does NOT integrate with the Execution Engine.
    """

    def __init__(self, registry: ToolRegistryPort) -> None:
        self._registry = registry

    def register(self, tool: Tool) -> None:
        """Register `tool` in the registry.

        Args:
            tool: The tool to register.

        Raises:
            ToolAlreadyRegisteredError: If a tool with the same id exists.
        """
        self._registry.register(tool)

    def get(self, tool_id: ToolId) -> Tool:
        """Return the registered tool with `tool_id`.

        Args:
            tool_id: The tool identifier to look up.

        Returns:
            The matching `Tool`.

        Raises:
            ToolNotFoundError: If no tool with `tool_id` is registered.
        """
        return self._registry.get(tool_id)

    def contains(self, tool_id: ToolId) -> bool:
        """Return whether a tool with `tool_id` is registered.

        Args:
            tool_id: The identifier to check.

        Returns:
            ``True`` if registered; ``False`` otherwise.
        """
        return self._registry.contains(tool_id)

    def list_tools(self) -> tuple[Tool, ...]:
        """Return all registered tools as an immutable tuple."""
        return self._registry.list_tools()

    def unregister(self, tool_id: ToolId) -> None:
        """Remove the tool with `tool_id`.

        Args:
            tool_id: The identifier of the tool to remove.

        Raises:
            ToolNotFoundError: If no tool with `tool_id` is registered.
        """
        self._registry.unregister(tool_id)

    def count(self) -> int:
        """Return the number of currently registered tools."""
        return self._registry.count()
