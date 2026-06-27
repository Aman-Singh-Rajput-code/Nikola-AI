"""Smoke test for the Sprint 1 bootstrap CLI entrypoint.

This is the single test that proves the project's packaging, src-layout, and
console-script wiring all work end to end. It deliberately tests nothing about
application behavior, because none exists yet — only that `main()` produces
the expected, exact bootstrap confirmation message.
"""

from __future__ import annotations

import pytest

from nikola.interfaces.cli.cli_app import __version__, main


@pytest.mark.unit
def test_main_prints_bootstrap_success_message(capsys: pytest.CaptureFixture[str]) -> None:
    """main() must print the exact bootstrap confirmation line."""
    main()

    captured = capsys.readouterr()
    assert captured.out.strip() == f"Nikola AI v{__version__} Bootstrap successful."


@pytest.mark.unit
def test_version_is_semver_string() -> None:
    """__version__ must match the project's declared version (0.1.0 for Sprint 1)."""
    assert __version__ == "0.1.0"
