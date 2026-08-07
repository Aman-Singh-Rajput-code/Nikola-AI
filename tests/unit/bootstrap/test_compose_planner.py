"""Integration tests for planner layer wiring in compose()."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest

from nikola.application.planner import PlanningManager, PlanningService
from nikola.bootstrap.compose import compose
from nikola.domain.ports import PlannerPort

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


@pytest.mark.unit
class TestPlannerServicesRegistered:
    def test_planner_port_is_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(PlannerPort)

    def test_planning_service_is_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(PlanningService)

    def test_planning_manager_is_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(PlanningManager)

    def test_all_planner_services_are_singletons(self, isolated_cwd: object) -> None:
        container = compose()
        assert container.resolve(PlanningService) is container.resolve(PlanningService)
        assert container.resolve(PlanningManager) is container.resolve(PlanningManager)

    def test_full_planning_flow_via_container(self, isolated_cwd: object) -> None:
        container = compose()
        mgr = container.resolve(PlanningManager)
        result = mgr.plan_goal_simple("create a python flask api with git and tests")
        assert result.plan.step_count > 0
        assert result.confidence == 1.0
        assert result.plan.goal == "create a python flask api with git and tests"

    def test_default_planner_is_rule_based(self, isolated_cwd: object) -> None:
        container = compose()
        mgr = container.resolve(PlanningManager)
        assert mgr.active_planner_name == "rule_based"
