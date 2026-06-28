"""Log record formatters.

This module is the seam that makes "JSON logging can be added later
without breaking changes" (Sprint 3 requirement) concrete rather than
aspirational: `build_formatter()` is the single place that decides which
`logging.Formatter` to construct, based on `LoggingSettings.json_format`.
Call sites (the logging service's handler setup) never construct a
formatter themselves and never branch on `json_format` directly — they
just call `build_formatter(settings)` and attach whatever comes back.

Both formatters below include a timestamp, the logger's (module-specific)
name, the level, and the message — satisfying the "timestamped log
entries" and "module-specific loggers" requirements regardless of which
format is active.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nikola.infrastructure.config.settings import LoggingSettings

__all__ = ["build_formatter", "TextFormatter", "JsonFormatter"]

#: Shared, human-readable format string used by the plain-text formatter.
#: %(name)s is the module-specific logger name (e.g. "nikola.infrastructure.config.loader").
_TEXT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


class TextFormatter(logging.Formatter):
    """Human-readable, single-line log format for local development.

    Example output:
        2026-06-28T10:15:32+0000 | INFO     | nikola.infrastructure.config.loader | ...
    """

    def __init__(self) -> None:
        super().__init__(fmt=_TEXT_FORMAT, datefmt=_DATE_FORMAT)


class JsonFormatter(logging.Formatter):
    """One JSON object per log line, for production/log-aggregator consumption.

    Deliberately minimal for Sprint 3: timestamp, level, logger name,
    message, and (when present) exception info. Later sprints may extend
    this with additional structured fields (e.g. correlation IDs once the
    orchestrator introduces them) without changing this class's public
    contract or how callers obtain it.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def build_formatter(settings: LoggingSettings) -> logging.Formatter:
    """Return the `logging.Formatter` selected by `settings.json_format`.

    This is the only place in the codebase that decides text-vs-JSON. Every
    handler attached by `LoggingService` is built by calling this function
    rather than constructing a formatter inline.
    """
    if settings.json_format:
        return JsonFormatter()
    return TextFormatter()
