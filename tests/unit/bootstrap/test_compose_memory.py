"""Integration tests for memory layer wiring in `compose()`."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest

from nikola.application.memory import (
    ImportanceRetrievalStrategy,
    MemoryManager,
    MemoryService,
)
from nikola.bootstrap.compose import compose
from nikola.domain.entities.memory_query import MemoryQuery
from nikola.domain.ports import MemoryRepositoryPort
from nikola.domain.value_objects.enums import MemoryType

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
class TestMemoryServicesRegistered:
    def test_memory_repository_port_is_registered(self, isolated_cwd: object) -> None:
        container = compose()
        assert container.is_registered(MemoryRepositoryPort)

    def test_memory_service_is_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(MemoryService)

    def test_memory_manager_is_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(MemoryManager)

    def test_importance_strategy_is_registered(self, isolated_cwd: object) -> None:
        assert compose().is_registered(ImportanceRetrievalStrategy)

    def test_all_memory_services_are_singletons(self, isolated_cwd: object) -> None:
        container = compose()
        assert container.resolve(MemoryService) is container.resolve(MemoryService)
        assert container.resolve(MemoryManager) is container.resolve(MemoryManager)

    def test_full_memory_flow_via_container(self, isolated_cwd: object) -> None:
        container = compose()
        mgr = container.resolve(MemoryManager)

        mgr.remember_fact("User's name is Aman", tags=frozenset({"user"}))
        mgr.note_procedure("User prefers Docker")
        mgr.record_episode("Deployed Sprint 8 successfully")

        result = mgr.recall(MemoryQuery())
        assert result.total_found == 3

        semantic = mgr.recall(MemoryQuery(memory_types=frozenset({MemoryType.SEMANTIC})))
        assert len(semantic.entries) == 1
        assert semantic.entries[0].content == "User's name is Aman"

        # Procedural has default importance 0.7 > semantic 0.6 > episodic 0.5
        assert result.entries[0].memory_type is MemoryType.PROCEDURAL
