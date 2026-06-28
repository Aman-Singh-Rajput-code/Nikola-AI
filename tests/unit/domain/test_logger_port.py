"""Unit tests for `nikola.domain.ports.logger_port.LoggerPort`.

`LoggerPort` is a structural `Protocol`, not an `ABC` — there is nothing to
instantiate or subclass. What matters is that the concrete object handed
back by `get_logger()` (a stdlib `logging.Logger`) satisfies the protocol's
shape, which these tests confirm both via static type-checking semantics
(implicitly, since this file passes `mypy --strict`) and via a runtime
duck-typing check.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

from nikola.infrastructure.logging.logging_service import get_logger

if TYPE_CHECKING:
    from nikola.domain.ports.logger_port import LoggerPort


@pytest.mark.unit
class TestLoggerPortConformance:
    def test_stdlib_logger_has_all_required_methods(self) -> None:
        logger: LoggerPort = get_logger("conformance_check")

        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "critical")

    def test_get_logger_return_value_is_usable_as_a_logger_port(self) -> None:
        """A function typed to accept LoggerPort must accept get_logger()'s result."""

        def _accepts_logger_port(logger: LoggerPort) -> None:
            logger.info("works fine through the port")

        _accepts_logger_port(get_logger("port_usage_check"))

    def test_plain_stdlib_logger_also_satisfies_the_protocol(self) -> None:
        """Confirms the protocol isn't accidentally coupled to get_logger's wrapping."""
        plain_logger = logging.getLogger("not_via_get_logger")

        def _accepts_logger_port(logger: LoggerPort) -> None:
            logger.debug("still fine")

        _accepts_logger_port(plain_logger)
