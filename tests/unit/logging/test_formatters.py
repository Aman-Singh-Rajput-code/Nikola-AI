"""Unit tests for `nikola.infrastructure.logging.formatters`.

Covers the formatter factory's branching on `json_format`, and the shape
of output each concrete formatter produces — including the timestamp,
level, logger name, and message fields required by Sprint 3.
"""

from __future__ import annotations

import json
import logging

import pytest

from nikola.infrastructure.config.settings import LoggingSettings
from nikola.infrastructure.logging.formatters import (
    JsonFormatter,
    TextFormatter,
    build_formatter,
)


def _make_record(
    *,
    name: str = "nikola.test_module",
    level: int = logging.INFO,
    message: str = "hello world",
) -> logging.LogRecord:
    return logging.LogRecord(
        name=name,
        level=level,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=None,
        exc_info=None,
    )


@pytest.mark.unit
class TestBuildFormatter:
    def test_returns_json_formatter_when_json_format_true(self) -> None:
        formatter = build_formatter(LoggingSettings(json_format=True))
        assert isinstance(formatter, JsonFormatter)

    def test_returns_text_formatter_when_json_format_false(self) -> None:
        formatter = build_formatter(LoggingSettings(json_format=False))
        assert isinstance(formatter, TextFormatter)


@pytest.mark.unit
class TestTextFormatter:
    def test_output_contains_level_logger_name_and_message(self) -> None:
        formatter = TextFormatter()
        record = _make_record(name="nikola.infrastructure.config", message="config loaded")

        output = formatter.format(record)

        assert "INFO" in output
        assert "nikola.infrastructure.config" in output
        assert "config loaded" in output

    def test_output_contains_a_timestamp(self) -> None:
        """A timestamp must be present; loosely checked via the date separator."""
        formatter = TextFormatter()
        record = _make_record()

        output = formatter.format(record)

        # %Y-%m-%dT... produces a 4-digit year followed by a hyphen near the start.
        assert output[:4].isdigit()
        assert "-" in output[:8]


@pytest.mark.unit
class TestJsonFormatter:
    def test_output_is_valid_json(self) -> None:
        formatter = JsonFormatter()
        record = _make_record()

        output = formatter.format(record)

        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_output_contains_required_fields(self) -> None:
        formatter = JsonFormatter()
        record = _make_record(
            name="nikola.application.planner",
            level=logging.WARNING,
            message="plan validation failed",
        )

        parsed = json.loads(formatter.format(record))

        assert parsed["level"] == "WARNING"
        assert parsed["logger"] == "nikola.application.planner"
        assert parsed["message"] == "plan validation failed"
        assert "timestamp" in parsed

    def test_timestamp_is_iso_8601(self) -> None:
        from datetime import datetime

        formatter = JsonFormatter()
        record = _make_record()

        parsed = json.loads(formatter.format(record))

        # Must not raise: confirms the timestamp round-trips as ISO 8601.
        datetime.fromisoformat(parsed["timestamp"])

    def test_includes_exception_info_when_present(self) -> None:
        formatter = JsonFormatter()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            record = logging.LogRecord(
                name="nikola.test_module",
                level=logging.ERROR,
                pathname=__file__,
                lineno=1,
                msg="something failed",
                args=None,
                exc_info=sys.exc_info(),
            )

        parsed = json.loads(formatter.format(record))

        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]
        assert "boom" in parsed["exception"]

    def test_omits_exception_key_when_absent(self) -> None:
        formatter = JsonFormatter()
        record = _make_record()

        parsed = json.loads(formatter.format(record))

        assert "exception" not in parsed
