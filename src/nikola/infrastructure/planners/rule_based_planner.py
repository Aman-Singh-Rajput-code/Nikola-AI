"""`RuleBasedPlanner` — deterministic keyword-driven `PlannerPort`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nikola.domain.entities.plan import Plan
from nikola.domain.entities.plan_step import PlanStep
from nikola.domain.entities.planning_request import PlanningResult
from nikola.domain.ports.planner_port import PlannerPort
from nikola.domain.value_objects.enums import StepType

if TYPE_CHECKING:
    from nikola.domain.entities.planning_request import PlanningRequest

__all__ = ["RuleBasedPlanner"]

_S = dict[str, Any]

_RULES: list[tuple[str, list[_S]]] = [
    (
        "python",
        [
            _S(
                title="Set up Python virtual environment",
                description="Create an isolated Python virtual environment using `python -m venv .venv`.",
                step_type=StepType.SHELL,
                estimated_duration_seconds=30,
                metadata={"command": "python -m venv .venv"},
            ),
            _S(
                title="Install project dependencies",
                description="Install required packages from requirements.txt or pyproject.toml.",
                step_type=StepType.SHELL,
                estimated_duration_seconds=60,
                metadata={"command": "pip install -e .[dev]"},
            ),
        ],
    ),
    (
        "flask",
        [
            _S(
                title="Install Flask",
                description="Install Flask and its dependencies into the active environment.",
                step_type=StepType.SHELL,
                estimated_duration_seconds=30,
                metadata={"command": "pip install flask"},
            ),
            _S(
                title="Create Flask application skeleton",
                description="Create app.py with a minimal Flask application factory.",
                step_type=StepType.CODE,
                estimated_duration_seconds=120,
                metadata={"filename": "app.py"},
            ),
        ],
    ),
    (
        "git",
        [
            _S(
                title="Initialize Git repository",
                description="Run `git init` to create a new local repository.",
                step_type=StepType.SHELL,
                estimated_duration_seconds=10,
                metadata={"command": "git init"},
            ),
            _S(
                title="Create .gitignore",
                description="Add a .gitignore file with sensible defaults for Python projects.",
                step_type=StepType.FILE,
                estimated_duration_seconds=15,
                metadata={"filename": ".gitignore"},
            ),
            _S(
                title="Make initial commit",
                description="Stage all files and create the first commit.",
                step_type=StepType.SHELL,
                estimated_duration_seconds=20,
                metadata={"command": "git add -A && git commit -m 'Initial commit'"},
            ),
        ],
    ),
    (
        "test",
        [
            _S(
                title="Set up test suite",
                description="Create tests/ directory, configure pytest, and write a smoke test.",
                step_type=StepType.CODE,
                estimated_duration_seconds=90,
                metadata={"tool": "pytest"},
            ),
        ],
    ),
    (
        "pytest",
        [
            _S(
                title="Set up test suite",
                description="Create tests/ directory, configure pytest, and write a smoke test.",
                step_type=StepType.CODE,
                estimated_duration_seconds=90,
                metadata={"tool": "pytest"},
            ),
        ],
    ),
    (
        "docker",
        [
            _S(
                title="Create Dockerfile",
                description="Write a multi-stage Dockerfile for the project.",
                step_type=StepType.FILE,
                estimated_duration_seconds=120,
                metadata={"filename": "Dockerfile"},
            ),
            _S(
                title="Create docker-compose.yml",
                description="Define services in docker-compose.yml for local development.",
                step_type=StepType.FILE,
                estimated_duration_seconds=60,
                metadata={"filename": "docker-compose.yml"},
            ),
        ],
    ),
    (
        "deploy",
        [
            _S(
                title="Prepare deployment configuration",
                description="Create deployment configuration files (e.g. Procfile, app.yaml).",
                step_type=StepType.FILE,
                estimated_duration_seconds=60,
            ),
            _S(
                title="Run deployment",
                description="Execute the deployment command for the target environment.",
                step_type=StepType.SHELL,
                estimated_duration_seconds=180,
            ),
        ],
    ),
    (
        "api",
        [
            _S(
                title="Design API schema",
                description="Define endpoints, request/response formats, and authentication strategy.",
                step_type=StepType.REASONING,
                estimated_duration_seconds=300,
            ),
            _S(
                title="Implement API endpoints",
                description="Write the route handlers, serializers, and validation logic.",
                step_type=StepType.CODE,
                estimated_duration_seconds=600,
            ),
        ],
    ),
]

_GENERIC_STEP = _S(
    title="Analyse and execute goal",
    description="Reason about the goal, identify required actions, and execute them in order.",
    step_type=StepType.REASONING,
    estimated_duration_seconds=None,
)


class RuleBasedPlanner(PlannerPort):
    """Deterministic keyword-driven planner — no AI, no external calls.

    Scans the goal string (case-insensitive) for known keywords and emits
    a fixed, ordered set of PlanStep objects for each match. Steps from
    multiple keyword matches are merged (deduplicated by title) and
    renumbered sequentially. When no keywords match, a single generic
    reasoning step is returned with confidence 0.5.
    """

    @property
    def planner_name(self) -> str:
        return "rule_based"

    def plan(self, request: PlanningRequest) -> PlanningResult:
        """Produce a deterministic plan by matching keywords in the goal.

        Args:
            request: The validated planning input.

        Returns:
            A PlanningResult with ordered steps, confidence, warnings,
            and a reasoning summary listing which rules fired.
        """
        goal_lower = request.goal.lower()
        matched_keywords: list[str] = []
        raw_steps: list[_S] = []
        seen_titles: set[str] = set()

        for keyword, steps in _RULES:
            if keyword in goal_lower:
                matched_keywords.append(keyword)
                for step_dict in steps:
                    title: str = step_dict["title"]
                    if title in seen_titles:
                        continue
                    seen_titles.add(title)
                    raw_steps.append(step_dict)

        plan = Plan.create(goal=request.goal)
        warnings: list[str] = []

        if not raw_steps:
            step = PlanStep.create(
                title=_GENERIC_STEP["title"],
                description=_GENERIC_STEP["description"],
                order=1,
                step_type=_GENERIC_STEP["step_type"],
                estimated_duration_seconds=_GENERIC_STEP.get("estimated_duration_seconds"),
            )
            plan.add_step(step)
            confidence = 0.5
            reasoning = (
                f"No specific keywords recognised in goal: '{request.goal}'. "
                "Falling back to a generic analysis step."
            )
            warnings.append(
                "Goal did not match any known planning rules. "
                "A generic step was generated. Consider refining the goal."
            )
        else:
            for order, step_dict in enumerate(raw_steps, start=1):
                step = PlanStep.create(
                    title=step_dict["title"],
                    description=step_dict["description"],
                    order=order,
                    step_type=step_dict.get("step_type", StepType.GENERIC),
                    estimated_duration_seconds=step_dict.get("estimated_duration_seconds"),
                    metadata=dict(step_dict.get("metadata", {})),
                )
                plan.add_step(step)
            confidence = 1.0
            reasoning = (
                f"Matched keyword(s): {matched_keywords}. "
                f"Generated {len(raw_steps)} step(s) from rule table."
            )
            if request.constraints:
                warnings.append(
                    f"Constraints provided but not enforced by RuleBasedPlanner: "
                    f"{list(request.constraints)}"
                )

        return PlanningResult(
            plan=plan,
            confidence=confidence,
            warnings=tuple(warnings),
            reasoning_summary=reasoning,
        )
