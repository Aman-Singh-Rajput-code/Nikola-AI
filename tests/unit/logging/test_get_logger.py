"""Unit tests for `nikola.infrastructure.logging.logging_service.get_logger`.

Covers the "module-specific loggers" requirement: every call site gets a
distinctly-named logger, correctly nested under the single "nikola" root
so centrally configured levels/handlers apply via propagation.
"""

from __future__ import annotations

import logging

import pytest

from nikola.infrastructure.logging.logging_service import get_logger


@pytest.mark.unit
class TestGetLogger:
    def test_returns_a_standard_logger(self) -> None:
        logger = get_logger("nikola.some.module")
        assert isinstance(logger, logging.Logger)

    def test_nests_unprefixed_name_under_nikola_root(self) -> None:
        logger = get_logger("some.module")
        assert logger.name == "nikola.some.module"

    def test_leaves_already_prefixed_name_unchanged(self) -> None:
        logger = get_logger("nikola.infrastructure.config.loader")
        assert logger.name == "nikola.infrastructure.config.loader"

    def test_returns_the_root_logger_itself_when_name_is_exactly_nikola(self) -> None:
        logger = get_logger("nikola")
        assert logger.name == "nikola"

    def test_typical_dunder_name_usage_is_nested_correctly(self) -> None:
        """Simulates the conventional call site usage: get_logger(__name__)."""
        simulated_module_name = "nikola.infrastructure.persistence.sqlite.conversation_repo_impl"
        logger = get_logger(simulated_module_name)
        assert logger.name == simulated_module_name

    def test_different_names_return_different_loggers(self) -> None:
        logger_a = get_logger("module_a")
        logger_b = get_logger("module_b")
        assert logger_a is not logger_b
        assert logger_a.name != logger_b.name

    def test_same_name_returns_the_same_logger_instance(self) -> None:
        """Python's logging registry caches by name; confirm get_logger preserves that."""
        first = get_logger("same.module")
        second = get_logger("same.module")
        assert first is second

    def test_child_logger_is_a_descendant_of_the_nikola_root(self) -> None:
        child = get_logger("some.deeply.nested.module")
        root = logging.getLogger("nikola")
        # Logging hierarchy is name-prefix based; this confirms child's
        # effective parent chain reaches the nikola root.
        assert child.name.startswith(root.name + ".")
