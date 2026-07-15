"""Abstract interfaces (ports) that the domain depends on and infrastructure implements.

Sprint 2: ConfigProviderPort. Sprint 3: LoggerPort. Sprint 6: BrainPort.
Sprint 7: ConversationRepositoryPort.
"""

from nikola.domain.ports.brain_port import BrainPort
from nikola.domain.ports.config_provider_port import ConfigProviderPort
from nikola.domain.ports.conversation_repository_port import ConversationRepositoryPort
from nikola.domain.ports.logger_port import LoggerPort

__all__ = [
    "ConfigProviderPort",
    "LoggerPort",
    "BrainPort",
    "ConversationRepositoryPort",
]
