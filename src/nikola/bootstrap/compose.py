"""The composition root: builds a fully wired ServiceContainer for Nikola AI.

Sprint 5: config, logging. Sprint 6: BrainPort.
Sprint 7: ConversationRepositoryPort, ConversationService, ConversationManager.
"""

from __future__ import annotations

from dataclasses import dataclass

from nikola.bootstrap.container import ServiceContainer
from nikola.domain.ports import BrainPort, ConfigProviderPort, ConversationRepositoryPort
from nikola.infrastructure.brains import BrainFactory, build_default_registry
from nikola.infrastructure.config import EnvConfigProvider
from nikola.infrastructure.logging import get_logger, setup_logging
from nikola.infrastructure.persistence.in_memory import InMemoryConversationRepository

__all__ = ["compose", "LoggingInitialized"]


@dataclass(frozen=True, slots=True)
class LoggingInitialized:
    """Marker returned once logging has been configured via setup_logging()."""


def compose() -> ServiceContainer:
    """Build and return a fully wired ServiceContainer for Nikola AI.

    Registers as of Sprint 7:
    - ConfigProviderPort (singleton) -> EnvConfigProvider
    - LoggingInitialized (singleton) -> configures logging from config
    - BrainPort (singleton) -> AI reasoning backend from config (default: NullBrain)
    - ConversationRepositoryPort (singleton) -> InMemoryConversationRepository
    - ConversationService (singleton) -> wraps the conversation repository
    - ConversationManager (singleton) -> session-level coordinator
    """
    from nikola.application.conversation.conversation_manager import ConversationManager
    from nikola.application.conversation.conversation_service import ConversationService

    container = ServiceContainer()

    container.register_singleton(
        ConfigProviderPort,  # type: ignore[type-abstract]
        factory=lambda _c: EnvConfigProvider(),
    )

    def _initialize_logging(c: ServiceContainer) -> LoggingInitialized:
        config_provider = c.resolve(ConfigProviderPort)  # type: ignore[type-abstract]
        settings = config_provider.get_settings()
        setup_logging(settings.logging)
        get_logger(__name__).info("Logging initialized via composition root.")
        return LoggingInitialized()

    container.register_singleton(LoggingInitialized, factory=_initialize_logging)

    def _build_brain(c: ServiceContainer) -> BrainPort:
        config_provider = c.resolve(ConfigProviderPort)  # type: ignore[type-abstract]
        settings = config_provider.get_settings()
        registry = build_default_registry()
        factory = BrainFactory(registry)
        brain = factory.create_from_settings(settings.brain)
        get_logger(__name__).info(
            "Brain initialized.",
            extra={"provider": brain.provider_name},
        )
        return brain

    container.register_singleton(
        BrainPort,  # type: ignore[type-abstract]
        factory=_build_brain,
    )

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
        factory=lambda c: ConversationManager(
            service=c.resolve(ConversationService),
        ),
    )

    return container
