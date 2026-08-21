"""`ToolRegistryPort` — the abstract domain port for the Tool Registry.

Defined in the domain layer so that application use cases depend only on
this interface, never on a specific registry implementation. The
`InMemoryToolRegistry` in `nikola.infrastructure.tool_registry` is
Sprint 11's sole implementation.

The registry manages tools — it does not execute them. There is
intentionally no `execute()` method on this port.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.entities.tool import Tool
    from nikola.domain.value_objects.tool_id import ToolId

__all__ = ["ToolRegistryPort"]


class ToolRegistryPort(ABC):
    """Abstract interface for the Tool Registry.

    The registry is responsible for managing tool registrations —
    storing, retrieving, listing, and removing `Tool` entities.

    It is NOT responsible for executing tools. There is no `execute()`
    method. Execution is the StepExecutorPort's responsibility.
    """

    @abstractmethod
    def register(self, tool: Tool) -> None:
        """Register `tool` in the registry.

        Args:
            tool: The tool to register. Its `id` is used as the registry key.

        Raises:
            ToolAlreadyRegisteredError: If a tool with the same `ToolId`
                is already registered. The registry does not silently
                overwrite existing tools.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, tool_id: ToolId) -> Tool:
        """Return the registered tool with `tool_id`.

        Args:
            tool_id: The identifier of the tool to retrieve.

        Returns:
            The matching registered `Tool`.

        Raises:
            ToolNotFoundError: If no tool with `tool_id` is registered.
        """
        raise NotImplementedError

    @abstractmethod
    def contains(self, tool_id: ToolId) -> bool:
        """Return whether a tool with `tool_id` is registered.

        Does not raise if the tool is absent — use `get()` when you need
        the tool itself and want an error on absence.

        Args:
            tool_id: The identifier to check.

        Returns:
            ``True`` if the tool is registered; ``False`` otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def list_tools(self) -> tuple[Tool, ...]:
        """Return all currently registered tools as an immutable tuple.

        The returned tuple is a snapshot — callers cannot corrupt the
        internal registry state through the returned collection.

        Returns:
            A tuple of all registered `Tool` objects. Empty if no tools
            are registered. Order is not guaranteed.
        """
        raise NotImplementedError

    @abstractmethod
    def unregister(self, tool_id: ToolId) -> None:
        """Remove the tool with `tool_id` from the registry.

        Args:
            tool_id: The identifier of the tool to remove.

        Raises:
            ToolNotFoundError: If no tool with `tool_id` is registered.
                Use `contains()` first to check existence if needed.
        """
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Return the number of tools currently registered."""
        raise NotImplementedError
