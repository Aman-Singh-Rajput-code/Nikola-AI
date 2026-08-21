"""`ToolRegistryManager` — high-level facade for Tool Registry operations.

Follows the same conventions as `MemoryManager`, `PlanningManager`, and
`ExecutionManager`: provides the expressive API that future Orchestrator
and Agent sprints will use, delegating all mechanics to the service.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.application.tool_registry.tool_registry_service import (
    ToolRegistryService,  # noqa: TC001
)

if TYPE_CHECKING:
    from nikola.domain.entities.tool import Tool
    from nikola.domain.value_objects.tool_id import ToolId

__all__ = ["ToolRegistryManager"]


class ToolRegistryManager:
    """High-level Tool Registry API for Orchestrator and Agent use.

    Delegates all operations to `ToolRegistryService`. Provides the
    stable, expressive interface that callers depend on.
    """

    def __init__(self, service: ToolRegistryService) -> None:
        self._service = service

    def register(self, tool: Tool) -> None:
        """Register `tool` in the Tool Registry.

        Args:
            tool: The tool to register.

        Raises:
            ToolAlreadyRegisteredError: If a tool with the same id is
                already registered.
        """
        self._service.register(tool)

    def get(self, tool_id: ToolId) -> Tool:
        """Return the registered tool with `tool_id`.

        Args:
            tool_id: The tool identifier.

        Returns:
            The matching registered `Tool`.

        Raises:
            ToolNotFoundError: If no tool with `tool_id` is registered.
        """
        return self._service.get(tool_id)

    def contains(self, tool_id: ToolId) -> bool:
        """Return whether a tool with `tool_id` is registered.

        Args:
            tool_id: The identifier to check.

        Returns:
            ``True`` if registered; ``False`` otherwise.
        """
        return self._service.contains(tool_id)

    def list_tools(self) -> tuple[Tool, ...]:
        """Return all currently registered tools as an immutable tuple."""
        return self._service.list_tools()

    def unregister(self, tool_id: ToolId) -> None:
        """Remove the tool with `tool_id`.

        Args:
            tool_id: The identifier of the tool to remove.

        Raises:
            ToolNotFoundError: If no tool with `tool_id` is registered.
        """
        self._service.unregister(tool_id)

    def count(self) -> int:
        """Return the number of currently registered tools."""
        return self._service.count()
