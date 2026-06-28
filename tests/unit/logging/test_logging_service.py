"""Unit tests for `nikola.infrastructure.logging.logging_service.setup_logging`.

Covers: console handler attachment, file handler attachment, level
configuration sourced from `LoggingSettings`, idempotent re-configuration
(no duplicate handlers across repeated calls), and that records actually
reach the configured destinations (console capture, file content).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

from nikola.infrastructure.config.settings import LoggingSettings, LogLevel
from nikola.infrastructure.logging.logging_service import get_logger, setup_logging

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.unit
class TestSetupLoggingConsoleHandler:
    def test_console_enabled_attaches_a_stream_handler(self) -> None:
        setup_logging(LoggingSettings(console_enabled=True, file_path=None))

        root = logging.getLogger("nikola")
        stream_handlers = [h for h in root.handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) == 1

    def test_console_disabled_attaches_no_stream_handler(self) -> None:
        setup_logging(LoggingSettings(console_enabled=False, file_path=None))

        root = logging.getLogger("nikola")
        assert len(root.handlers) == 0

    def test_logged_message_is_emitted_to_console(self, capsys: pytest.CaptureFixture[str]) -> None:
        setup_logging(LoggingSettings(console_enabled=True, json_format=False))
        logger = get_logger("test_console_emission")

        logger.info("a console-bound message")

        captured = capsys.readouterr()
        assert "a console-bound message" in captured.out


@pytest.mark.unit
class TestSetupLoggingFileHandler:
    def test_file_path_set_attaches_a_file_handler(self, tmp_path: Path) -> None:
        log_file = tmp_path / "nikola.log"
        setup_logging(LoggingSettings(console_enabled=False, file_path=log_file))

        root = logging.getLogger("nikola")
        file_handlers = [h for h in root.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1

    def test_file_path_none_attaches_no_file_handler(self) -> None:
        setup_logging(LoggingSettings(console_enabled=True, file_path=None))

        root = logging.getLogger("nikola")
        file_handlers = [h for h in root.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 0

    def test_logged_message_is_written_to_the_file(self, tmp_path: Path) -> None:
        log_file = tmp_path / "nikola.log"
        setup_logging(LoggingSettings(console_enabled=False, file_path=log_file, json_format=False))
        logger = get_logger("test_file_emission")

        logger.warning("a file-bound message")
        for handler in logging.getLogger("nikola").handlers:
            handler.flush()

        assert log_file.exists()
        assert "a file-bound message" in log_file.read_text(encoding="utf-8")

    def test_creates_parent_directories_for_the_log_file(self, tmp_path: Path) -> None:
        nested_log_file = tmp_path / "nested" / "dirs" / "nikola.log"
        setup_logging(LoggingSettings(console_enabled=False, file_path=nested_log_file))

        assert nested_log_file.parent.is_dir()

    def test_both_console_and_file_can_be_enabled_simultaneously(self, tmp_path: Path) -> None:
        log_file = tmp_path / "nikola.log"
        setup_logging(LoggingSettings(console_enabled=True, file_path=log_file))

        root = logging.getLogger("nikola")
        assert len(root.handlers) == 2


@pytest.mark.unit
class TestSetupLoggingLevel:
    @pytest.mark.parametrize(
        "level",
        [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL],
    )
    def test_root_logger_level_matches_settings(self, level: LogLevel) -> None:
        setup_logging(LoggingSettings(level=level))

        root = logging.getLogger("nikola")
        assert root.level == logging.getLevelName(level.value)

    def test_messages_below_configured_level_are_suppressed(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        setup_logging(LoggingSettings(level=LogLevel.WARNING, json_format=False))
        logger = get_logger("test_level_suppression")

        logger.info("should not appear")
        logger.warning("should appear")

        captured = capsys.readouterr()
        assert "should not appear" not in captured.out
        assert "should appear" in captured.out


@pytest.mark.unit
class TestSetupLoggingIdempotency:
    def test_calling_setup_logging_twice_does_not_duplicate_handlers(self) -> None:
        setup_logging(LoggingSettings(console_enabled=True))
        setup_logging(LoggingSettings(console_enabled=True))

        root = logging.getLogger("nikola")
        assert len(root.handlers) == 1

    def test_reconfiguring_with_different_settings_replaces_handlers(self, tmp_path: Path) -> None:
        setup_logging(LoggingSettings(console_enabled=True, file_path=None))
        root = logging.getLogger("nikola")
        assert len(root.handlers) == 1

        log_file = tmp_path / "nikola.log"
        setup_logging(LoggingSettings(console_enabled=False, file_path=log_file))
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0], logging.FileHandler)

    def test_repeated_calls_do_not_cause_duplicate_log_lines(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        setup_logging(LoggingSettings(console_enabled=True, json_format=False))
        setup_logging(LoggingSettings(console_enabled=True, json_format=False))
        logger = get_logger("test_no_duplicate_lines")

        logger.info("only once please")

        captured = capsys.readouterr()
        assert captured.out.count("only once please") == 1


@pytest.mark.unit
class TestSetupLoggingPropagation:
    def test_nikola_root_does_not_propagate_to_stdlib_root(self) -> None:
        setup_logging(LoggingSettings())

        root = logging.getLogger("nikola")
        assert root.propagate is False
