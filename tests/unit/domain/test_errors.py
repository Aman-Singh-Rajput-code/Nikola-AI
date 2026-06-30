"""Unit tests for `nikola.domain.errors`.

Pure, I/O-free tests confirming the exception hierarchy's inheritance
contract — important because calling code (and future sprints) will rely
on being able to catch `ConfigurationError` (or `NikolaError`, for the
broadest catch) to handle every error of that family uniformly, regardless
of which specific subclass was raised.
"""

from __future__ import annotations

import pytest

from nikola.domain.errors import (
    CommandExecutionError,
    ConfigFileNotFoundError,
    ConfigurationError,
    ConfigValidationError,
    InvalidCommandError,
    NikolaError,
    ToolUnavailableError,
)


@pytest.mark.unit
class TestErrorHierarchy:
    def test_configuration_error_is_a_nikola_error(self) -> None:
        assert issubclass(ConfigurationError, NikolaError)

    def test_config_file_not_found_error_is_a_configuration_error(self) -> None:
        assert issubclass(ConfigFileNotFoundError, ConfigurationError)

    def test_config_validation_error_is_a_configuration_error(self) -> None:
        assert issubclass(ConfigValidationError, ConfigurationError)

    def test_all_config_errors_are_catchable_as_nikola_error(self) -> None:
        for error_cls in (ConfigurationError, ConfigFileNotFoundError, ConfigValidationError):
            with pytest.raises(NikolaError):
                raise error_cls("boom")

    def test_nikola_error_is_a_plain_exception(self) -> None:
        assert issubclass(NikolaError, Exception)


@pytest.mark.unit
class TestCommandAndToolErrorHierarchy:
    def test_invalid_command_error_is_a_nikola_error(self) -> None:
        assert issubclass(InvalidCommandError, NikolaError)

    def test_tool_unavailable_error_is_a_nikola_error(self) -> None:
        assert issubclass(ToolUnavailableError, NikolaError)

    def test_command_execution_error_is_a_nikola_error(self) -> None:
        assert issubclass(CommandExecutionError, NikolaError)

    def test_all_three_are_catchable_as_nikola_error(self) -> None:
        for error_cls in (InvalidCommandError, ToolUnavailableError, CommandExecutionError):
            with pytest.raises(NikolaError):
                raise error_cls("boom")

    def test_the_three_are_independent_siblings_not_nested(self) -> None:
        """InvalidCommandError and ToolUnavailableError are not specializations
        of CommandExecutionError — they represent failures before execution
        ever begins, not failures during execution.
        """
        assert not issubclass(InvalidCommandError, CommandExecutionError)
        assert not issubclass(ToolUnavailableError, CommandExecutionError)
