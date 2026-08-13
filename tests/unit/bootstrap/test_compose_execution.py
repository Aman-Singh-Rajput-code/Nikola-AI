"""Integration tests for execution layer wiring in compose()."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest

from nikola.application.execution import ExecutionEngine, ExecutionManager, ExecutionService
from nikola.bootstrap.compose import compose
from nikola.domain.entities.plan import Plan
from nikola.domain.entities.plan_step import PlanStep
from nikola.domain.ports import StepExecutorPort
from nikola.domain.value_objects.enums import ExecutionStatus, StepType

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@pytest.fixture(autouse=True)
def _isolated_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    for key in list(os.environ.keys()):
        if key.startswith("NIKOLA_"):
            monkeypatch.delenv(key, raising=False)
    yield


@pytest.fixture(autouse=True)
def _isolated_nikola_logger() -> Iterator[None]:
    root = logging.getLogger("nikola")
    level, propagate = root.level, root.propagate
    for h in list(root.handlers):
        root.removeHandler(h)
        h.close()
    yield
    for h in list(root.handlers):
        root.removeHandler(h)
        h.close()
    root.setLevel(level)
    root.propagate = propagate


@pytest.fixture
def isolated_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _simple_plan() -> Plan:
    p = Plan.create(goal="integration test plan")
    p.add_step(
        PlanStep.create(title="step one", description="d", order=1, step_type=StepType.GENERIC)
    )
    p.add_step(PlanStep.create(title="step two", description="d", order=2, step_type=StepType.CODE))
    return p


@pytest.mark.unit
class TestExecutionServicesRegistered:
    def test_step_executor_port_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(StepExecutorPort)

    def test_execution_engine_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(ExecutionEngine)

    def test_execution_service_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(ExecutionService)

    def test_execution_manager_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(ExecutionManager)

    def test_all_are_singletons(self, isolated_cwd: object) -> None:
        container = compose()
        assert container.resolve(ExecutionEngine) is container.resolve(ExecutionEngine)
        assert container.resolve(ExecutionService) is container.resolve(ExecutionService)
        assert container.resolve(ExecutionManager) is container.resolve(ExecutionManager)

    def test_full_execution_flow_via_container(self, isolated_cwd: object) -> None:
        container = compose()
        mgr = container.resolve(ExecutionManager)
        result = mgr.execute_plan(_simple_plan())
        assert result.final_status is ExecutionStatus.COMPLETED
        assert len(result.completed_steps) == 2
        assert result.execution.started_at is not None
        assert result.execution.completed_at is not None

    def test_executor_name_is_deterministic(self, isolated_cwd: object) -> None:
        mgr = compose().resolve(ExecutionManager)
        assert mgr.executor_name == "deterministic"
