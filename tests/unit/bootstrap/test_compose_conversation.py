"""Integration tests for conversation layer wiring in `compose()`."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest

from nikola.application.conversation import ConversationManager, ConversationService
from nikola.bootstrap.compose import compose
from nikola.domain.ports import ConversationRepositoryPort

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
class TestConversationServicesRegistered:
    def test_conversation_repository_port_is_registered(self, isolated_cwd: object) -> None:
        container = compose()
        assert container.is_registered(ConversationRepositoryPort)

    def test_conversation_service_is_registered(self, isolated_cwd: object) -> None:
        container = compose()
        assert container.is_registered(ConversationService)

    def test_conversation_manager_is_registered(self, isolated_cwd: object) -> None:
        container = compose()
        assert container.is_registered(ConversationManager)

    def test_all_three_are_singletons(self, isolated_cwd: object) -> None:
        container = compose()
        assert container.resolve(ConversationService) is container.resolve(ConversationService)
        assert container.resolve(ConversationManager) is container.resolve(ConversationManager)

    def test_full_conversation_flow_via_container(self, isolated_cwd: object) -> None:
        from nikola.domain.value_objects.session_id import SessionId

        container = compose()
        mgr = container.resolve(ConversationManager)
        sid = SessionId.generate()

        conv = mgr.get_or_create_active_conversation(sid)
        mgr.add_user_message(conv.id, "hello from integration test")
        mgr.add_assistant_message(conv.id, "hello back")

        history = mgr.get_brain_context(conv.id)
        assert len(history) == 2
        assert history[0].content == "hello from integration test"
