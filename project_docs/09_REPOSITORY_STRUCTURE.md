# Nikola AI Repository Structure

Version: 1.0

Status: Active

This document defines the official repository structure for Nikola AI.

Every file and directory in the project should have a clearly defined purpose.

A directory should never become a general dumping location for unrelated files.

---

# Repository Overview

```
nikola/

├── docs/
├── project_docs/
├── src/
├── tests/
├── scripts/
├── examples/
├── configs/
├── .github/
├── pyproject.toml
├── README.md
└── LICENSE
```

The repository is organized into logical areas with well-defined responsibilities.

---

# Root Directory

The root directory contains only project-level files.

Examples:

- README.md
- LICENSE
- pyproject.toml
- .gitignore
- requirements
- development configuration

Business logic should never exist in the root directory.

---

# src/

Purpose

Contains the complete Nikola source code.

Nothing outside `src/` should contain production application logic.

```
src/

nikola/

bootstrap/

domain/

application/

infrastructure/

interfaces/

plugins/
```

---

# bootstrap/

Purpose

Application startup and dependency composition.

Contains:

- Dependency Injection Container
- Service registration
- Startup initialization
- Configuration loading
- Logger initialization

Bootstrap knows every subsystem.

No other layer should.

---

# domain/

Purpose

Business rules.

Contains:

- Entities
- Value Objects
- Domain Events
- Domain Errors
- Ports
- Business Rules

Must remain independent from infrastructure.

---

# application/

Purpose

Application orchestration.

Contains:

- Use Cases
- Services
- Managers
- Coordinators
- Validation

Application coordinates work.

It does not implement infrastructure.

---

# infrastructure/

Purpose

Concrete implementations.

Contains:

- AI Providers
- Memory Providers
- Repository Implementations
- Logging
- Configuration
- External APIs
- Storage

Infrastructure implements ports defined by the Domain.

---

# interfaces/

Purpose

Entry points into Nikola.

Examples:

- CLI
- REST API
- Desktop UI
- Web API
- Future Voice Interface

Interfaces should remain thin.

Business logic belongs elsewhere.

---

# plugins/

Purpose

Optional extensions.

Examples:

- Browser Plugin
- Git Plugin
- Filesystem Plugin
- Calendar Plugin
- Email Plugin

Plugins communicate through stable interfaces.

Core architecture should never depend on plugins.

---

# tests/

Purpose

Project test suite.

Example structure:

tests/

unit/

integration/

fixtures/

mocks/

helpers/

Tests should mirror the production structure where practical.

---

# docs/

Purpose

User-facing documentation.

Examples:

- Installation
- Usage
- Tutorials
- API documentation

This directory is intended for project users.

---

# project_docs/

Purpose

Internal engineering documentation.

Examples:

- Architecture
- Coding Standards
- Sprint History
- Roadmap
- Development Workflow

This directory is intended for contributors and AI-assisted development.

---

# configs/

Purpose

Configuration templates.

Examples:

- YAML files
- Default settings
- Example configuration

Secrets must never be committed.

---

# scripts/

Purpose

Development utilities.

Examples:

- Code generation
- Release scripts
- Development helpers
- Migration tools

Scripts should not contain business logic.

---

# examples/

Purpose

Example applications.

Examples:

- CLI examples
- Memory examples
- Plugin examples

Examples demonstrate usage without becoming part of the core application.

---

# .github/

Purpose

Repository automation.

Examples:

- GitHub Actions
- Issue Templates
- Pull Request Templates
- Workflows

Continuous Integration belongs here.

---

# Directory Ownership

| Directory | Responsibility |
|-----------|----------------|
| src | Production code |
| tests | Testing |
| docs | User documentation |
| project_docs | Engineering documentation |
| configs | Configuration templates |
| scripts | Development utilities |
| examples | Sample implementations |
| .github | Repository automation |

---

# Rules

- Every directory has one responsibility.
- Avoid circular dependencies between packages.
- New modules should be added to the correct architectural layer.
- Utility code should not become a dumping ground.
- Keep the repository easy to navigate.

---

# Future Growth

As Nikola evolves, new directories may be introduced.

However, the existing architectural layers should remain stable.

Repository growth should occur through extension rather than restructuring.

---

# Summary

A predictable repository structure improves:

- Readability
- Navigation
- Maintainability
- Onboarding
- Collaboration

Every contributor should understand where new code belongs before implementing it.