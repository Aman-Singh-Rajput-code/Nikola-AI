# Nikola AI Development Workflow

Version: 1.0

Status: Active

This document defines the official development workflow for Nikola AI.

Every sprint, feature, bug fix, and architectural change must follow this workflow.

The objective is to ensure that Nikola evolves consistently while preserving architectural integrity, code quality, and long-term maintainability.

---

# Development Philosophy

Nikola is developed incrementally.

Development is organized into independent sprints.

Each sprint introduces one major subsystem or capability.

A sprint is considered complete only when it satisfies implementation, testing, documentation, and quality requirements.

Architecture always takes priority over development speed.

---

# Core Principles

Every development task should follow these principles:

- Build one subsystem at a time.
- Preserve Clean Architecture.
- Preserve provider independence.
- Extend existing architecture instead of redesigning it.
- Prefer abstractions before implementations.
- Write tests alongside production code.
- Keep documentation synchronized with implementation.

---

# Sprint Lifecycle

Every sprint follows the same lifecycle.

```
Understand
    ↓
Design
    ↓
Review Architecture
    ↓
Implement
    ↓
Write Tests
    ↓
Run Quality Checks
    ↓
Update Documentation
    ↓
Merge
```

No step should be skipped.

---

# Step 1 – Understand the Sprint

Before writing code:

Understand:

- Sprint objective
- Scope
- Responsibilities
- Dependencies
- Constraints
- Deliverables

Do not begin implementation until the objective is fully understood.

If requirements are ambiguous, resolve them before coding.

---

# Step 2 – Review Existing Architecture

Before introducing new code:

Review:

- Project Context
- Architecture
- Current Status
- Sprint History
- Coding Standards

Ensure the new subsystem integrates naturally with existing architecture.

Never introduce architectural shortcuts.

---

# Step 3 – Design Before Implementation

Every subsystem should be designed before implementation.

Design should identify:

- Domain objects
- Ports
- Services
- Repositories
- Managers
- Dependencies
- Error hierarchy

Implementation begins only after the design is logically consistent.

---

# Step 4 – Preserve Clean Architecture

During implementation verify:

- Dependencies point inward.
- Domain remains framework-independent.
- Infrastructure implements ports.
- Interfaces remain thin.
- Business logic stays inside Domain and Application.

Any violation should be corrected before continuing.

---

# Step 5 – Implement Incrementally

Build the subsystem in small, logical increments.

Recommended order:

1. Domain
2. Ports
3. Application
4. Infrastructure
5. Bootstrap
6. Interface Integration

Avoid implementing everything in a single step.

---

# Step 6 – Testing

Testing is mandatory.

Every public component should have unit tests.

Tests should verify:

- Success cases
- Failure cases
- Edge cases
- Validation
- Error handling

Tests must remain isolated.

No test should require:

- Internet
- External APIs
- Databases
- File system
- Previous test execution

---

# Step 7 – Quality Checks

Before completing a sprint, execute:

- Ruff
- Black
- MyPy
- Pytest

All checks must pass.

Warnings should be investigated rather than ignored.

---

# Step 8 – Documentation

Documentation is part of the implementation.

After every completed sprint update:

- Current Status
- Sprint History
- Roadmap (if required)

Documentation should accurately reflect the implemented state of the project.

Never document features that do not exist.

---

# Step 9 – Review

Before merging verify:

- Responsibilities are clearly separated.
- Public APIs are consistent.
- Naming follows project standards.
- Dependencies remain correct.
- No unnecessary complexity has been introduced.

The objective is clarity rather than cleverness.

---

# Definition of Done

A sprint is complete only when all of the following are true:

✓ Objective achieved

✓ Clean Architecture preserved

✓ Provider independence maintained

✓ Tests written

✓ Tests passing

✓ Ruff passing

✓ Black passing

✓ MyPy passing

✓ Documentation updated

✓ No known architectural regressions

Incomplete work should not be merged.

---

# Handling Bugs

When fixing bugs:

1. Understand the root cause.
2. Reproduce the issue.
3. Write or update a failing test.
4. Implement the fix.
5. Verify the fix.
6. Ensure no regressions.
7. Update documentation if behavior changes.

Avoid speculative fixes.

---

# Handling Refactoring

Refactoring should:

- Improve readability.
- Reduce complexity.
- Preserve behavior.
- Preserve public APIs whenever possible.

Avoid mixing refactoring with feature development unless necessary.

---

# Introducing New Features

Every new feature should answer:

- Does it belong in an existing subsystem?
- Does it require a new abstraction?
- Does it introduce unnecessary coupling?
- Can it be extended in the future?
- Does it preserve provider independence?

Architecture decisions should always precede implementation.

---

# Architectural Decision Rules

Before introducing a new class or subsystem, consider:

- Can an existing abstraction be reused?
- Does this violate the Single Responsibility Principle?
- Is this dependency pointing in the correct direction?
- Will this design still make sense after ten more sprints?

Avoid short-term optimizations that weaken long-term architecture.

---

# Working With AI Providers

AI providers are implementation details.

Never place provider-specific logic inside:

- Domain
- Application

Provider implementations belong only in Infrastructure.

Changing providers should never require business logic changes.

---

# Working With Storage

Storage implementations are interchangeable.

Business logic must not depend on:

- SQLite
- JSON
- Vector databases
- Cloud storage

Storage should always be accessed through repository ports.

---

# Working With Memory

Memory is independent from:

- Conversations
- AI providers
- Storage providers

Memory should expose clear abstractions.

Retrieval strategies should remain replaceable.

---

# Code Review Checklist

Before completing work verify:

✓ Responsibilities are clear

✓ Dependencies point inward

✓ Classes are cohesive

✓ Functions are small and focused

✓ Type hints are complete

✓ Public APIs documented

✓ Tests added

✓ Quality checks passing

✓ Documentation updated

---

# Common Mistakes to Avoid

Do not:

- Bypass abstractions.
- Add provider-specific logic to business layers.
- Mix responsibilities.
- Duplicate business logic.
- Introduce global state.
- Ignore failing tests.
- Hardcode configuration.
- Merge incomplete work.
- Document planned features as implemented.

---

# Collaboration Guidelines

When contributing to Nikola:

- Prioritize clarity over cleverness.
- Ask architectural questions before implementing.
- Prefer extension over replacement.
- Leave the codebase cleaner than it was found.

Every change should make the project easier to understand and easier to extend.

---

# Final Principle

Nikola is being built as a long-term engineering project.

Every sprint should strengthen the architecture.

Every implementation should preserve consistency.

Every contributor should think beyond the current sprint and build with future expansion in mind.