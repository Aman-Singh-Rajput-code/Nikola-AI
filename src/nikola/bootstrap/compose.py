"""Composition root. Sprint 11 adds ToolRegistryPort, ToolRegistryService, ToolRegistryManager."""

from __future__ import annotations

from dataclasses import dataclass

from nikola.bootstrap.container import ServiceContainer
from nikola.domain.ports import (
    BrainPort,
    ConfigProviderPort,
    ConversationRepositoryPort,
    MemoryRepositoryPort,
    PlannerPort,
    StepExecutorPort,
    ToolRegistryPort,
)
from nikola.infrastructure.brains import BrainFactory, build_default_registry
from nikola.infrastructure.config import EnvConfigProvider
from nikola.infrastructure.executors import DeterministicStepExecutor
from nikola.infrastructure.logging import get_logger, setup_logging
from nikola.infrastructure.persistence.in_memory import (
    InMemoryConversationRepository,
    InMemoryMemoryRepository,
)
from nikola.infrastructure.planners import RuleBasedPlanner
from nikola.infrastructure.tool_registry import InMemoryToolRegistry

__all__ = ["compose", "LoggingInitialized"]


@dataclass(frozen=True, slots=True)
class LoggingInitialized:
    """Marker returned once logging has been configured via setup_logging()."""


def compose() -> ServiceContainer:
    """Build and return a fully wired ServiceContainer for Nikola AI."""
    from nikola.application.conversation.conversation_manager import ConversationManager
    from nikola.application.conversation.conversation_service import ConversationService
    from nikola.application.execution.execution_engine import ExecutionEngine
    from nikola.application.execution.execution_manager import ExecutionManager
    from nikola.application.execution.execution_service import ExecutionService
    from nikola.application.memory.memory_manager import MemoryManager
    from nikola.application.memory.memory_retrieval_strategy import ImportanceRetrievalStrategy
    from nikola.application.memory.memory_service import MemoryService
    from nikola.application.planner.planning_manager import PlanningManager
    from nikola.application.planner.planning_service import PlanningService
    from nikola.application.tool_registry.tool_registry_manager import ToolRegistryManager
    from nikola.application.tool_registry.tool_registry_service import ToolRegistryService

    container = ServiceContainer()

    # --- Configuration ---
    container.register_singleton(
        ConfigProviderPort,  # type: ignore[type-abstract]
        factory=lambda _c: EnvConfigProvider(),
    )

    # --- Logging ---
    def _initialize_logging(c: ServiceContainer) -> LoggingInitialized:
        config_provider = c.resolve(ConfigProviderPort)  # type: ignore[type-abstract]
        settings = config_provider.get_settings()
        setup_logging(settings.logging)
        get_logger(__name__).info("Logging initialized via composition root.")
        return LoggingInitialized()

    container.register_singleton(LoggingInitialized, factory=_initialize_logging)

    # --- Brain ---
    def _build_brain(c: ServiceContainer) -> BrainPort:
        config_provider = c.resolve(ConfigProviderPort)  # type: ignore[type-abstract]
        settings = config_provider.get_settings()
        registry = build_default_registry()
        factory = BrainFactory(registry)
        brain = factory.create_from_settings(settings.brain)
        get_logger(__name__).info("Brain initialized.", extra={"provider": brain.provider_name})
        return brain

    container.register_singleton(BrainPort, factory=_build_brain)  # type: ignore[type-abstract]

    # --- Conversation ---
    container.register_singleton(
        ConversationRepositoryPort,  # type: ignore[type-abstract]
        factory=lambda _c: InMemoryConversationRepository(),
    )
    container.register_singleton(
        ConversationService,
        factory=lambda c: ConversationService(
            repository=c.resolve(ConversationRepositoryPort),  # type: ignore[type-abstract]
        ),
    )
    container.register_singleton(
        ConversationManager,
        factory=lambda c: ConversationManager(service=c.resolve(ConversationService)),
    )

    # --- Memory ---
    container.register_singleton(
        MemoryRepositoryPort,  # type: ignore[type-abstract]
        factory=lambda _c: InMemoryMemoryRepository(),
    )
    container.register_singleton(
        ImportanceRetrievalStrategy,
        factory=lambda _c: ImportanceRetrievalStrategy(),
    )
    container.register_singleton(
        MemoryService,
        factory=lambda c: MemoryService(
            repository=c.resolve(MemoryRepositoryPort),  # type: ignore[type-abstract]
            retrieval_strategy=c.resolve(ImportanceRetrievalStrategy),
        ),
    )
    container.register_singleton(
        MemoryManager,
        factory=lambda c: MemoryManager(service=c.resolve(MemoryService)),
    )

    # --- Planner ---
    container.register_singleton(
        PlannerPort,  # type: ignore[type-abstract]
        factory=lambda _c: RuleBasedPlanner(),
    )
    container.register_singleton(
        PlanningService,
        factory=lambda c: PlanningService(
            planner=c.resolve(PlannerPort),  # type: ignore[type-abstract]
        ),
    )
    container.register_singleton(
        PlanningManager,
        factory=lambda c: PlanningManager(service=c.resolve(PlanningService)),
    )

    # --- Execution ---
    container.register_singleton(
        StepExecutorPort,  # type: ignore[type-abstract]
        factory=lambda _c: DeterministicStepExecutor(),
    )
    container.register_singleton(
        ExecutionEngine,
        factory=lambda c: ExecutionEngine(
            step_executor=c.resolve(StepExecutorPort),  # type: ignore[type-abstract]
        ),
    )
    container.register_singleton(
        ExecutionService,
        factory=lambda c: ExecutionService(engine=c.resolve(ExecutionEngine)),
    )
    container.register_singleton(
        ExecutionManager,
        factory=lambda c: ExecutionManager(service=c.resolve(ExecutionService)),
    )

    # --- Tool Registry ---
    container.register_singleton(
        ToolRegistryPort,  # type: ignore[type-abstract]
        factory=lambda _c: InMemoryToolRegistry(),
    )
    container.register_singleton(
        ToolRegistryService,
        factory=lambda c: ToolRegistryService(
            registry=c.resolve(ToolRegistryPort),  # type: ignore[type-abstract]
        ),
    )
    container.register_singleton(
        ToolRegistryManager,
        factory=lambda c: ToolRegistryManager(service=c.resolve(ToolRegistryService)),
    )

    return container
