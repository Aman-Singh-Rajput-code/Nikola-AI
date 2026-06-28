"""Shared fixtures for the logging test suite.

Python's `logging` module is global, mutable, process-wide state: the
logger registry, and any handlers attached to a given logger, persist
across tests unless explicitly cleaned up. Without isolation, one test's
`setup_logging()` call could leave handlers attached that bleed into the
next test (causing duplicate output, unexpected handler counts, or a
stale level), or vice versa. The fixture below resets the "nikola" root
logger to a known-empty state both before and after every test in this
directory tree.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator

#: Mirrors the private constant in logging_service.py. Duplicated here
#: (rather than imported) so this fixture has no dependency on the
#: module under test's internals beyond the well-known root logger name.
NIKOLA_ROOT_LOGGER_NAME = "nikola"


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


def _clear_handlers(logger: logging.Logger) -> None:
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
