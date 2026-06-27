# Nikola AI

**Nikola AI** is a modular, provider-agnostic AI Operating System — designed to grow over
time into a personal assistant capable of controlling a computer, browsing the web, writing
code, managing files, scheduling tasks, remembering conversations, and orchestrating multiple
specialized agents.

This project is built on **Clean Architecture** and **SOLID** principles, with a
**plugin-based tool system** and a **provider-agnostic AI Brain abstraction** (Claude, OpenAI,
Gemini, Ollama, or any future provider) — so the core application logic never has to change
when the underlying AI model, storage backend, or interface does.

> **Current status: Sprint 1 — Project Bootstrap.**
> This repository currently contains only the project skeleton, tooling configuration, and a
> minimal CLI smoke test. No Brain, Planner, Agent, Memory, Tool, or Permission logic has been
> implemented yet — that begins in subsequent sprints per the project roadmap.

---

## Architecture at a Glance

The codebase follows a strict **Clean Architecture** dependency rule: dependencies only point
inward.

```
domain/          <- pure business entities & ports. Zero third-party dependencies.
application/     <- use cases / orchestration. Depends only on domain/.
infrastructure/  <- concrete adapters (LLM providers, databases, schedulers).
plugins/         <- tool plugins (filesystem, terminal, browser, etc.) — the only
                    code permitted to perform real-world side effects.
interfaces/      <- user-facing entrypoints (CLI, web, voice).
bootstrap/       <- composition root: wires everything together.
```

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full architectural design, including the
permission system, multi-agent design, and the complete information-flow diagrams.

---

## Project Structure

```
nikola-ai/
├── pyproject.toml          # Package metadata, build config, all dev-tool configs
├── requirements.txt        # Sprint 1 pinned dependencies (convenience mirror of pyproject)
├── .gitignore
├── .pre-commit-config.yaml # Ruff + Black + MyPy git hooks
├── LICENSE                 # MIT
├── README.md               # This file
├── ARCHITECTURE.md         # Full architecture design document
│
├── src/nikola/             # Importable package (src-layout)
│   ├── domain/              # Entities, value objects, errors, ports
│   ├── application/         # Use cases: planner, agent, tool_registry, permissions,
│   │                         #   memory, conversation, scheduler, orchestration
│   ├── infrastructure/      # Adapters: brains, persistence, event_bus, scheduler,
│   │                         #   logging, config
│   ├── plugins/             # Tool plugins: filesystem, terminal, browser, messaging,
│   │                         #   vision, voice, system_info
│   ├── interfaces/          # CLI, web, voice entrypoints
│   └── bootstrap/           # Dependency injection wiring / composition root
│
├── config/                 # Default config, permission policy, agent profiles (later sprints)
├── tests/
│   ├── unit/                 # Fast, no I/O
│   ├── integration/          # Real adapters (DB, filesystem, network)
│   ├── e2e/                  # Full user journeys
│   └── fixtures/
├── scripts/                 # Dev/maintenance scripts
└── docs/adr/                # Architecture Decision Records
```

Every folder above already exists in this repository with an explanatory `__init__.py`
docstring (or `.gitkeep` for non-package directories), even though most are empty of logic —
this is intentional. The skeleton is laid out up front so future sprints add code into an
already-agreed structure rather than inventing folders ad hoc.

---

## Requirements

- **Python 3.12+**
- `pip` (or `pipx`/`uv`, if you prefer — standard `pip` instructions are given below)
- Git

---

## Getting Started — From Zero

These are the **exact commands** to clone, set up, and verify this project from scratch.

```bash
# 1. Clone the repository
git clone https://github.com/your-org/nikola-ai.git
cd nikola-ai

# 2. Create and activate a virtual environment
python3.12 -m venv .venv
source .venv/bin/activate          # On Windows: .venv\Scripts\activate

# 3. Upgrade pip (recommended)
pip install --upgrade pip

# 4. Install the project in editable mode, with dev dependencies
pip install -e ".[dev]"

# 5. Install git hooks (Ruff, Black, MyPy run automatically on every commit)
pre-commit install

# 6. Verify the bootstrap: run the CLI entrypoint
nikola
# Expected output:
#   Nikola AI v0.1.0 Bootstrap successful.

# 7. Run the test suite
pytest

# 8. Run the full quality gate manually (what CI runs)
ruff check .
black --check .
mypy src
pytest -m unit
```

If step 6 prints `Nikola AI v0.1.0 Bootstrap successful.`, the project is correctly installed
and the src-layout packaging, console-script entry point, and import path are all wired
correctly.

---

## Development Workflow

| Task | Command |
|---|---|
| Run the CLI | `nikola` |
| Run all tests | `pytest` |
| Run only unit tests | `pytest -m unit` |
| Lint (check only) | `ruff check .` |
| Lint (auto-fix) | `ruff check . --fix` |
| Format (check only) | `black --check .` |
| Format (apply) | `black .` |
| Type-check | `mypy src` |
| Run all pre-commit hooks manually | `pre-commit run --all-files` |

---

## Tooling Configuration

All tooling is configured centrally in [`pyproject.toml`](./pyproject.toml):

- **[Ruff](https://docs.astral.sh/ruff/)** — linting and import sorting (replaces
  flake8 + isort). Configured under `[tool.ruff]`.
- **[Black](https://black.readthedocs.io/)** — opinionated code formatter. Configured
  under `[tool.black]`. Line length and target Python version are kept in sync with Ruff.
- **[MyPy](https://mypy-lang.org/)** — static type checking. Configured under `[tool.mypy]`.
  `domain/` is checked in `strict` mode from Sprint 1 onward; other layers are widened to
  strict mode as they're implemented in later sprints.
- **[Pytest](https://docs.pytest.org/)** — test runner. Configured under
  `[tool.pytest.ini_options]`, with custom markers (`unit`, `integration`, `e2e`) matching the
  three-tier test strategy described in the architecture document.
- **[pre-commit](https://pre-commit.com/)** — runs Ruff, Black, and MyPy automatically on
  every commit. Configured in [`.pre-commit-config.yaml`](./.pre-commit-config.yaml).

---

## Packaging Notes

This project uses **src-layout** (`src/nikola/`, not a flat `nikola/` at the repo root). This
is a deliberate choice: it guarantees that `import nikola` always resolves to the properly
*installed* package, never to an accidental same-named folder sitting in your current working
directory. Combined with `pip install -e .` (editable install), this gives the best of both
worlds — live code edits are picked up immediately, but the import path is never ambiguous.

---

## Roadmap

This repository is being built incrementally according to a versioned roadmap, from
**v0.1 (Skeleton & Contracts)** — this sprint — through **v3.0 (Jarvis-Class Assistant)**. See
the project's roadmap document for the full milestone breakdown, acceptance criteria, and
implementation order for every future sprint.

**Sprint 1 (this repository) delivers only:**
- The complete folder structure
- Packaging, dependency, and dev-tool configuration
- A minimal `nikola` CLI command that prints a bootstrap confirmation message

**No Brain, Planner, Agent, Tool Registry, Memory, or Permission logic exists yet.** That is
intentional and matches the project's architecture-first development philosophy: contracts and
tooling before any business logic.

---

## License

MIT — see [`LICENSE`](./LICENSE).
