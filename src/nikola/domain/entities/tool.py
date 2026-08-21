"""`Tool` — a domain entity describing a registered capability.

A `Tool` describes *what* a capability is and *how* to identify it. It does
NOT execute the capability — that is the executor's responsibility. This
separation mirrors the Planner/ExecutionEngine split: the registry knows
about tools, the executor knows how to run them.

`Tool` is immutable. Once registered, a tool's identity and description
do not change — to update a tool, unregister it and register a replacement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.domain.value_objects.tool_id import ToolId

__all__ = ["Tool"]


@dataclass(frozen=True, slots=True)
class Tool:
    """An immutable domain entity describing a registered capability.

    A `Tool` holds the minimum information required for Nikola to identify,
    describe, and reason about a capability. It does not contain execution
    logic, parameter schemas, or permission requirements — those concerns
    belong to future sprints.

    Attributes:
        id: The tool's unique identifier. Used as the registry key and
            referenced in `ReasoningResponse.tool_name` and
            `PlanStep.metadata`.
        description: A human-readable description of what the tool does.
            Used by the Brain to understand the tool's purpose when
            building a `ReasoningRequest.available_tools` list.
        version: A version string for the tool implementation (e.g.
            ``"1.0.0"``). Defaults to ``"1.0.0"``. Not used for version
            resolution in Sprint 11 — recorded for future use.
        metadata: Arbitrary key-value pairs for extensibility. May carry
            tool category, author, documentation URL, etc. Not interpreted
            by the registry in Sprint 11.

    Raises:
        ValueError: If `description` is empty or whitespace-only.
    """

    id: ToolId
    description: str
    version: str = field(default="1.0.0")
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Tool.description must not be empty or whitespace-only.")

    @classmethod
    def create(
        cls,
        tool_id: ToolId,
        description: str,
        *,
        version: str = "1.0.0",
        metadata: dict[str, object] | None = None,
    ) -> Tool:
        """Construct a new `Tool`.

        Args:
            tool_id: The tool's unique identifier.
            description: Human-readable description of what the tool does.
            version: Version string. Defaults to ``"1.0.0"``.
            metadata: Optional extensibility key-value pairs.

        Returns:
            An immutable `Tool`.

        Raises:
            ValueError: If `description` is empty.
        """
        return cls(
            id=tool_id,
            description=description,
            version=version,
            metadata=metadata if metadata is not None else {},
        )
