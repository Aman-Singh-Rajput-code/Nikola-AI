# Nikola AI — Developer Handoff Document

**Location:** `project_docs/10_DEVELOPER_HANDOFF.md`
**Verified against:** Sprint 9 repository state
**Purpose:** Architectural continuity guide for future development — human or AI
**Audience:** Any developer or Claude session continuing Nikola AI without access to prior conversation history

---

## Source of Truth Hierarchy

Before reading further, understand the authoritative hierarchy for this project:

1. **Git repository / actual source code** → the definitive record of what is *implemented*. If a class is not in the repository, it does not exist. If a test does not pass, the feature is not complete.

2. **Project documentation** (`project_docs/`) → authoritative for architecture intent, development philosophy, established design decisions, and the roadmap. Describes *why* things were built the way they were.

3. **This Developer Handoff Document** → a continuity guide that bridges the gap between what exists now and how future development should proceed. It explains the current architecture, the decisions that shaped it, and the rules for extending it correctly.

4. **Previous Claude conversation history** → **NOT a source of truth**. Conversations contain design reasoning and intermediate steps, but what matters is what ended up in the repository. Never assume something exists because it was discussed in a past session.

**Rule:** If you cannot find something in the repository, do not treat it as implemented, no matter what any document says about it.

---

## Table of Contents

1. [Project Vision](#1-project-vision)
2. [Development Philosophy](#2-development-philosophy)
3. [Architecture Overview — Current State](#3-architecture-overview--current-state)
4. [Sprint History — Sprints 1–9](#4-sprint-history--sprints-19)
5. [Currently Implemented Capabilities](#5-currently-implemented-capabilities)
6. [Current Limitations](#6-current-limitations)
7. [Dependency Rules](#7-dependency-rules)
8. [Important Design Decisions](#8-important-design-decisions)
9. [Coding Standards](#9-coding-standards)
10. [Testing Strategy](#10-testing-strategy)
11. [Development Workflow](#11-development-workflow)
12. [Repository Organization](#12-repository-organization)
13. [Future Development Roadmap](#13-future-development-roadmap)
14. [Rules For Future Development](#14-rules-for-future-development)
15. [Guidance For Future Claude Conversations](#15-guidance-for-future-claude-conversations)

---

## 1. Project Vision

### What Nikola AI Is

Nikola AI is a **modular, provider-agnostic AI Operating System** built in Python 3.12+. The long-term vision is a personal AI assistant capable of autonomous action: holding conversations, retaining memories across sessions, planning multi-step tasks, and eventually controlling a computer — browsing the web, writing code, managing files, sending email, scheduling recurring jobs, and coordinating specialist sub-agents — without being locked to any single AI provider or storage technology.

After nine sprints, the foundational architecture is complete. The system can manage conversations, store and retrieve memories, reason (via a deterministic NullBrain), classify intent, and produce structured execution plans. **It cannot yet execute those plans, invoke tools, call a real AI provider, or persist data across process restarts.** These are planned for future sprints.

### Architecture Philosophy

The architecture was chosen to solve Nikola AI's most important constraint: **every major external dependency will change**. The AI provider will change. The storage engine will change. The planning strategy will change. The architecture must absorb those changes without requiring rewrites of core business logic.

This drove two fundamental decisions:
- **Clean Architecture with strict dependency inversion** — domain and application layers are insulated from infrastructure choices by abstract port interfaces.
- **Provider independence by default** — every capability that touches an external system (AI reasoning, data persistence, planning) is modeled as a domain port with at least one concrete implementation that requires no external dependency.

---

## 2. Development Philosophy

### Clean Architecture

Source code dependencies always point inward. The domain layer at the center has no external dependencies. Application logic depends only on the domain. Infrastructure implements domain contracts. The bootstrap layer is the only place that imports from all layers simultaneously.

**Why this matters for Nikola AI specifically:** A system of this scope — spanning AI reasoning, memory, planning, conversation management, eventual tool invocation, and scheduling — will collapse into an entangled monolith without strict layering. Clean Architecture is the structural guarantee that these concerns stay separated as the system grows.

### SOLID Principles

- **Single Responsibility:** `ConversationService` manages conversation lifecycle. `ConversationValidator` enforces business rules. `ConversationManager` coordinates at the session level. These are separate classes with separate reasons to change.
- **Open/Closed:** New Brain providers, planning strategies, and memory retrieval strategies can be added without modifying existing classes — only by adding new implementations of existing ports.
- **Liskov Substitution:** Every concrete port implementation is fully substitutable. `NullBrain` and any future `ClaudeBrainAdapter` are interchangeable from the application layer's perspective.
- **Interface Segregation:** Ports are narrow. `BrainPort` has one method. `PlannerPort` has one method. No port forces implementors to provide unrelated behavior.
- **Dependency Inversion:** High-level modules (application use cases) depend on abstractions (ports). Concrete implementations live in infrastructure. The DI container wires them.

### Provider Independence

Every major capability is modeled as a domain port with a no-dependency default implementation: `NullBrain` (no API key), `InMemoryConversationRepository` (no database), `InMemoryMemoryRepository` (no database), `RuleBasedPlanner` (no AI model). This means:
- The test suite passes in CI without API keys or network access.
- The system can be demonstrated without external services.
- Switching providers requires a config change and one new file — nothing else.

### Test-Driven Quality

A sprint is complete only when four validation gates all pass: `nikola` (CLI runs), `pytest` (all tests pass), `ruff check .` (zero lint errors), `mypy src` (zero type errors under strict mode). These gates are run both in the development environment and in a clean-room extraction before packaging.

### Incremental Delivery

Each sprint delivers a complete, tested, packaging-ready artifact. No sprint ends with "this will be fixed next sprint." Every sprint's deliverable must be independently usable as a baseline.

---

## 3. Architecture Overview — Current State

This section describes the architecture **as it exists after Sprint 9**. Stub directories that contain only placeholder `__init__.py` files are not described as implemented — they exist to pre-declare package structure for future sprints.

### Dependency Direction

```
interfaces/ ──► bootstrap/ ──► infrastructure/
                                      │
               application/ ◄─────────┘
                     │
                domain/  (imports from nothing outside stdlib)
```

Every arrow represents "may import from." The domain layer is imported by everyone; it imports from no one. `bootstrap/` is the only layer that imports from all other layers simultaneously.

### Domain Layer (`src/nikola/domain/`) — IMPLEMENTED

The heart of the system. Pure Python standard library only. No third-party imports.

**Value Objects** (`domain/value_objects/`): All immutable, validated, compared by value.
- Typed identifiers: `CommandId`, `TaskId`, `SessionId`, `ConversationId`, `MessageId`, `MemoryId`, `PlanId`, `StepId`
- `Intent`, `IntentType` — Brain's classification of a reasoning request
- Enums (all `StrEnum`): `TaskStatus`, `CommandType`, `ResponseType`, `MessageRole`, `ConversationStatus`, `MemoryType`, `PlanStatus`, `StepStatus`, `StepType`

**Entities** (`domain/entities/`): Objects with identity and lifecycle.
- `Command`, `Task`, `Response`, `Session` — core request/execution/outcome cycle (Sprint 4)
- `ConversationTurn`, `ReasoningRequest`, `ReasoningResponse` — Brain port boundary objects (Sprint 6)
- `Message`, `Conversation` — conversation record (Sprint 7)
- `MemoryEntry`, `MemoryQuery`, `MemoryResult` — memory system (Sprint 8)
- `PlanStep`, `Plan`, `PlanningRequest`, `PlanningResult` — planning system (Sprint 9)

**Ports** (`domain/ports/`): Abstract interfaces — what the domain needs from the outside world.
- `ConfigProviderPort` — provides `NikolaSettings`
- `LoggerPort` — Protocol for logger instances
- `BrainPort` — abstract AI reasoning interface
- `ConversationRepositoryPort` — abstract conversation persistence
- `MemoryRepositoryPort` — abstract memory persistence
- `PlannerPort` — abstract planning interface

**Errors** (`domain/errors/`): Exception hierarchy under `NikolaError`.
- `ConfigurationError`, `ConfigFileNotFoundError`, `ConfigValidationError`
- `InvalidCommandError`, `ToolUnavailableError`, `CommandExecutionError`
- `ServiceNotRegisteredError`, `CircularDependencyError`
- `BrainError`, `ConversationError`, `MessageValidationError`
- `MemoryError` (distinct from Python's built-in `MemoryError`)
- `PlanningError`

**Events** (`domain/events/`): `TaskStarted`, `TaskCompleted` — frozen dataclasses prepared for a future event bus. Not yet connected to any bus.

**Must never:** Import from `application/`, `infrastructure/`, `bootstrap/`, or any third-party library.

---

### Application Layer (`src/nikola/application/`) — PARTIALLY IMPLEMENTED

Use-case logic and orchestration. Depends only on `domain/`.

**Implemented subpackages:**

`application/brain/`:
- `IntentClassifier` — abstract base. Defines how intent is classified.
- `DefaultIntentClassifier` — delegates to `BrainPort.reason()` and extracts the `Intent` from the response.

`application/conversation/`:
- `ConversationValidator` — stateless rule enforcement (status, role, content validation).
- `ConversationService` — conversation CRUD: `create_conversation()`, `add_message()`, `get_conversation()`, `get_history_for_brain()`, `archive_conversation()`, `list_active_for_session()`.
- `ConversationManager` — session-level coordinator: `get_or_create_active_conversation()`, role-specific message helpers, `get_brain_context()`.

`application/memory/`:
- `MemoryRetrievalStrategy` — abstract ordering/limiting policy.
- `ImportanceRetrievalStrategy` — orders results by `importance` descending, then `created_at` descending; applies `query.limit` after sorting.
- `MemoryService` — primary memory use case: `store()`, `retrieve()`, `get()`, `strengthen()`, `forget()`.
- `MemoryManager` — high-level coordinator: `remember_fact()` (SEMANTIC), `record_episode()` (EPISODIC), `note_procedure()` (PROCEDURAL), `set_working_memory()` (WORKING), `recall()`, `strengthen()`, `forget()`.

`application/planner/`:
- `PlanningService` — delegates to `PlannerPort`: `create_plan()`, `create_plan_for_goal()`.
- `PlanningManager` — goal-level coordinator: `plan_goal()`, `plan_goal_simple()`.

**Stub-only subpackages** (placeholder `__init__.py` only — NOT implemented):
- `application/agent/` — future: agent orchestration (think-act-observe loop)
- `application/orchestration/` — future: top-level Orchestrator use case
- `application/permissions/` — future: Permission Gateway
- `application/scheduler/` — future: scheduled/recurring task use cases
- `application/tool_registry/` — future: tool discovery and invocation use cases

**Must never:** Import from `infrastructure/`, `bootstrap/`, or `interfaces/`. Must not make network calls or access the filesystem.

---

### Infrastructure Layer (`src/nikola/infrastructure/`) — PARTIALLY IMPLEMENTED

Concrete implementations of domain ports. May import third-party libraries.

**Implemented subpackages:**

`infrastructure/config/`:
- `NikolaSettings` (Pydantic BaseSettings) — layered config resolution: env vars → `.env` → `config/default.yaml` → field defaults. Sub-models: `AppSettings`, `LoggingSettings`, `BrainSettings`.
- `EnvConfigProvider` — implements `ConfigProviderPort`.
- `YamlConfigSettingsSource` — custom Pydantic settings source for YAML.
- `load_settings()` — fail-fast loader that wraps validation errors in `ConfigurationError`.

`infrastructure/logging/`:
- `setup_logging(settings: LoggingSettings)` — configures the `"nikola"` root logger. Must be called once at startup.
- `get_logger(name: str)` — returns a standard `logging.Logger`.
- `TextFormatter`, `JsonFormatter`, `build_formatter()` — console and JSON output formats.

`infrastructure/brains/`:
- `NullBrain` — fully functional `BrainPort` returning deterministic CHAT responses. No network, no API key. The default provider.
- `BrainRegistry` — maps provider name strings to factory callables.
- `BrainFactory` — reads `BrainSettings.provider`, builds the configured Brain via the registry.
- `build_default_registry()` — returns a registry with only `"null"` registered.

`infrastructure/persistence/in_memory/`:
- `InMemoryConversationRepository` — dict-backed `ConversationRepositoryPort`. Process-lifetime only.
- `InMemoryMemoryRepository` — dict-backed `MemoryRepositoryPort`. Python-based filtering; does NOT apply `limit` (the retrieval strategy's responsibility).

`infrastructure/planners/`:
- `RuleBasedPlanner` — implements `PlannerPort`. Scans goal string (case-insensitive) for 8 keyword families: `python`, `flask`, `git`, `test`/`pytest`, `docker`, `deploy`, `api`. Emits fixed, ordered `PlanStep` sequences per match; deduplicates by title; confidence 1.0 for matches, 0.5 for generic fallback. No AI, no network, fully deterministic.

**Stub-only subpackages** (placeholder `__init__.py` only — NOT implemented):
- `infrastructure/event_bus/` — future: pub/sub event bus adapters
- `infrastructure/persistence/sqlite/` — future: SQLite persistence adapters
- `infrastructure/persistence/vector_store/` — future: vector store adapters
- `infrastructure/persistence/file_store/` — future: file-based persistence
- `infrastructure/scheduler/` — future: APScheduler or similar

**Must never:** Import from `application/`, `bootstrap/`, or `interfaces/`.

---

### Bootstrap Layer (`src/nikola/bootstrap/`) — IMPLEMENTED

The composition root. The only layer permitted to import from all other layers simultaneously.

`bootstrap/container.py`:
- `ServiceContainer` — hand-rolled DI container: `register_singleton()`, `register_factory()`, `register_transient()`, `resolve()`, `is_registered()`. Circular dependency detection. ~150 lines of pure Python.
- `ServiceLifetime` — `SINGLETON`, `FACTORY`, `TRANSIENT` (StrEnum).
- `ServiceDescriptor` — internal record per registration.

`bootstrap/compose.py`:
- `LoggingInitialized` — frozen dataclass marker confirming `setup_logging()` ran.
- `compose()` — returns a fully wired `ServiceContainer`. Currently registers 13 singletons:
  1. `ConfigProviderPort` → `EnvConfigProvider`
  2. `LoggingInitialized` → side-effecting logging setup
  3. `BrainPort` → `NullBrain` (via `BrainFactory`/`BrainRegistry`)
  4. `ConversationRepositoryPort` → `InMemoryConversationRepository`
  5. `ConversationService`
  6. `ConversationManager`
  7. `MemoryRepositoryPort` → `InMemoryMemoryRepository`
  8. `ImportanceRetrievalStrategy`
  9. `MemoryService`
  10. `MemoryManager`
  11. `PlannerPort` → `RuleBasedPlanner`
  12. `PlanningService`
  13. `PlanningManager`

**Must not:** Contain business logic. Only register and configure services.

---

### Interfaces Layer (`src/nikola/interfaces/`) — MINIMALLY IMPLEMENTED

`interfaces/cli/cli_app.py`:
- `main()` — prints `"Nikola AI v0.1.0 Bootstrap successful."` and exits. Registered as the `nikola` console script via `pyproject.toml`. Contains no application logic by design.

**Stub-only** (placeholder `__init__.py` only — NOT implemented):
- `interfaces/web/` — future: web API and websocket interface
- `interfaces/voice/` — future: voice interaction loop

---

### Plugins Layer (`src/nikola/plugins/`) — STUB ONLY

All plugin subdirectories (`base/`, `browser/`, `filesystem/`, `messaging/`, `system_info/`, `terminal/`, `vision/`, `voice/`) contain only placeholder `__init__.py` files. The plugin system is **not implemented**. These directories pre-declare the intended package structure for future sprints.

---

## 4. Sprint History — Sprints 1–9

For each sprint: what it delivered, why, the key design decisions, and what it deliberately did NOT implement.

---

### Sprint 1 — Bootstrap

**Purpose:** Establish the project skeleton. Prove that the packaging, src-layout, console-script wiring, and tooling configuration are correct before building anything else.

**What was implemented:**
- `pyproject.toml` — single source of truth for Black, Ruff, MyPy, pytest, dependencies, and console-script registration.
- `src/nikola/` — src-layout package with all future sub-packages created as empty stubs.
- `src/nikola/interfaces/cli/cli_app.py` — `main()` prints bootstrap confirmation and exits.
- Pre-commit hook configuration. GitHub Actions CI workflow skeleton.

**Key design decisions:**
- **src-layout** prevents accidental imports from the project root during testing. This is a Python packaging best practice that matters at scale.
- **`pyproject.toml` as single source of truth** — no `setup.cfg`, no `tox.ini`. All tooling configured in one place.
- **All future sub-packages created as empty stubs immediately** — import paths are valid from Sprint 1 onward; future sprints fill in the content without restructuring the tree.

**Deliberately did NOT implement:** Any business logic, configuration, logging, or application services. Those come in later sprints where they can be designed properly.

**Validation:** `nikola` prints bootstrap message. 2 smoke tests pass. All four gates pass.

---

### Sprint 2 — Production Configuration System

**Purpose:** Establish a layered, validated configuration system that all subsequent sprints can depend on. Configuration must be resolvable from multiple sources with a defined priority order, and it must be accessible via a domain port (not a direct import of the infrastructure class).

**What was implemented:**
- `NikolaSettings` (Pydantic BaseSettings) with `AppSettings` and `LoggingSettings` sub-models.
- `YamlConfigSettingsSource` — custom Pydantic settings source for `config/default.yaml`.
- `EnvConfigProvider` — implements `ConfigProviderPort`; the sole infrastructure adapter for configuration.
- `ConfigProviderPort` — abstract domain port.
- `config/default.yaml` — base configuration, checked into git, must never contain secrets.
- Domain error hierarchy established: `NikolaError`, `ConfigurationError`, `ConfigFileNotFoundError`, `ConfigValidationError`.
- `load_settings()` — wraps Pydantic validation errors in `ConfigurationError`.

**Key design decisions:**
- **Resolution priority (highest wins):** environment variables → `.env` file → `config/default.yaml` → field defaults. Production overrides are environment variables; no code change needed.
- **`ConfigProviderPort` in domain, `EnvConfigProvider` in infrastructure** — application code never imports `EnvConfigProvider` directly. This means the configuration source can be replaced (e.g. a remote config service) without touching any application code.
- **Fail-fast on misconfiguration** — `load_settings()` raises `ConfigurationError` immediately on startup rather than allowing the application to run in a partially-configured state.

**Deliberately did NOT implement:** Secrets management, remote configuration, or any dynamic config reloading. Simple layered file/env config is sufficient for the current phase.

**Validation:** All four gates pass.

---

### Sprint 3 — Structured Logging Framework

**Purpose:** Establish centralized, structured logging that every module can use without knowing how logging is configured. Logging must be set up once and be usable immediately everywhere.

**What was implemented:**
- `setup_logging(settings: LoggingSettings)` — configures the `"nikola"` root logger. Console handler always created; file handler optional via `LoggingSettings.file_path`.
- `get_logger(name: str)` — returns a standard `logging.Logger`. The established pattern is `get_logger(__name__)` at each call site.
- `TextFormatter`, `JsonFormatter`, `build_formatter()` — text for human-readable dev output; JSON for machine-readable production output.
- `LoggerPort` — `typing.Protocol` in `domain/ports/` defining the logger interface.
- `LoggingSettings` extended with `json_format`, `console_enabled`, `file_path`.

**Key design decisions:**
- **`get_logger(__name__)` at each call site** — not a single injected logger passed through constructors. This is idiomatic Python and avoids polluting every class constructor with a logger parameter.
- **`LoggingInitialized` marker singleton** (registered in Sprint 5's composition root) — since `setup_logging()` is void-returning, a frozen dataclass marker is registered in the DI container. Any service that must have logging available before starting can declare a dependency on this marker. This keeps logging initialization explicit and ordered.
- **JSON default** — production deployments get structured JSON logs; local development can set `json_format: false` in `.env`.

**Deliberately did NOT implement:** Distributed tracing, log aggregation, or structured correlation IDs. Simple structured logging is sufficient for the current phase.

**Validation:** All four gates pass.

---

### Sprint 4 — Domain Layer

**Purpose:** Build the core domain entities that model Nikola AI's fundamental concepts. The domain exists before any application logic and must remain independent of all infrastructure.

**What was implemented:**
- **Value Objects:** `CommandId`, `TaskId`, `SessionId` (frozen dataclasses, UUID-backed). `TaskStatus`, `CommandType`, `ResponseType` (StrEnums).
- **Entities:** `Command` (frozen), `Task` (mutable, state machine: `start()`, `complete()`, `fail()`, `cancel()`), `Response` (frozen), `Session` (mutable, accumulates Tasks).
- **Events:** `TaskStarted`, `TaskCompleted` (frozen dataclasses in `domain/events/`). Pre-declared for a future event bus; not yet connected to any bus.
- **Domain errors extended:** `InvalidCommandError`, `ToolUnavailableError`, `CommandExecutionError`.

**Key design decisions:**
- **Typed value objects over bare strings** — `TaskId` cannot be accidentally passed where `SessionId` is expected. MyPy catches this at compile time, eliminating an entire class of runtime bugs.
- **StrEnum for all enums** — values serialize cleanly to strings without `.value` access. `TaskStatus.PENDING == "pending"` is true. This simplifies logging, serialization, and comparisons throughout the codebase.
- **State machine on `Task`** — only valid transitions are allowed. Invalid transitions raise `PlanningError`. The entity itself enforces domain invariants, not callers.
- **`domain/events/` pre-declared** — events exist now but require a future event bus to be meaningful. They are defined in the domain layer because they represent domain-level facts.

**Deliberately did NOT implement:** Event bus, event handlers, or any infrastructure for events. The events are pure data definitions.

**Validation:** All four gates pass.

---

### Sprint 5 — Dependency Injection & Composition Root

**Purpose:** Build the DI container and the composition root that wires all layers together. Establish the pattern that every future sprint follows for registering new services.

**What was implemented:**
- `ServiceContainer` — `register_singleton()`, `register_factory()`, `register_transient()`, `resolve()`, `is_registered()`. Circular dependency detection via resolution stack. Constructor injection for `TRANSIENT` registrations via `get_type_hints()`.
- `ServiceLifetime` — `SINGLETON`, `FACTORY`, `TRANSIENT` (StrEnum).
- `ServiceDescriptor` — internal record per registration.
- `compose()` — the composition root. Registers `ConfigProviderPort` → `EnvConfigProvider` and `LoggingInitialized` → logging setup.
- `ServiceNotRegisteredError`, `CircularDependencyError` — new domain errors.

**Key design decisions:**
- **No third-party DI library** — a ~150-line hand-rolled container is fully auditable, has zero additional dependencies, and does exactly what Nikola needs. General-purpose DI frameworks solve problems Nikola doesn't have.
- **Abstract types as DI keys** — `container.resolve(ConfigProviderPort)` returns an `EnvConfigProvider` but callers see only `ConfigProviderPort`. This is a known MyPy false positive (`type-abstract`) documented with inline `# type: ignore[type-abstract]` comments explaining the pattern.
- **Lazy construction** — `compose()` only registers *how* to build services. Construction happens on first `resolve()`. This avoids forced registration ordering.
- **`compose()` returns a fresh container** — no global singleton container. Tests call `compose()` to get an isolated container.
- **`LoggingInitialized` marker** — since `setup_logging()` is void-returning, a typed frozen dataclass is returned from the singleton factory so other services can declare a typed dependency on "logging is initialized."

**Deliberately did NOT implement:** Brain, Planner, Memory, or any application services. This sprint is pure infrastructure wiring.

**Validation:** 236 tests pass. All four gates pass.

---

### Sprint 6 — Brain Abstraction

**Purpose:** Define the provider-agnostic reasoning interface, prove it works end-to-end with a deterministic no-network implementation, and register it in the composition root.

**What was implemented:**
- `BrainPort` — abstract domain port. Single method: `reason(request: ReasoningRequest) -> ReasoningResponse`. Plus `provider_name` abstract property.
- `ReasoningRequest` — frozen entity: `content`, `conversation_history` (tuple of `ConversationTurn`), `available_tools` (tuple of strings), `system_context`.
- `ReasoningResponse` — frozen entity: `content`, `intent`, `model_used`, `tool_name`, `tool_args`, `finish_reason`. Validates that `TOOL_INVOCATION` intent always has a `tool_name`.
- `ConversationTurn` — frozen entity: `role` ("user"/"assistant"/"tool"), `content`. Extended in Sprint 7 to accept "tool" as a valid role.
- `Intent`, `IntentType` (`CHAT`, `TOOL_INVOCATION`, `CLARIFICATION_NEEDED`, `OUT_OF_SCOPE`) — value objects with `confidence` ([0,1]) and optional `reasoning` string.
- `NullBrain` — fully functional `BrainPort`. Returns deterministic `ReasoningResponse` with `IntentType.CHAT` and content echoing the request. No network call, no API key.
- `BrainRegistry` — maps provider name strings to zero-argument factory callables that return `BrainPort` instances.
- `BrainFactory` — reads `BrainSettings.provider` from config, looks up the factory in `BrainRegistry`, returns the built Brain.
- `build_default_registry()` — returns a registry with only `"null"` registered.
- `BrainSettings` with `provider: str = "null"` added to `NikolaSettings`.
- `IntentClassifier` (abstract), `DefaultIntentClassifier` (delegates to `BrainPort.reason()`).
- `BrainError` — new domain error.
- `BrainPort` registered as singleton in `compose()`.

**Key design decisions:**
- **`NullBrain` is not a stub** — it is a working implementation that produces valid `ReasoningResponse` objects. Every downstream test that needs a Brain uses `NullBrain` and gets predictable results without mocks, network access, or API keys.
- **`ReasoningRequest` is structured, not a raw prompt string** — each Brain adapter is responsible for its own prompt engineering. The rest of the application never deals with prompts.
- **`BrainPort` in domain; concrete adapters in infrastructure** — adding a real AI provider requires one new file in `infrastructure/brains/` and one `registry.register()` call. Nothing else changes.
- **`IntentClassifier` in application, not domain** — classifying intent is use-case-level policy. The Planner and future Orchestrator depend on `IntentClassifier`, not `BrainPort`, keeping the reasoning boundary at the right abstraction level.

**Deliberately did NOT implement:** Any real AI provider adapter. `NullBrain` is the only Brain. Real adapters (Claude, OpenAI, Ollama) come in a future sprint once the full request pipeline exists.

**Validation:** 306 tests pass. All four gates pass.

---

### Sprint 7 — Conversation Layer

**Purpose:** Model the persistent, ordered record of an exchange between a user and Nikola AI. This is distinct from the transient per-Brain-call data shapes (`ReasoningRequest`/`ReasoningResponse`) built in Sprint 6.

**What was implemented:**
- `ConversationId`, `MessageId` — new typed value objects (frozen dataclasses, UUID-backed).
- `MessageRole` — `USER`, `ASSISTANT`, `SYSTEM`, `TOOL` (StrEnum).
- `ConversationStatus` — `ACTIVE`, `ARCHIVED`, `DELETED` (StrEnum).
- `Message` — frozen entity: `id`, `conversation_id`, `role`, `content`, `created_at`. Content must be non-empty.
- `Conversation` — mutable entity. Accumulates `Message` objects. Lifecycle: `archive()` (ACTIVE→ARCHIVED), `soft_delete()` (any→DELETED). `get_history_for_brain()` returns `tuple[ConversationTurn, ...]` excluding SYSTEM messages.
- `ConversationRepositoryPort` — abstract: `save()`, `get()`, `list_by_session()`, `delete()`.
- `InMemoryConversationRepository` — dict-backed implementation.
- `ConversationValidator` — stateless rule enforcement.
- `ConversationService` — CRUD and lifecycle use cases.
- `ConversationManager` — `get_or_create_active_conversation()`, role-specific message helpers, `get_brain_context()`.
- `ConversationError`, `MessageValidationError` — new domain errors.
- **`ConversationTurn.role` extended** to accept `"tool"` (previously only `"user"` or `"assistant"`).
- `ConversationRepositoryPort`, `ConversationService`, `ConversationManager` registered in `compose()`.

**Key design decisions:**
- **`Conversation` vs `ReasoningRequest`** — `Conversation` is the durable record (appended to over a session's lifetime). `ReasoningRequest` is a transient DTO built fresh for each Brain call from the conversation record. Different shapes, different lifetimes, different purposes.
- **SYSTEM messages excluded from `get_history_for_brain()`** — system context is injected as `ReasoningRequest.system_context`, mirroring the convention of all major LLM APIs where system prompts and user/assistant turns are separate inputs.
- **Soft-delete, not hard-delete** — `soft_delete()` sets status to DELETED; the record is retained. Physical deletion from the repository is the repository's `delete()` method.
- **`ConversationValidator` is stateless** — it holds no state and is independently testable. `ConversationService` delegates rule enforcement entirely to the validator.

**Deliberately did NOT implement:** Database persistence, conversation search, pagination, or any connection to the Brain or Planner layers. The conversation layer records what happened; it does not drive what happens.

**Validation:** 407 tests pass. All four gates pass.

---

### Sprint 8 — Memory Architecture

**Purpose:** Define how Nikola retains information across turns and sessions, with a cognitively-motivated four-type taxonomy, structured query filtering, and a pluggable retrieval ordering strategy.

**What was implemented:**
- `MemoryId` — typed value object.
- `MemoryType` — `WORKING`, `EPISODIC`, `SEMANTIC`, `PROCEDURAL` (StrEnum).
- `MemoryEntry` — mutable entity: `id`, `memory_type`, `content`, `created_at`, `updated_at`, `importance` (float [0,1]), `tags` (frozenset[str]), `metadata` (dict[str,object]). `strengthen(delta)` updates importance (clamped to [0,1]); `has_all_tags(required)` tests membership.
- `MemoryQuery` — frozen filter: `memory_types`, `tags`, `min_importance`, `created_after`, `created_before`, `limit`. All fields optional; empty query matches all.
- `MemoryResult` — frozen: `entries` (tuple), `total_found`, `query`.
- `MemoryRepositoryPort` — abstract: `save()`, `get()`, `search()`, `delete()`, `count()`.
- `InMemoryMemoryRepository` — dict-backed. `search()` applies all non-None query fields as AND conditions. Does NOT apply `limit` — that is the retrieval strategy's responsibility.
- `MemoryRetrievalStrategy` — abstract application-layer ordering policy.
- `ImportanceRetrievalStrategy` — sorts by `importance` descending, then `created_at` descending; then applies `query.limit`.
- `MemoryService` — `store()`, `retrieve()`, `get()`, `strengthen()`, `forget()`.
- `MemoryManager` — `remember_fact()` (SEMANTIC, default importance 0.6), `record_episode()` (EPISODIC, 0.5), `note_procedure()` (PROCEDURAL, 0.7), `set_working_memory()` (WORKING, 0.4), `recall()`, `strengthen()`, `forget()`.
- `MemoryError` — new domain error (distinct from Python's built-in `MemoryError`).
- 4 new singletons registered in `compose()`.

**Key design decisions:**
- **Repository filters; strategy orders** — `search()` returns the full unordered match set; `apply()` sorts and limits. These are independent, replaceable concerns. A future semantic relevance strategy can be plugged in without touching the repository.
- **`frozenset[str]` for tags** — immutable, hashable, supports `issubset()` for `has_all_tags()`.
- **AND semantics for tag queries** — `tags = frozenset({"python", "deployment"})` returns only entries that have BOTH. More precise than OR semantics for targeted recall.
- **Four memory types mirror cognitive science** — WORKING (temporary scratchpad), EPISODIC (timestamped event record), SEMANTIC (factual knowledge), PROCEDURAL (learned patterns). This taxonomy shapes how a future Orchestrator will query different types for different purposes.
- **`MemoryError` must be imported explicitly** — the name clashes with Python's built-in `MemoryError`. Tests verify the distinction.

**Deliberately did NOT implement:** Vector embeddings, semantic similarity search, vector store adapters, or any connection to the Brain for memory-augmented reasoning. The memory system stores and retrieves; augmenting Brain calls with memory is the future Orchestrator's responsibility.

**Validation:** 519 tests pass. All four gates pass.

---

### Sprint 9 — Planner Architecture

**Purpose:** Define how Nikola converts a goal into a structured execution plan. The Planner creates plans only — it does not execute them. A deterministic rule-based implementation proves the port contract without requiring any AI dependency.

**What was implemented:**
- `PlanId`, `StepId` — typed value objects.
- `PlanStatus` — `PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `CANCELLED` (StrEnum).
- `StepStatus` — `PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `SKIPPED` (StrEnum).
- `StepType` — `RESEARCH`, `CODE`, `SHELL`, `FILE`, `COMMUNICATION`, `REASONING`, `HUMAN_INPUT`, `GENERIC` (StrEnum).
- `PlanStep` — mutable entity: `id`, `title`, `description`, `order`, `step_type`, `status` (always PENDING at creation), `dependencies` (tuple of StepId), `estimated_duration_seconds`, `metadata`.
- `Plan` — mutable entity. Accumulates `PlanStep` objects sorted by `order`. Lifecycle: `start()` (PENDING→IN_PROGRESS, requires at least one step), `complete()` (IN_PROGRESS→COMPLETED), `fail(reason)` (IN_PROGRESS→FAILED, `reason` accepted but not yet stored — reserved for execution engine), `cancel()` (PENDING/IN_PROGRESS→CANCELLED). `is_terminal`, `pending_steps()`, `completed_steps()`, `estimated_duration_seconds` (sum or None).
- `PlanningRequest` — frozen: `goal` (non-empty), `context`, `constraints` (tuple of strings).
- `PlanningResult` — frozen: `plan`, `confidence` ([0,1]), `warnings`, `reasoning_summary`.
- `PlannerPort` — abstract: `plan(request) -> PlanningResult`, `planner_name` property.
- `RuleBasedPlanner` — implements `PlannerPort`. 8 keyword families: `python`, `flask`, `git`, `test`/`pytest` (deduplicated), `docker`, `deploy`, `api`. Emits fixed step sequences per match. Deduplicates steps by title across matched keywords. Confidence 1.0 for keyword match, 0.5 for generic fallback. Fully deterministic.
- `PlanningService` — `create_plan()`, `create_plan_for_goal()`, `active_planner_name`.
- `PlanningManager` — `plan_goal()`, `plan_goal_simple()`, `active_planner_name`.
- `PlanningError` — new domain error.
- 3 new singletons registered in `compose()`.

**Key design decisions:**
- **Planner creates, never executes** — `Plan` and `PlanStep` are pure data. The future Execution Engine reads `step.step_type` to dispatch each step. This separation allows plans to be reviewed and modified before any side-effecting action occurs.
- **`RuleBasedPlanner` is not a stub** — like `NullBrain`, it is a real working implementation that produces genuinely useful plans for recognized goals. It also proves the port contract without external dependencies.
- **`Plan.fail(reason)` reserves the parameter** — `_ = reason` documents that the parameter exists for the future Execution Engine which will pass failure messages. The API is forward-compatible.
- **`_S = dict[str, Any]`** — the step-definition rule table uses this typed alias. MyPy strict mode requires the explicit type parameter.
- **Step deduplication by title** — `"test"` and `"pytest"` keywords both match "run pytest tests" but produce only one "Set up test suite" step via the `seen_titles` set.

**Deliberately did NOT implement:** Step execution, tool invocation, plan storage/retrieval, plan modification after creation, or LLM-based planning. The Planner only creates; execution comes in a future sprint.

**Validation:** 619 tests pass. All four gates pass.

---

## 5. Currently Implemented Capabilities

These are capabilities that Nikola AI can actually exercise through the codebase after Sprint 9. All of these work without external services, API keys, or databases.

**Configuration:**
- Load configuration from `config/default.yaml`, `.env`, and environment variables in priority order.
- Validate configuration at startup with domain-level error reporting.
- Switch the active Brain provider via `NIKOLA_BRAIN__PROVIDER` environment variable (only `"null"` is currently registered).

**Logging:**
- Configure structured logging (JSON or text format) with optional file output.
- Use `get_logger(__name__)` anywhere in the codebase.

**Dependency Injection:**
- Register services with SINGLETON, FACTORY, or TRANSIENT lifetimes.
- Resolve services by port/class type.
- Detect circular dependencies at resolution time.
- Build a fully wired application via `compose()`.

**Conversation Management:**
- Create conversations for a session.
- Add USER, ASSISTANT, SYSTEM, and TOOL messages.
- Enforce conversation lifecycle (ACTIVE → ARCHIVED / DELETED).
- Retrieve conversation history formatted for a Brain call (`get_history_for_brain()`).
- Find or create the active conversation for a session (`get_or_create_active_conversation()`).
- Archive conversations.
- List active conversations for a session.

**Memory Storage and Retrieval:**
- Store memories as WORKING, EPISODIC, SEMANTIC, or PROCEDURAL types.
- Attach importance scores, tags, and metadata to memories.
- Query memories with structured filters (type, tags, minimum importance, time range, limit).
- Order results by importance then recency.
- Strengthen memory importance.
- Forget (delete) memories.
- High-level convenience API: `remember_fact()`, `record_episode()`, `note_procedure()`, `set_working_memory()`.

**Reasoning (via NullBrain):**
- Call `BrainPort.reason(request)` and receive a deterministic `ReasoningResponse`.
- Classify intent from a reasoning response.
- `NullBrain` always returns `IntentType.CHAT` with the request content echoed. This is the only Brain registered.

**Planning:**
- Create plans from goal strings via `PlanningManager.plan_goal()` or `plan_goal_simple()`.
- `RuleBasedPlanner` recognizes 8 keyword families and produces ordered, typed plan steps.
- Plans include confidence scores, warnings, and reasoning summaries.
- Plans support lifecycle transitions (`start()`, `complete()`, `fail()`, `cancel()`).
- Plans expose `pending_steps()`, `completed_steps()`, and `estimated_duration_seconds`.

---

## 6. Current Limitations

These are explicit limitations of the system as it exists after Sprint 9. Future sprints address them.

**No real AI reasoning:** `NullBrain` produces scripted, deterministic responses. There is no Claude, GPT, Gemini, or Ollama integration. Adding a real Brain adapter requires creating one new file in `infrastructure/brains/` and registering it — but this has not been done yet.

**No plan execution:** Plans are created but never executed. There is no Execution Engine, no step dispatch, no tool invocation. A plan is a data structure describing what should happen; nothing makes it happen.

**No tool system:** There is no Tool Registry, no tool discovery, no tool schema validation, and no tool invocation mechanism. `ReasoningRequest.available_tools` accepts strings but there are no real tools behind them.

**No data persistence:** All conversation and memory data lives in process memory (`InMemoryConversationRepository`, `InMemoryMemoryRepository`). Restarting the process loses all data. No SQLite, file, or vector store adapters are implemented.

**No Orchestrator:** The Conversation, Memory, Brain, and Planner layers are individually wired but not coordinated by a single component that handles a complete user request end-to-end. No component currently: receives user input → queries memory → calls the Brain → classifies intent → creates a plan → records the response.

**No permission system:** There is no risk classification, no approval workflow, and no gate controlling what Nikola is permitted to do. This is required before any real tool execution.

**Minimal CLI:** `nikola` prints a bootstrap confirmation and exits. There is no conversational interface, no REPL, no command dispatch.

**No scheduler:** No mechanism for recurring or time-triggered tasks.

**No event bus:** `domain/events/` defines `TaskStarted` and `TaskCompleted` as frozen dataclasses, but there is no bus to publish or subscribe to them.

**No voice, vision, or web interface:** These interface layers exist only as placeholder `__init__.py` stubs.

---

## 7. Dependency Rules

### What Each Layer May Import

| Layer | May import from |
|---|---|
| `domain/` | Python standard library only; other `domain/` subpackages |
| `application/` | Python standard library; `domain/` |
| `infrastructure/` | Python standard library; `domain/`; third-party libraries |
| `bootstrap/` | Everything (composition root only) |
| `interfaces/` | `bootstrap/`, `application/`, `domain/`; presentation libraries |
| `plugins/` | `domain/`; `infrastructure/` utilities (e.g. logging); third-party tool libraries |

### What Each Layer Must Never Import

- **`domain/`** — must never import from `application/`, `infrastructure/`, `bootstrap/`, `interfaces/`, or any third-party library.
- **`application/`** — must never import from `infrastructure/`, `bootstrap/`, or `interfaces/`. Must not make network calls, access the filesystem, or use third-party libraries for core logic.
- **`infrastructure/`** — must never import from `application/`, `bootstrap/`, or `interfaces/`.
- **`bootstrap/compose.py`** — must not contain business logic; only registrations.
- **`interfaces/`** — must not contain business logic.

### How Dependency Inversion Is Enforced

1. **`domain/ports/` defines the contract** — `BrainPort`, `PlannerPort`, `ConversationRepositoryPort`, `MemoryRepositoryPort` are ABCs with `@abstractmethod` declarations.
2. **`infrastructure/` implements the contracts** — `NullBrain`, `RuleBasedPlanner`, `InMemoryConversationRepository`, `InMemoryMemoryRepository` subclass the corresponding ports.
3. **`application/` depends on ports** — `ConversationService.__init__` takes `ConversationRepositoryPort`, not `InMemoryConversationRepository`.
4. **`bootstrap/compose.py` wires them** — the only place where abstract ports are connected to concrete implementations.
5. **MyPy strict mode enforces this** — if `application/` ever imports a concrete infrastructure class, MyPy will flag it.

---

## 8. Important Design Decisions

For each decision: what was decided, why, and what this means for future development.

---

### Decision: Brain Is Provider-Independent

**What:** `BrainPort` is an abstract domain port with one method. All Brain adapters implement it. No AI provider SDK is imported anywhere except in concrete Brain adapter files in `infrastructure/brains/`.

**Why:** The AI landscape changes rapidly. If core application logic imported Anthropic's SDK directly, switching providers would require rewriting conversation management, memory retrieval, and planning logic. Provider independence means switching from `NullBrain` to a real provider requires: one new file + one `registry.register()` call + one config change.

**Future implication:** Every real Brain adapter (`ClaudeBrainAdapter`, `OpenAIBrainAdapter`, `OllamaBrainAdapter`) must implement `BrainPort` and be registered in `build_default_registry()`. Application code must never import them directly.

---

### Decision: NullBrain Is a Working Implementation, Not a Stub

**What:** `NullBrain` returns valid, deterministic `ReasoningResponse` objects. It is not a stub that raises `NotImplementedError`. The entire test suite passes without any API key because of `NullBrain`.

**Why:** A stub that raises `NotImplementedError` forces every test involving the Brain to mock it. A working implementation means tests can use real dependency injection without any mock setup, and the system can be demonstrated and tested end-to-end without external services.

**Future implication:** When adding a real Brain adapter, `NullBrain` remains registered as `"null"` and continues to be the default for tests and CI. Real adapters are opt-in via the `brain.provider` configuration value.

---

### Decision: Planner Creates Plans; It Does Not Execute Them

**What:** `PlannerPort.plan()` returns a `PlanningResult` containing a `Plan` with ordered `PlanStep` objects. Nothing in the planning layer invokes tools, accesses the filesystem, or makes network calls.

**Why:** Plans are artifacts that can be reviewed, stored, resumed after interruption, and modified before execution begins. Mixing creation and execution in one component would make plans impossible to inspect before side effects occur and impossible to resume after a failure.

**Future implication:** A future Execution Engine reads a `Plan` and dispatches each step via `StepType` to the appropriate handler. The Planner never needs to know this is happening.

---

### Decision: RuleBasedPlanner Exists as a Real Implementation

**What:** `RuleBasedPlanner` recognizes 8 keyword families and produces genuinely useful, ordered plans. It is not a placeholder — it is a real implementation of `PlannerPort`.

**Why:** Like `NullBrain`, `RuleBasedPlanner` proves the port contract is implementable without external dependencies, enables CI testing without AI, and provides a genuine fallback for structured workflows where deterministic planning is more reliable than LLM-based planning.

**Future implication:** When an LLM-based planner is added, `RuleBasedPlanner` remains registered as `"rule_based"` and continues to be the default. LLM-based planning is opt-in via configuration.

---

### Decision: Repository Filters; Strategy Orders

**What:** `MemoryRepositoryPort.search()` applies all non-None query filters and returns the full unordered match set. It does NOT apply `query.limit`. `MemoryRetrievalStrategy.apply()` sorts results and applies the limit.

**Why:** These are independent, replaceable concerns. The repository should not need to know the desired ordering; the strategy should not need to re-implement filter logic. A future semantic relevance strategy can be plugged in alongside the importance strategy without touching the repository.

**Future implication:** Any new retrieval strategy implements `MemoryRetrievalStrategy` and is registered in `compose()`. The repository interface never changes to accommodate ordering preferences.

---

### Decision: Abstract Types as DI Keys With Documented `type-abstract` Suppressions

**What:** `container.register_singleton(ConfigProviderPort, ...)` uses an abstract class as a dictionary key. MyPy flags this as `type-abstract` (can't instantiate an ABC). All such usages in `compose.py` carry `# type: ignore[type-abstract]` with an inline explanation.

**Why:** Using the port as the key is the essential mechanism of dependency inversion. The container stores it as a dictionary key, not as something to instantiate. MyPy's warning is a known false positive for this DI pattern.

**Future implication:** Every new port registered in `compose.py` will carry the same documented suppression. Never suppress broadly with `# type: ignore` without specifying the error code and explaining why.

---

### Decision: `compose()` Returns a Fresh Container; No Global Singleton

**What:** `compose()` creates and returns a new `ServiceContainer` on every call. There is no module-level global container.

**Why:** A global container makes tests order-dependent and difficult to isolate. A factory function means each test or application startup gets a clean, independent container.

**Future implication:** Never add a module-level `_container` global. The entry point calls `compose()` once at startup; tests call `compose()` once per test that needs a container.

---

### Decision: All New Enums Are `StrEnum`

**What:** Every enum in the codebase subclasses `StrEnum`. `PlanStatus.PENDING == "pending"` is true.

**Why:** Values serialize cleanly to strings without `.value` access everywhere. This simplifies logging, serialization, comparison with string literals, and persistence.

**Future implication:** Every new enum must be a `StrEnum`. Do not use `IntEnum` or plain `Enum`.

---

### Decision: All New Typed IDs Are Frozen Dataclasses Wrapping UUID Strings

**What:** `PlanId`, `StepId`, `MemoryId`, etc., are all `@dataclass(frozen=True, slots=True)` with a `value: str` field, a `generate()` classmethod, and a `__str__` method.

**Why:** Typed IDs cannot be accidentally passed where a different ID type is expected. MyPy enforces this at compile time, eliminating an entire class of runtime bugs.

**Future implication:** Every new entity identifier must follow this pattern exactly. Do not use bare strings or `uuid.UUID` objects as IDs.

---

## 9. Coding Standards

These standards are established by the existing codebase. Future code must match them.

### Naming

- **Classes:** `PascalCase`. Ports: `*Port`. Repositories: `*Repository`. Services: `*Service`. Managers: `*Manager`. Strategies: `*Strategy`.
- **Methods:** `snake_case`. Factory classmethods: `create()` or `create_*()`. Lifecycle transitions: verb-named (`archive()`, `start()`, `fail()`). Boolean properties: `is_*` or `has_*`.
- **Value Object identifiers:** `*Id` suffix (`PlanId`, `StepId`).
- **Enums:** `PascalCase` class, `UPPER_SNAKE_CASE` members.
- **Private:** `_` prefix for internal attributes and methods. Unused-but-reserved parameters: `_ = param_name` with an inline comment.

### Type Hints

- All public functions and methods have complete type hints on all parameters and return values.
- `from __future__ import annotations` at the top of every module.
- `TYPE_CHECKING` blocks for annotation-only imports to avoid circular imports and reduce runtime import overhead.
- `frozenset[str]` for immutable tag collections. `tuple[T, ...]` for immutable ordered sequences. `dict[str, object]` for extensibility metadata.
- MyPy strict mode applied incrementally per sprint via `[[tool.mypy.overrides]]` in `pyproject.toml`.

### Documentation

- Every public class has a docstring: what it is, what it is responsible for, what it is NOT responsible for, key attributes, exceptions raised.
- Every public method has a docstring with `Args:`, `Returns:`, and `Raises:` sections.
- Non-obvious decisions explained with inline comments.
- Suppressions (`# type: ignore[specific]`, `# noqa: CODE`) always have inline explanations.

### Testing

- Tests mirror the `src/nikola/` structure under `tests/unit/`.
- Test files: `test_<module_name>.py`.
- Test classes: `Test<ClassOrConcept>`.
- Test methods: descriptive, e.g., `test_empty_goal_raises`.
- All test methods decorated with `@pytest.mark.unit`.
- No `unittest.mock.patch` on internal state — use dependency injection.
- Helper factory functions at module level, not inside test classes.

### Formatting

- Black enforces `line-length = 100`. Never argue with Black.
- Ruff enforces import organization (`I` rules), style (`E`/`W` rules), and type-checking block placement (`TC` rules).

### Adding New Modules — The Pattern

Every new module follows this sequence:

1. Domain errors (if new failure modes needed) → domain value objects → domain entities → domain ports
2. Application layer (services, managers, strategies)
3. Infrastructure layer (concrete implementations)
4. Bootstrap (`compose.py` registrations)
5. `__init__.py` updates for every new public symbol at each level
6. `pyproject.toml` MyPy override additions for new modules
7. Tests written for each layer as it is implemented

---

## 10. Testing Strategy

### Validation Gates

All four gates must pass before a sprint is considered complete:

1. **`nikola`** — the CLI entry point runs without error. Confirms the package is importable and `compose()` doesn't crash.
2. **`pytest`** — all tests pass with no skips.
3. **`ruff check .`** — zero lint errors. Auto-fixable issues fixed first; remaining addressed manually.
4. **`mypy src`** — zero type errors on source code under strict mode (for all modules that have been added to the strict override list).

`mypy tests` is also run and must pass, though it is not one of the four official gates.

### Clean-Room Verification

Before packaging each sprint deliverable, a clean-room verification is mandatory:
- Copy the project to a fresh directory.
- Create a fresh virtual environment.
- Install from scratch: `pip install -e ".[dev]"`.
- Run all four gates.

This catches issues that only manifest in a clean installation (missing exports in `__init__.py`, missing `pyproject.toml` entries, import paths that worked due to editor/IDE path manipulation).

### Coverage Philosophy

100% line and branch coverage is the expectation on all new modules. Tests cover all code paths explicitly. Coverage tooling confirms coverage; it does not drive what tests are written.

### Test Count After Sprint 9

The test suite contains **619 passing tests** after Sprint 9 (verified by running `pytest` against the Sprint 9 repository). This number must not decrease in future sprints.

### Why Regressions Must Be Prevented

Nikola AI is built across many separate sessions. There is no continuous state between sessions — each session starts from the latest sprint artifact. If Sprint N introduces a regression in Sprint N-3's DI container, and that regression is not caught by Sprint N's tests, it may not surface until Sprint N+5 — at which point diagnosis is much harder. Comprehensive tests on every sprint ensure each deliverable is a known-good artifact.

---

## 11. Development Workflow

Every sprint follows this workflow. The order is not optional.

```
Architecture Design
        ↓
Sprint Specification (what to implement, what NOT to implement)
        ↓
Implementation (in layer order: domain → application → infrastructure → bootstrap)
        ↓
Architecture Review (does the implementation match the design? layer violations? missing exports?)
        ↓
Unit Testing (tests written per layer as implementation proceeds)
        ↓
Static Analysis (Black → Ruff → MyPy — fix issues immediately, do not accumulate)
        ↓
Workspace Validation (run all four gates in the development environment)
        ↓
Merge (apply changes to the project working directory)
        ↓
Post-Merge Validation (run all four gates again after merge)
        ↓
Clean-Room Verification (fresh directory, fresh venv, install, run all four gates)
        ↓
Package (create sprint zip, excluding .venv, cache dirs, *.pyc)
```

**Why this order exists:** The architecture must be designed before code is written, or the implementation will diverge from the intended design. Tests must be written as each layer is implemented, not batched at the end. Static analysis must be run incrementally — accumulating 30 MyPy errors to fix at the end leads to suppressions that hide real problems. The clean-room verification is non-negotiable because it is the only way to confirm the artifact is self-contained.

---

## 12. Repository Organization

### Actual Directory Structure (Sprint 9 State)

```
nikola-ai/
├── config/
│   └── default.yaml              # Base configuration (checked into git, no secrets)
├── docs/                         # Architecture documentation
├── project_docs/
│   └── 10_DEVELOPER_HANDOFF.md  # This document
├── scripts/                      # Development utility scripts
├── src/
│   └── nikola/
│       ├── application/
│       │   ├── brain/            # IMPLEMENTED: IntentClassifier, DefaultIntentClassifier
│       │   ├── conversation/     # IMPLEMENTED: Validator, Service, Manager
│       │   ├── memory/           # IMPLEMENTED: Strategy, Service, Manager
│       │   ├── planner/          # IMPLEMENTED: PlanningService, PlanningManager
│       │   ├── agent/            # STUB ONLY — future
│       │   ├── orchestration/    # STUB ONLY — future
│       │   ├── permissions/      # STUB ONLY — future
│       │   ├── scheduler/        # STUB ONLY — future
│       │   └── tool_registry/    # STUB ONLY — future
│       ├── bootstrap/
│       │   ├── compose.py        # IMPLEMENTED: composition root, grows every sprint
│       │   └── container.py      # IMPLEMENTED: DI container (~150 lines, rarely changes)
│       ├── domain/
│       │   ├── entities/         # IMPLEMENTED: all entities listed in Section 3
│       │   ├── errors/           # IMPLEMENTED: full hierarchy under NikolaError
│       │   ├── events/           # IMPLEMENTED: TaskStarted, TaskCompleted (not yet connected to a bus)
│       │   ├── ports/            # IMPLEMENTED: all 6 ports listed in Section 3
│       │   └── value_objects/    # IMPLEMENTED: all value objects listed in Section 3
│       ├── infrastructure/
│       │   ├── brains/           # IMPLEMENTED: NullBrain, BrainRegistry, BrainFactory
│       │   ├── config/           # IMPLEMENTED: NikolaSettings, EnvConfigProvider
│       │   ├── logging/          # IMPLEMENTED: setup_logging, get_logger, formatters
│       │   ├── planners/         # IMPLEMENTED: RuleBasedPlanner
│       │   ├── persistence/
│       │   │   ├── in_memory/    # IMPLEMENTED: InMemoryConversationRepository, InMemoryMemoryRepository
│       │   │   ├── sqlite/       # STUB ONLY — future
│       │   │   ├── vector_store/ # STUB ONLY — future
│       │   │   └── file_store/   # STUB ONLY — future
│       │   ├── event_bus/        # STUB ONLY — future
│       │   └── scheduler/        # STUB ONLY — future
│       ├── interfaces/
│       │   ├── cli/              # IMPLEMENTED: main() prints bootstrap message and exits
│       │   ├── shared/           # STUB ONLY — future
│       │   ├── voice/            # STUB ONLY — future
│       │   └── web/              # STUB ONLY — future
│       └── plugins/
│           ├── base/             # STUB ONLY — future
│           ├── browser/          # STUB ONLY — future
│           ├── filesystem/       # STUB ONLY — future
│           ├── messaging/        # STUB ONLY — future
│           ├── system_info/      # STUB ONLY — future
│           ├── terminal/         # STUB ONLY — future
│           ├── vision/           # STUB ONLY — future
│           └── voice/            # STUB ONLY — future
├── tests/
│   └── unit/                     # Mirrors src/nikola/ structure
├── .env.example                  # Documents available environment variables
└── pyproject.toml                # Single source of truth for all tooling
```

### Where Future Modules Belong

- **New AI provider adapters** → `infrastructure/brains/<provider>_brain.py`
- **New planner implementations** → `infrastructure/planners/<name>_planner.py`
- **New persistence adapters** → `infrastructure/persistence/<engine>/<entity>_repository.py`
- **New tool implementations** → `infrastructure/tools/<category>/<tool>.py` and `plugins/<tool>/`
- **New application use cases** → `application/<domain_area>/<service_or_manager>.py`
- **New domain concepts** → `domain/entities/`, `domain/value_objects/`, `domain/ports/`, `domain/errors/`
- **New CLI commands** → `interfaces/cli/commands/`
- **New web endpoints** → `interfaces/web/routes/`

---

## 13. Future Development Roadmap

**IMPORTANT: Nothing in this section exists in the repository.** These are planned capabilities based on the project's architectural intent and the stub directories pre-declared in the repository. This roadmap describes direction, not current state.

The ordering reflects architectural dependencies: each capability requires what comes before it.

### Planned: Execution Engine

**What:** An `ExecutionEngine` application service that takes a `Plan` and executes its `PlanStep` objects one at a time by dispatching each step's `StepType` to the appropriate handler.

**Why next:** The Planner (Sprint 9) produces plans. An Execution Engine is the natural next step that makes plans actionable. Without it, plans are pure data with no effect.

**Requires:** A basic step handler registry to dispatch `StepType` to handlers. Even a minimal implementation with only `REASONING` and `GENERIC` steps would be useful.

### Planned: Tool Registry

**What:** A `ToolRegistry` that discovers, validates, and exposes tool plugins. Each plugin provides a manifest (name, description, parameter schema, required permissions) and an implementation. The registry maps tool names to handlers.

**Why after Execution Engine:** The Execution Engine needs concrete tools to invoke for step types like `SHELL`, `FILE`, `CODE`, and `COMMUNICATION`. The Tool Registry is what makes real tools available.

### Planned: Permission Gateway

**What:** A `PermissionGateway` that classifies actions by risk level and enforces approval requirements before any side-effecting action occurs. Human confirmation required for high-risk actions. Immutable audit trail.

**Why here:** Before the Execution Engine invokes real-world tools (write files, execute commands, send email), a control mechanism must prevent accidental or unauthorized actions.

### Planned: Real Brain Adapters

**What:** `ClaudeBrainAdapter`, `OpenAIBrainAdapter`, `OllamaBrainAdapter` — each implementing `BrainPort` by calling the respective provider's API. Registered in `build_default_registry()` alongside `NullBrain`.

**Why after execution infrastructure:** Real AI reasoning becomes meaningful once there is a complete pipeline to use it — Execution Engine, Tool Registry, and Permission Gateway. Before that, `NullBrain` is sufficient for testing everything else.

### Planned: Orchestrator

**What:** A top-level `OrchestratorService` (in `application/orchestration/`) that handles a complete user request: receive input → record in conversation → retrieve memories → reason with Brain → classify intent → plan if needed → execute plan → record outcome in memory → return response.

**Why here:** The individual components (Conversation, Memory, Brain, Planner, Execution Engine) exist or will exist independently. The Orchestrator is what coordinates them into a coherent request-handling flow.

### Planned: SQLite / Persistent Storage

**What:** `SqliteConversationRepository` and `SqliteMemoryRepository` implementing the existing repository ports, backed by SQLite. Swap into `compose()` to persist data across process restarts.

**Why:** In-memory repositories lose all data on restart. Persistent storage is required for any real-world use.

### Planned: Vector Store Adapter

**What:** A vector store-backed `MemoryRepositoryPort` implementation enabling semantic similarity search. Would work alongside or replace `InMemoryMemoryRepository`.

**Why:** Importance-based filtering is a useful baseline, but semantic similarity search (finding memories relevant to a new query) requires embedding-based retrieval. The `MemoryRepositoryPort` and `MemoryRetrievalStrategy` separation means this can be added without changing any application code.

### Planned: Scheduler

**What:** Recurring task execution. Allows Nikola to perform actions on a schedule (e.g. "every Monday morning, summarize my emails"). Would live in `application/scheduler/` and `infrastructure/scheduler/`.

### Planned: Event Bus

**What:** An internal pub/sub event bus connecting `domain/events/` (which pre-declares `TaskStarted`, `TaskCompleted`) to handlers in `infrastructure/event_bus/`. Enables decoupled, reactive component communication.

### Planned: Multi-Agent Orchestration

**What:** The ability to spawn specialist sub-agents (Coder, Researcher, etc.) as separate Nikola instances with scoped tool permissions, coordinated by a primary Orchestrator.

**Long-term vision.** Requires the full Orchestrator, Tool Registry, Permission Gateway, and Scheduler to be in place first.

### Planned: Voice Interface

**What:** Wake-word detection, speech-to-text, and text-to-speech. Implementation in `interfaces/voice/`.

**Long-term vision.**

### Planned: Web Interface

**What:** A FastAPI-based web API and WebSocket interface. Implementation in `interfaces/web/`.

### Planned: Vision

**What:** Screenshot capture, OCR, and visual understanding via a `VisionPort`.

**Long-term vision.**

---

## 14. Rules For Future Development

These rules exist because violations compound across sprints into architectural debt that cannot be undone without rewriting large portions of the system.

### Architecture Rules

1. **Never redesign previous architecture.** If a previous sprint's design has a limitation, extend it or add a new abstraction alongside it. Do not modify existing port interfaces, entity signatures, or service APIs in ways that break existing tests.

2. **Never bypass ports.** Application code must never import a concrete infrastructure class. If `ConversationService` needs to call `InMemoryConversationRepository` directly, the port must be extended first.

3. **Never import infrastructure from domain.** The domain layer must remain pure Python standard library. Any dependency on a third-party library in `domain/` is a design error.

4. **Never put business logic in `compose.py`.** The composition root registers services. It does not make decisions about how they behave.

5. **Never make `compose()` a global singleton.** It must return a fresh `ServiceContainer` on every call.

6. **Never hard-code provider details in application or domain.** AI provider names, model IDs, API keys, and endpoints belong in configuration or concrete infrastructure files only.

### Quality Rules

7. **Never reduce the test count.** Each sprint must maintain or increase the number of passing tests. Removing tests to pass the gate is strictly forbidden.

8. **Never merge code that fails any of the four gates.** All four (`nikola`, `pytest`, `ruff check .`, `mypy src`) must pass.

9. **Never suppress MyPy broadly.** Every `# type: ignore` must be `# type: ignore[specific-error]` with an inline explanation.

10. **Every public class must have a docstring. Every public method must have complete type hints.**

11. **100% coverage is the expectation, not a target.** If a line exists, it must be tested.

### Extension Rules

12. **Add by extension, not modification.** New Brain providers are new files, not modifications to `NullBrain`. New retrieval strategies are new files. New planner implementations are new files.

13. **Maintain backward compatibility.** Public APIs (method signatures, exception types, port interfaces) should not break existing callers. If a breaking change is truly necessary, document why and provide a migration path.

14. **Register new services in `compose()`, nowhere else.** The composition root is the complete map of how the application is wired.

### Style Rules

15. **Follow existing naming conventions.** New ports: `*Port`. Repositories: `*Repository`. Managers: `*Manager`. Services: `*Service`. Deviating requires a documented reason.

16. **Every new enum is a `StrEnum`.**

17. **Every new typed ID is a frozen dataclass with `value: str`, `generate()`, and `__str__`.**

18. **Maintain provider independence.** Memory, planning, reasoning, and tool invocation must remain swappable via configuration.

---

## 15. Guidance For Future Claude Conversations

This section is addressed directly to a future Claude session continuing Nikola AI development.

### Before Implementing Anything

1. **Read the repository.** The repository is the ground truth. If a class is not in the repository, it does not exist, no matter what any document says.

2. **Read `project_docs/`.** The handoff document and any other project documentation explain the architectural intent behind what exists.

3. **Read this Developer Handoff Document in full.** Understand both what exists and what was deliberately excluded from prior sprints.

4. **Run the four validation gates before touching anything.**
   ```bash
   nikola
   pytest
   ruff check .
   mypy src
   ```
   Confirm you are starting from a clean baseline. If any gate fails, diagnose and fix before adding new code.

5. **Identify the current sprint boundary.** The last completed sprint is Sprint 9. Do not assume that anything described in the roadmap (Execution Engine, Tool Registry, Orchestrator, etc.) has been implemented unless you can find it in the repository.

### How to Approach Future Sprints

**Design before coding.** Write out the full design before touching the codebase: what layer each new class belongs in, what port it implements, what pattern it follows. Catching design mistakes before they become code mistakes is essential.

**Implement in layer order.** Domain → Application → Infrastructure → Bootstrap. Never write application code that depends on an infrastructure class you haven't created yet.

**Use `TYPE_CHECKING` for annotation-only imports.** This avoids circular imports and keeps the runtime import graph clean. Look at existing code in the repository for the established pattern.

**Write tests as you implement each layer.** Do not batch all tests at the end. Tests for `Plan` should exist before tests for `PlanningService`.

**Run `ruff check .` and `mypy src` incrementally.** After implementing each layer, not at the very end. Accumulating errors leads to broad suppressions.

**Do a clean-room verification before presenting the deliverable.** Copy to a fresh directory, fresh venv, install from scratch, run all four gates.

### How to Preserve Architecture

The most common architectural violations are:

- **Importing infrastructure from application.** The pressure to "just use `InMemoryConversationRepository` directly" is real. Resist it. Use the port.
- **Putting logic in `compose.py`.** If you find an `if` statement in `compose.py` that is not about configuration-based adapter selection, that logic belongs in a service.
- **Forgetting `__init__.py` exports.** Every new public symbol must be exported from its package's `__init__.py`. Otherwise `from nikola.domain.ports import NewPort` will fail.
- **Forgetting MyPy strict overrides.** After adding new modules, add them to `[[tool.mypy.overrides]]` in `pyproject.toml` with `strict = true`.

### How to Distinguish Current From Future

The repository is divided into:

- **IMPLEMENTED:** has substantive Python files with real classes and tests.
- **STUB ONLY:** has only a placeholder `__init__.py` with a docstring saying "Implemented in later sprints."

If you look at `src/nikola/application/orchestration/__init__.py` and it contains only a docstring, the Orchestrator is not implemented. Do not describe it as existing. Do not build on top of it as if it exists.

**Stubs pre-declare the package structure; they are not implementations.**

### Critical Things to Remember

1. **619 tests must continue to pass after every change.** The test count must never go down.

2. **The domain layer is sacred.** It imports from nothing outside the Python standard library. Any third-party import in `domain/` is a design error.

3. **Each sprint deliverable must be self-contained.** The sprint zip must pass all four gates in a clean-room installation.

4. **Stub directories are not implemented features.** `application/orchestration/`, `infrastructure/event_bus/`, `plugins/browser/`, and all other stubs are placeholders only.

5. **NullBrain and RuleBasedPlanner are the only Brain and Planner implementations.** There are no real AI provider adapters and no LLM-based planner in the current repository.

6. **All data is in-memory.** There is no database, no file persistence, no vector store. Everything is lost on process restart.

7. **There is no Orchestrator.** The Conversation, Memory, Brain, and Planner layers are independently wired in `compose()` but nothing coordinates them into a complete request-handling flow.

8. **Read existing code before writing new code.** Every time. The established patterns are consistent and deliberate. The fastest way to introduce inconsistency is to write code without reading what is already there.

---

*End of Developer Handoff Document*

*When a new sprint is completed, update the following sections to reflect the new state:*
- *Section 4 (Sprint History) — add the new sprint*
- *Section 5 (Currently Implemented Capabilities) — add new capabilities*
- *Section 6 (Current Limitations) — remove limitations that have been addressed*
- *Section 12 (Repository Organization) — update STUB ONLY → IMPLEMENTED for newly built modules*
- *Section 13 (Future Roadmap) — move implemented items to Section 4*
