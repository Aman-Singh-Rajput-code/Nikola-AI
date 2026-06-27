"""Minimal CLI entrypoint for Nikola AI.

This module exists, in Sprint 1, purely to prove that the project's packaging,
src-layout, and console-script wiring are correctly configured end to end.

It intentionally contains NO application logic. Starting in later sprints,
this module will be expanded to dispatch into `nikola.bootstrap.app_factory`
to build a fully wired application (DI container, configuration, logging,
event bus) before handing control to the orchestrator. None of that exists
yet, by design.
"""

from __future__ import annotations

__version__ = "0.1.0"


def main() -> None:
    """Entrypoint registered as the `nikola` console script.

    Sprint 1 scope: print a single confirmation line and exit successfully.
    This is the smoke test that proves `pip install -e .` and the
    `[project.scripts]` entry in pyproject.toml are wired correctly.
    """
    print(f"Nikola AI v{__version__} Bootstrap successful.")


if __name__ == "__main__":
    main()
