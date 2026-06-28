"""Unit tests for `nikola.domain.errors`.

Pure, I/O-free tests confirming the exception hierarchy's inheritance
contract — important because calling code (and future sprints) will rely
on being able to catch `ConfigurationError` to handle every configuration
problem uniformly, regardless of which specific subclass was raised.
"""

from __future__ import annotations

import pytest

from nikola.domain.errors import (
    ConfigFileNotFoundError,
    ConfigurationError,
    ConfigValidationError,
    NikolaError,
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
