"""Shared fixtures for the configuration test suite.

Configuration is sourced partly from real process environment variables and
`.env` files relative to the current working directory. Without isolation,
tests could: (a) pick up whatever the developer happens to have exported in
their shell, (b) leak NIKOLA_* env vars set by one test into the next, or
(c) accidentally read the real repository's `config/default.yaml`. The
fixtures below close all three gaps.

`write_yaml` is exposed as the `yaml_writer` fixture (rather than a plain
importable helper function) because `tests/` is not an installed/importable
package in this project — only `src/nikola` is. Fixtures are pytest's
supported mechanism for sharing test helpers across modules without
requiring the test tree itself to be a proper Python package.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Protocol

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


class YamlWriter(Protocol):
    """Callable signature returned by the `yaml_writer` fixture."""

    def __call__(self, path: Path, content: str) -> Path: ...


@pytest.fixture(autouse=True)
def _isolated_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Strip all NIKOLA_*-prefixed environment variables before each test.

    Applied automatically to every test in this directory tree so that no
    test needs to remember to do this itself, and so a developer's real
    shell environment (which may well have NIKOLA_* variables set) never
    affects test outcomes.
    """
    for key in list(os.environ.keys()):
        if key.startswith("NIKOLA_"):
            monkeypatch.delenv(key, raising=False)
    yield


@pytest.fixture
def isolated_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Run a test inside an empty temporary directory.

    Prevents tests from accidentally discovering the real project's
    `config/default.yaml` or `.env` file via relative-path lookups, and
    gives each test a clean place to write its own fixture files.
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def yaml_writer() -> YamlWriter:
    """Return a callable that writes YAML content to a path, creating parents."""

    def _write(path: Path, content: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    return _write
