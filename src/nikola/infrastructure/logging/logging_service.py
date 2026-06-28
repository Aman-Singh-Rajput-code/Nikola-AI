"""Centralized logging service.

This module is the one and only place in Nikola AI that configures Python's
stdlib `logging` machinery — handlers, formatters, and levels. Every other
module obtains a logger by calling `get_logger(__name__)` and never touches
`logging.basicConfig()`, `addHandler()`, or a formatter directly. This
centralization is what Sprint 3 requirement #5 ("every module must obtain
loggers through a centralized logging service") means concretely.

Usage
-----
Once, at application startup (a future bootstrap/composition-root sprint
will be the actual caller):

    from nikola.infrastructure.config import EnvConfigProvider
    from nikola.infrastructure.logging import setup_logging

    settings = EnvConfigProvider().get_settings()
    setup_logging(settings.logging)

Everywhere else, in any module that wants to log something:

    from nikola.infrastructure.logging import get_logger

    logger = get_logger(__name__)
    logger.info("Something happened")

Design notes
------------
- All of Nikola AI's loggers live under a single root logger named
  "nikola" (`_ROOT_LOGGER_NAME`). `get_logger(name)` always returns a
  logger that is a descendant of (or equal to) that root, regardless of
  what `name` is passed — this guarantees that the level and handlers
  configured once on the root apply to every module-specific logger via
  Python's normal logger-hierarchy propagation, with no per-module setup
  required.
- `setup_logging()` is idempotent: calling it more than once (e.g. once
  in a test, once for real) clears any handlers it previously attached
  before adding new ones, rather than accumulating duplicate handlers
  that would each emit the same line — a classic stdlib-logging footgun.
- Handler/formatter construction is delegated to `formatters.py`
  (`build_formatter`), so adding new formatting strategies later does not
  require changes here.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

from nikola.infrastructure.logging.formatters import build_formatter

if TYPE_CHECKING:
    from nikola.infrastructure.config.settings import LoggingSettings

__all__ = ["setup_logging", "get_logger"]

#: All Nikola AI loggers are descendants of this single root logger name.
_ROOT_LOGGER_NAME = "nikola"


def setup_logging(settings: LoggingSettings) -> None:
    """Configure console/file handlers, formatter, and level for Nikola AI.

    Must be called once at application startup, before any meaningful
    logging is expected to occur, with the `logging` section of the
    already-validated `NikolaSettings` (see Sprint 2's configuration
    system). Safe to call again later (e.g. to apply a changed
    configuration, or between tests) — previous handlers attached by this
    function are removed first.

    Args:
        settings: The validated logging configuration to apply.
    """
    root_logger = logging.getLogger(_ROOT_LOGGER_NAME)
    root_logger.setLevel(settings.level.value)

    _remove_existing_handlers(root_logger)

    formatter = build_formatter(settings)

    if settings.console_enabled:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if settings.file_path is not None:
        settings.file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(settings.file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Prevent the "nikola" logger's records from also being handled by the
    # stdlib root logger (name ""), which could otherwise double-print to
    # the console if something else in the process has configured it.
    root_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return a module-specific logger, scoped under the "nikola" root.

    This is the single entry point every module in the codebase should use
    to obtain a logger — never `logging.getLogger(__name__)` directly.

    Args:
        name: Conventionally `__name__` of the calling module, e.g.
            `"nikola.infrastructure.config.loader"`. If `name` is not
            already within the "nikola" hierarchy, it is nested under it
            (as `"nikola.<name>"`) so the centrally configured level and
            handlers still apply via logger-hierarchy propagation.

    Returns:
        A standard library `logging.Logger`, which satisfies
        `nikola.domain.ports.logger_port.LoggerPort`.
    """
    if name == _ROOT_LOGGER_NAME or name.startswith(f"{_ROOT_LOGGER_NAME}."):
        return logging.getLogger(name)
    return logging.getLogger(f"{_ROOT_LOGGER_NAME}.{name}")


def _remove_existing_handlers(logger: logging.Logger) -> None:
    """Detach and close every handler currently on `logger`.

    Called at the start of `setup_logging()` so repeated calls don't
    accumulate duplicate handlers (which would cause every log line to be
    emitted once per accumulated handler).
    """
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
