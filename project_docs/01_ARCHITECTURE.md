# Nikola AI Architecture Specification

Version: 1.0

Status: Active

This document defines the official architecture of Nikola AI. Every subsystem, sprint, feature, and future enhancement must comply with the architectural principles described here.

This document is considered the single source of truth for Nikola's architecture.

---

# 1. Architecture Overview

Nikola AI is designed as a modular, provider-independent AI Operating System built using Clean Architecture, Domain-Driven Design (DDD), SOLID principles, and Dependency Injection.

The system is intentionally divided into independent subsystems. Every subsystem has a single responsibility and communicates only through well-defined abstractions.

The primary architectural goal is long-term maintainability.

Every implementation decision should optimize for extensibility rather than short-term development speed.

---

# 2. Architectural Principles

Nikola follows the following principles throughout the entire project.

## Clean Architecture

Business logic must remain independent of frameworks, databases, APIs, SDKs, AI providers, operating systems, and external services.

Dependencies always point inward.

Outer layers may depend on inner layers.

Inner layers must never depend on outer layers.

---

## Domain Driven Design

Business concepts are represented as domain objects.

The domain should describe what Nikola is capable of doing rather than how those capabilities are implemented.

The domain contains:

- Entities
- Value Objects
- Ports
- Domain Errors
- Domain Events

The domain never imports infrastructure code.

---

## Dependency Injection

Every service is created by the Dependency Injection Container.

No class should manually instantiate another service.

The Bootstrap layer is responsible for wiring the complete application.

---

## Provider Independence

Nikola must never depend directly on:

- OpenAI
- Claude
- Gemini
- Ollama
- Any future LLM

Every provider must implement an abstract port.

Replacing providers must require changing configuration only.

---

## Testability

Every subsystem must be testable in complete isolation.

Business logic should never require:

- Internet
- APIs
- Databases
- File system
- External services

Unit tests should execute using only in-memory implementations.

---

# 3. Layered Architecture

Nikola consists of six primary layers.

```
Interfaces
      ↓
Bootstrap
      ↓
Infrastructure
      ↓
Application
      ↓
Domain
```

Dependencies always move downward.

The Domain layer never depends on any outer layer.

---

# 4. Layer Responsibilities

## Domain

The Domain layer represents Nikola's business rules.

Responsibilities:

- Entities
- Value Objects
- Domain Events
- Domain Errors
- Ports
- Business Rules

The Domain layer must contain no infrastructure code.

Allowed imports:

- Python Standard Library

Forbidden:

- Requests
- HTTP Clients
- AI SDKs
- Databases
- File System
- Frameworks

---

## Application

The Application layer coordinates business logic.

Responsibilities:

- Use Cases
- Managers
- Services
- Validation
- Workflow Coordination

The Application layer orchestrates the Domain.

It never performs infrastructure work directly.

---

## Infrastructure

Infrastructure contains concrete implementations.

Examples:

- AI Providers
- Logging
- Configuration
- Persistence
- External APIs

Infrastructure implements the ports defined by the Domain.

Infrastructure may use third-party libraries.

---

## Bootstrap

Bootstrap is the composition root.

Responsibilities:

- Dependency Injection
- Service Registration
- Configuration Loading
- Logger Initialization
- Provider Registration

Bootstrap is the only layer allowed to know every subsystem.

---

## Interfaces

Interfaces expose Nikola to users.

Examples:

- CLI
- REST API
- Desktop UI
- Voice Interface
- Future Web Interface

Interfaces should contain no business logic.

---

# 5. Dependency Rule

Dependencies must always point inward.

Correct:

Interface

↓

Bootstrap

↓

Infrastructure

↓

Application

↓

Domain

Incorrect:

Domain

↓

Infrastructure

This dependency is never allowed.

---

# 6. Project Structure

src/

nikola/

domain/

application/

infrastructure/

bootstrap/

interfaces/

plugins/

tests/

Each directory has one responsibility.

No folder should become a dumping ground.

---

# 7. Current Architecture

The following subsystems have been completed.

## Bootstrap

Responsible for application startup.

Responsibilities:

- Initialize configuration
- Initialize logging
- Register services
- Build Dependency Injection Container

---

## Configuration

Loads configuration from multiple sources.

Priority:

Environment Variables

↓

.env

↓

YAML

↓

Default Values

Configuration validation happens during startup.

Startup should fail immediately if configuration is invalid.

---

## Logging

Provides structured logging.

Supports:

- Console logging
- JSON logging

Logging is initialized once during startup.

No subsystem should configure logging independently.

---

## Domain

Current domain contains:

- Command
- Task
- Session
- Response

Value Objects

Domain Events

Domain Errors

Ports

---

## Dependency Injection

All services are resolved through ServiceContainer.

Supported lifetimes:

- Singleton
- Factory
- Transient

The container detects circular dependencies.

---

## Brain

The Brain subsystem is responsible for reasoning.

Responsibilities:

- Intent Classification
- Prompt Construction
- Response Generation

The Brain never stores conversations.

The Brain never stores memory.

The Brain never accesses infrastructure directly.

Current implementation:

NullBrain

Future implementations:

OpenAI

Claude

Gemini

Ollama

Local Models

---

## Conversation

Conversation is responsible for message history.

Responsibilities:

- Store conversation messages
- Validate messages
- Retrieve history
- Manage sessions

Conversation owns history.

Conversation does not own memory.

Conversation does not perform reasoning.

---

# 8. Planned Architecture

The following subsystems are planned.

Their exact implementation may evolve, but their responsibilities are fixed.

---

## Memory

Purpose:

Provide Nikola with persistent knowledge.

Responsibilities:

- Store memories
- Retrieve memories
- Categorize memories
- Support future retrieval strategies

Memory is provider independent.

Memory exists independently of conversations.

Future implementations:

- InMemory
- SQLite
- JSON
- Vector Database
- Cloud Storage

---

## Context Manager

Purpose:

Prepare context before reasoning.

Responsibilities:

- Collect conversation history
- Retrieve relevant memories
- Merge current task state
- Produce reasoning context

The Brain receives prepared context.

The Brain never assembles context itself.

---

## Planner

Purpose:

Convert goals into executable plans.

Responsibilities:

- Task decomposition
- Planning
- Dependency ordering

The Planner never executes tasks.

---

## Execution Engine

Purpose:

Execute plans.

Responsibilities:

- Execute tools
- Track execution
- Handle failures
- Retry operations

---

## Tool Registry

Purpose:

Manage external capabilities.

Examples:

Filesystem

Terminal

Browser

Git

Email

Calendar

Vision

OCR

Voice

Plugins

---

## Plugin System

Purpose:

Allow external capabilities without modifying Nikola core.

Plugins communicate through defined interfaces.

Plugins never modify domain logic.

---

# 9. Communication Flow

High-level request lifecycle.

User

↓

Interface

↓

Conversation

↓

Memory

↓

Context Manager

↓

Brain

↓

Planner

↓

Execution Engine

↓

Tool Registry

↓

Response

Some components are planned and will be introduced in future sprints.

---

# 10. Architectural Constraints

The following rules are mandatory.

- Never bypass abstractions.
- Never access infrastructure from the Domain.
- Never create circular dependencies.
- Never couple providers to business logic.
- Never instantiate services manually.
- Never expose infrastructure classes to interfaces.
- Never duplicate business logic across layers.

---

# 11. Extensibility

Every subsystem should be replaceable.

Future additions should require implementing new adapters rather than modifying existing code.

Examples:

New AI Provider

↓

Implement BrainPort

New Memory Backend

↓

Implement MemoryPort

New Tool

↓

Implement Tool Interface

Core architecture should remain unchanged.

---

# 12. Architecture Evolution

Nikola is expected to evolve through many future sprints.

Architecture should grow through extension rather than redesign.

Whenever possible:

- Add new implementations.
- Add new adapters.
- Add new strategies.

Avoid modifying stable public APIs.

---

# 13. Summary

Nikola AI is designed as a long-term engineering project.

Every subsystem is developed independently.

Every dependency flows inward.

Every implementation remains replaceable.

The architecture prioritizes:

- Maintainability
- Extensibility
- Testability
- Provider Independence
- Long-term scalability

All future development should preserve these principles.