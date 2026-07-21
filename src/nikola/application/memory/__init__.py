"""Memory use-case layer.

Sprint 8 delivers:
- `MemoryRetrievalStrategy` — abstract ordering/limiting policy.
- `ImportanceRetrievalStrategy` — orders by importance desc, recency desc.
- `MemoryService` — primary use-case: store, retrieve, strengthen, forget.
- `MemoryManager` — high-level coordinator with type-specific convenience methods.
"""

from nikola.application.memory.memory_manager import MemoryManager
from nikola.application.memory.memory_retrieval_strategy import (
    ImportanceRetrievalStrategy,
    MemoryRetrievalStrategy,
)
from nikola.application.memory.memory_service import MemoryService

__all__ = [
    "MemoryRetrievalStrategy",
    "ImportanceRetrievalStrategy",
    "MemoryService",
    "MemoryManager",
]
