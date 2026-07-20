# Nikola AI Coding Standards

Version: 1.0

Status: Active

This document defines the official coding standards for Nikola AI.

Every contribution to the project must comply with these standards.

These rules exist to preserve maintainability, readability, consistency, and long-term scalability.

Violation of these standards should be considered a design issue rather than a style preference.

---

# 1. General Principles

Nikola prioritizes engineering quality over development speed.

Every implementation should be:

- Simple
- Readable
- Maintainable
- Testable
- Extensible
- Consistent

Code is expected to remain understandable years after it is written.

---

# 2. Clean Architecture

Every implementation must respect Clean Architecture.

Dependencies always point inward.

Allowed dependency direction:

Interfaces

↓

Bootstrap

↓

Infrastructure

↓

Application

↓

Domain

The Domain layer must never depend on outer layers.

---

# 3. Single Responsibility Principle

Every class should have one responsibility.

Avoid classes that perform multiple unrelated tasks.

Large classes should be split into smaller focused components.

---

# 4. Open/Closed Principle

Existing components should be extended through abstractions.

Avoid modifying stable implementations whenever possible.

New behavior should be added by introducing new implementations.

---

# 5. Dependency Injection

Never manually instantiate services.

Incorrect

service = MemoryService()

Correct

Resolve services through the Dependency Injection Container.

Every service should receive dependencies through its constructor.

---

# 6. Provider Independence

Business logic must never depend on:

- OpenAI
- Claude
- Gemini
- Ollama
- LangChain
- LlamaIndex

External providers belong exclusively to Infrastructure.

The Domain and Application layers should communicate only through ports.

---

# 7. Business Logic

Business logic belongs inside:

- Domain
- Application

Infrastructure should contain implementation details only.

---

# 8. Naming Conventions

Names should clearly describe responsibilities.

Classes

PascalCase

Examples

MemoryService

ConversationManager

BrainFactory

Methods

snake_case

Examples

remember()

retrieve()

classify_intent()

Variables

snake_case

Constants

UPPER_CASE

Files

snake_case.py

Package names

lowercase

---

# 9. File Organization

Each file should contain one primary responsibility.

Avoid large files containing unrelated classes.

Split files whenever responsibilities become unclear.

---

# 10. Class Design

Classes should:

- Be cohesive.
- Have minimal dependencies.
- Hide implementation details.
- Expose only necessary public APIs.

Avoid "God Classes."

---

# 11. Functions

Functions should:

- Perform one task.
- Be easy to understand.
- Return predictable results.
- Avoid unnecessary side effects.

Small functions are preferred.

---

# 12. Type Hints

Every public function must use type hints.

Avoid untyped public APIs.

Example

def retrieve(query: MemoryQuery) -> MemoryResult

Type safety is mandatory.

---

# 13. Docstrings

Public classes, methods and modules should include meaningful docstrings.

Docstrings should explain purpose rather than implementation.

---

# 14. Error Handling

Never ignore exceptions.

Raise meaningful domain-specific errors.

Avoid exposing infrastructure exceptions outside Infrastructure.

Convert external exceptions into Nikola errors.

---

# 15. Validation

Validate data as early as possible.

Invalid objects should never enter the Domain.

Prefer fail-fast validation.

---

# 16. Immutability

Use immutable value objects whenever practical.

Mutable state should exist only where necessary.

Immutable objects simplify reasoning and testing.

---

# 17. Domain Layer Rules

Domain may contain:

- Entities
- Value Objects
- Ports
- Domain Events
- Domain Errors

Domain must never contain:

- HTTP
- Databases
- AI SDKs
- Configuration loading
- Logging
- File system access

---

# 18. Application Layer Rules

Application coordinates business logic.

Application may:

- Call Domain
- Use Ports
- Coordinate workflows

Application must not:

- Call databases directly.
- Use AI SDKs directly.
- Perform infrastructure work.

---

# 19. Infrastructure Rules

Infrastructure implements ports.

Infrastructure may contain:

- API Clients
- Databases
- Logging
- Configuration
- AI Providers
- External SDKs

Infrastructure must never contain business rules.

---

# 20. Interfaces

Interfaces should remain thin.

They should:

- Accept input.
- Call Application.
- Return output.

Interfaces should not contain business logic.

---

# 21. Dependency Injection Rules

Every subsystem should register services through Bootstrap.

Avoid global state.

Avoid singleton implementations outside the DI Container.

---

# 22. Testing

Every sprint must include tests.

Required test categories:

- Domain Tests
- Application Tests
- Infrastructure Tests
- Bootstrap Tests

Every public API should have unit tests.

---

# 23. Test Isolation

Tests must remain independent.

Tests should never depend on:

- Internet
- APIs
- Databases
- Previous tests
- Execution order

Every test should be repeatable.

---

# 24. Code Duplication

Avoid duplicated logic.

Extract reusable behavior into shared components.

Copy-paste programming is prohibited.

---

# 25. Comments

Comments should explain why.

Code should explain how.

Avoid unnecessary comments.

Readable code is preferred over commented code.

---

# 26. Configuration

Never hardcode:

- API keys
- File paths
- URLs
- Secrets

Configuration belongs in the configuration system.

---

# 27. Public APIs

Public APIs should remain stable.

Breaking changes should be avoided whenever possible.

Future extensions should preserve backward compatibility.

---

# 28. Architecture Evolution

Architecture should evolve through extension.

Do not redesign completed systems without strong architectural justification.

Existing abstractions should be reused whenever possible.

---

# 29. Documentation

Every completed sprint must update:

- Current Status
- Sprint History
- Roadmap
- Next Sprint

Documentation is considered part of the implementation.

---

# 30. Code Review Checklist

Before merging code verify:

✓ Clean Architecture maintained

✓ SOLID principles respected

✓ Provider independence preserved

✓ Dependency Injection used correctly

✓ Type hints complete

✓ Ruff passes

✓ Black passes

✓ MyPy passes

✓ Pytest passes

✓ Documentation updated

✓ No unnecessary coupling introduced

✓ Public APIs remain consistent

---

# Final Principle

Nikola is a long-term engineering project.

Every contribution should make the architecture:

- Simpler
- Cleaner
- More maintainable
- More extensible

If an implementation achieves functionality but weakens the architecture, it should be reconsidered.

Architecture always takes precedence over convenience.