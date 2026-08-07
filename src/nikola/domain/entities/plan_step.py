"""`PlanStep` — one atomic unit of work within a `Plan`."""

from __future__ import annotations

from dataclasses import dataclass, field

from nikola.domain.value_objects.enums import StepStatus, StepType
from nikola.domain.value_objects.step_id import StepId

__all__ = ["PlanStep"]


@dataclass(slots=True)
class PlanStep:
    """One atomic unit of work within a Plan.

    Attributes:
        id: Unique identifier.
        title: Short human-readable label.
        description: Fuller explanation of what this step does and why.
        order: Execution position (1-based ascending).
        step_type: Category of action for the future execution engine.
        status: Lifecycle state. Always PENDING at creation time.
        dependencies: StepIds that must complete before this step starts.
        estimated_duration_seconds: Optional time estimate in seconds.
        metadata: Arbitrary key-value extensibility dict.
    """

    id: StepId
    title: str
    description: str
    order: int
    step_type: StepType
    status: StepStatus = field(default=StepStatus.PENDING)
    dependencies: tuple[StepId, ...] = field(default_factory=tuple)
    estimated_duration_seconds: int | None = field(default=None)
    metadata: dict[str, object] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        title: str,
        description: str,
        order: int,
        step_type: StepType = StepType.GENERIC,
        dependencies: tuple[StepId, ...] | None = None,
        estimated_duration_seconds: int | None = None,
        metadata: dict[str, object] | None = None,
    ) -> PlanStep:
        """Construct a new PENDING PlanStep with a generated StepId."""
        return cls(
            id=StepId.generate(),
            title=title,
            description=description,
            order=order,
            step_type=step_type,
            dependencies=dependencies or (),
            estimated_duration_seconds=estimated_duration_seconds,
            metadata=metadata or {},
        )
