"""Shared fixtures for the bootstrap/composition-root test suite.

`compose()` resolves real configuration (environment variables, `.env`,
`config/default.yaml`) and configures real `logging` module state when its
`LoggingInitialized` singleton is resolved. Without isolation, tests here
have the same two leakage risks already addressed in
`tests/unit/config/conftest.py` and `tests/unit/logging/conftest.py`:
stray `NIKOLA_*` environment variables, and stale handlers left on the
"nikola" logger. This file combines both isolation strategies so
`compose()` can be tested end-to-end safely.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

NIKOLA_ROOT_LOGGER_NAME = "nikola"


@pytest.fixture(autouse=True)
def _isolated_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Strip all NIKOLA_*-prefixed environment variables before each test."""
    for key in list(os.environ.keys()):
        if key.startswith("NIKOLA_"):
            monkeypatch.delenv(key, raising=False)
    yield


@pytest.fixture(autouse=True)
def _isolated_nikola_logger() -> Iterator[None]:
    """Reset the "nikola" root logger's handlers and level around each test."""
    root_logger = logging.getLogger(NIKOLA_ROOT_LOGGER_NAME)
    original_level = root_logger.level
    original_propagate = root_logger.propagate

    _clear_handlers(root_logger)

    yield

    _clear_handlers(root_logger)
    root_logger.setLevel(original_level)
    root_logger.propagate = original_propagate


@pytest.fixture
def isolated_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Run a test inside an empty temporary directory.

    Prevents tests from accidentally discovering the real project's
    `config/default.yaml` or `.env` file via relative-path lookups.
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _clear_handlers(logger: logging.Logger) -> None:
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
