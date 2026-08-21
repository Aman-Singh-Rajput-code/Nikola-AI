"""Integration tests for Tool Registry wiring in compose()."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest

from nikola.application.tool_registry import ToolRegistryManager, ToolRegistryService
from nikola.bootstrap.compose import compose
from nikola.domain.entities.tool import Tool
from nikola.domain.ports import ToolRegistryPort
from nikola.domain.value_objects.tool_id import ToolId
from nikola.infrastructure.tool_registry import InMemoryToolRegistry

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
class TestToolRegistryServicesRegistered:
    def test_tool_registry_port_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(ToolRegistryPort)

    def test_tool_registry_service_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(ToolRegistryService)

    def test_tool_registry_manager_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(ToolRegistryManager)

    def test_resolved_registry_is_in_memory(self, isolated_cwd: object) -> None:
        container = compose()
        registry = container.resolve(ToolRegistryPort)  # type: ignore[type-abstract]
        assert isinstance(registry, InMemoryToolRegistry)

    def test_all_are_singletons(self, isolated_cwd: object) -> None:
        container = compose()
        assert container.resolve(ToolRegistryService) is container.resolve(ToolRegistryService)
        assert container.resolve(ToolRegistryManager) is container.resolve(ToolRegistryManager)

    def test_full_tool_registry_flow_via_container(self, isolated_cwd: object) -> None:
        container = compose()
        mgr = container.resolve(ToolRegistryManager)
        tool = Tool.create(ToolId(value="test.sprint11"), description="Sprint 11 test tool")
        mgr.register(tool)
        assert mgr.contains(tool.id) is True
        assert mgr.get(tool.id) == tool
        assert mgr.count() == 1
        mgr.unregister(tool.id)
        assert mgr.count() == 0

    def test_execution_engine_remains_unchanged(self, isolated_cwd: object) -> None:
        """Verify the Execution Engine is still wired independently of the Tool Registry."""
        from nikola.application.execution import ExecutionManager

        container = compose()
        exec_mgr = container.resolve(ExecutionManager)
        assert exec_mgr.executor_name == "deterministic"
