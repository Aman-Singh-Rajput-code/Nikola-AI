"""`InMemoryToolRegistry` — dict-backed `ToolRegistryPort` implementation.

Sprint 11's sole Tool Registry adapter. All tools are stored in a plain
Python `dict` keyed by `ToolId.value`. Data lives only for the lifetime
of the process — no persistence across restarts.

Thread-unsafe by design, consistent with all other in-memory adapters
in the Nikola codebase (`InMemoryConversationRepository`,
`InMemoryMemoryRepository`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nikola.domain.errors.domain_errors import ToolAlreadyRegisteredError, ToolNotFoundError
from nikola.domain.ports.tool_registry_port import ToolRegistryPort

if TYPE_CHECKING:
    from nikola.domain.entities.tool import Tool
    from nikola.domain.value_objects.tool_id import ToolId

__all__ = ["InMemoryToolRegistry"]


class InMemoryToolRegistry(ToolRegistryPort):
    """In-process, dict-backed Tool Registry.

    Implements all `ToolRegistryPort` operations with deterministic
    behavior and no external dependencies.
    """

    def __init__(self) -> None:
        self._store: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register `tool`. Raises `ToolAlreadyRegisteredError` if id already exists."""
        if tool.id.value in self._store:
            raise ToolAlreadyRegisteredError(
                f"A tool with id '{tool.id}' is already registered. "
                "Unregister it before registering a replacement."
            )
        self._store[tool.id.value] = tool

    def get(self, tool_id: ToolId) -> Tool:
        """Return the tool with `tool_id`. Raises `ToolNotFoundError` if absent."""
        tool = self._store.get(tool_id.value)
        if tool is None:
            raise ToolNotFoundError(
                f"No tool with id '{tool_id}' is registered in the Tool Registry."
            )
        return tool

    def contains(self, tool_id: ToolId) -> bool:
        """Return whether a tool with `tool_id` is registered."""
        return tool_id.value in self._store

    def list_tools(self) -> tuple[Tool, ...]:
        """Return all registered tools as an immutable tuple."""
        return tuple(self._store.values())

    def unregister(self, tool_id: ToolId) -> None:
        """Remove the tool with `tool_id`. Raises `ToolNotFoundError` if absent."""
        if tool_id.value not in self._store:
            raise ToolNotFoundError(
                f"Cannot unregister: no tool with id '{tool_id}' is registered."
            )
        del self._store[tool_id.value]

    def count(self) -> int:
        """Return the number of tools currently registered."""
        return len(self._store)
