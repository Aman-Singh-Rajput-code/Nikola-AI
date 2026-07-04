"""Integration tests for `BrainPort` wiring in the composition root."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest

from nikola.bootstrap.compose import compose
from nikola.domain.ports import BrainPort
from nikola.infrastructure.brains.null_brain import NullBrain

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


# Reuse the same isolation fixtures pattern from bootstrap/conftest.py
@pytest.fixture(autouse=True)
def _isolated_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    for key in list(os.environ.keys()):
        if key.startswith("NIKOLA_"):
            monkeypatch.delenv(key, raising=False)
    yield


@pytest.fixture(autouse=True)
def _isolated_nikola_logger() -> Iterator[None]:
    root_logger = logging.getLogger("nikola")
    original_level = root_logger.level
    original_propagate = root_logger.propagate
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()
    yield
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()
    root_logger.setLevel(original_level)
    root_logger.propagate = original_propagate


@pytest.fixture
def isolated_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _resolve_brain(container: object) -> BrainPort:
    from nikola.bootstrap.container import ServiceContainer

    assert isinstance(container, ServiceContainer)
    return container.resolve(BrainPort)  # type: ignore[type-abstract]


@pytest.mark.unit
class TestBrainPortRegisteredInCompose:
    def test_brain_port_is_registered(self, isolated_cwd: object) -> None:
        from nikola.bootstrap.container import ServiceContainer

        container = compose()
        assert isinstance(container, ServiceContainer)
        assert container.is_registered(BrainPort)

    def test_default_provider_resolves_to_null_brain(self, isolated_cwd: object) -> None:
        container = compose()
        brain = _resolve_brain(container)
        assert isinstance(brain, NullBrain)

    def test_brain_port_is_a_singleton(self, isolated_cwd: object) -> None:
        container = compose()
        first = _resolve_brain(container)
        second = _resolve_brain(container)
        assert first is second

    def test_resolved_brain_can_process_a_reasoning_request(self, isolated_cwd: object) -> None:
        from nikola.domain.entities.reasoning_request import ReasoningRequest

        container = compose()
        brain = _resolve_brain(container)
        resp = brain.reason(ReasoningRequest(content="hello from integration test"))
        assert resp.model_used == "null"
        assert "hello from integration test" in resp.content
