"""`ToolId` — an immutable, validated identifier for a registered `Tool`.

Unlike most other IDs in Nikola AI (which wrap auto-generated UUIDs),
`ToolId` wraps a human-readable name string chosen by whoever registers
the tool (e.g. ``"filesystem.read_file"``, ``"terminal.execute"``,
``"browser.navigate"``). This makes tool names meaningful in logs, plans,
and reasoning responses without requiring a separate lookup.

The same validation rule applies: an empty `ToolId` is not permitted.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["ToolId"]


@dataclass(frozen=True, slots=True)
class ToolId:
    """A validated, immutable identifier for a `Tool`.

    Wraps a human-readable name string rather than a UUID, so tool names
    are meaningful in `PlanStep.metadata`, `ReasoningResponse.tool_name`,
    and execution logs.

    Conventions:
    - Use dot-notation for namespacing: ``"filesystem.read_file"``.
    - Use lowercase with underscores: ``"terminal.execute_command"``.
    - Names must be non-empty.

    Use the constructor directly to create a `ToolId` from a known name.
    There is no `generate()` classmethod — tool names are chosen by the
    registrant, not randomly generated.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("ToolId value must not be empty or whitespace-only.")

    def __str__(self) -> str:
        return self.value
