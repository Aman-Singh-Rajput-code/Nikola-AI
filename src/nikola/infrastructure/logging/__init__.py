"""Structured application logging.

Sprint 3 implements the centralized logging framework:

- `logging_service.py` — `setup_logging()` (one-time handler/formatter/level
  configuration, driven by `LoggingSettings`) and `get_logger(name)` (the
  single entry point every module uses to obtain a module-specific logger).
- `formatters.py` — `build_formatter()`, the seam that selects between
  plain-text and JSON output based on `LoggingSettings.json_format`.

The immutable audit logger (for permission/security-relevant events) is a
separate concern, implemented in a later sprint alongside the Permission
Gateway.
"""

from nikola.infrastructure.logging.formatters import JsonFormatter, TextFormatter, build_formatter
from nikola.infrastructure.logging.logging_service import get_logger, setup_logging

__all__ = [
    "setup_logging",
    "get_logger",
    "build_formatter",
    "TextFormatter",
    "JsonFormatter",
]
