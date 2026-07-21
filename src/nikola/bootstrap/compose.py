"""The composition root: builds a fully wired ServiceContainer for Nikola AI.

Sprint 5: config, logging. Sprint 6: BrainPort.
Sprint 7: ConversationRepositoryPort, ConversationService, ConversationManager.
Sprint 8: MemoryRepositoryPort, MemoryService, MemoryManager.
"""

from __future__ import annotations

from dataclasses import dataclass

from nikola.bootstrap.container import ServiceContainer
from nikola.domain.ports import (
    BrainPort,
    ConfigProviderPort,
    ConversationRepositoryPort,
    MemoryRepositoryPort,
)
from nikola.infrastructure.brains import BrainFactory, build_default_registry
from nikola.infrastructure.config import EnvConfigProvider
from nikola.infrastructure.logging import get_logger, setup_logging
from nikola.infrastructure.persistence.in_memory import (
    InMemoryConversationRepository,
    InMemoryMemoryRepository,
)

__all__ = ["compose", "LoggingInitialized"]


@dataclass(frozen=True, slots=True)
class LoggingInitialized:
    """Marker returned once logging has been configured via setup_logging()."""


def compose() -> ServiceContainer:
    """Build and return a fully wired ServiceContainer for Nikola AI.

    Registers as of Sprint 8:
    - ConfigProviderPort          -> EnvConfigProvider
    - LoggingInitialized          -> configures logging from config
    - BrainPort                   -> AI reasoning backend (default: NullBrain)
    - ConversationRepositoryPort  -> InMemoryConversationRepository
    - ConversationService         -> wraps the conversation repository
    - ConversationManager         -> session-level coordinator
    - MemoryRepositoryPort        -> InMemoryMemoryRepository
    - ImportanceRetrievalStrategy -> importance-then-recency ordering
    - MemoryService               -> store, retrieve, strengthen, forget
    - MemoryManager               -> type-specific convenience API
    """
    from nikola.application.conversation.conversation_manager import ConversationManager
    from nikola.application.conversation.conversation_service import ConversationService
    from nikola.application.memory.memory_manager import MemoryManager
    from nikola.application.memory.memory_retrieval_strategy import (
        ImportanceRetrievalStrategy,
    )
    from nikola.application.memory.memory_service import MemoryService

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

    container.register_singleton(
        BrainPort,  # type: ignore[type-abstract]
        factory=_build_brain,
    )

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

    return container
