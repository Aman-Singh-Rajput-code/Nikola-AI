"""Abstract interfaces (ports) that the domain depends on and infrastructure implements.

Sprint 2 adds `ConfigProviderPort`. BrainPort, ToolPort, MemoryRepositoryPort,
and the rest are implemented in later sprints.
"""

from nikola.domain.ports.config_provider_port import ConfigProviderPort
from nikola.domain.ports.logger_port import LoggerPort

__all__ = [
    "ConfigProviderPort",
    "LoggerPort"
]
