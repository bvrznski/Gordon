# Persistent Access - Phase 5.1.3 Canonical Long-Term Memory Access

"""
Persistent Access: Provides deterministic access to long-lived semantic information.

Supports:
    - Historical retrieval
    - Knowledge grounding
    - Identity continuity
    - Long-term planning
    - Semantic inspection

Persistent access never implies direct storage.
"""

from gordon_system.src.agent.components.systems.memory.access.session import (
    MemoryAccessSession,
)
from gordon_system.src.agent.components.systems.memory.access.request import (
    MemoryAccessRequest,
)
from gordon_system.src.agent.components.systems.memory.access.response import (
    MemoryAccessResponse,
)
from gordon_system.src.agent.components.systems.memory.access.publication import (
    PublicationResult,
)

__all__ = [
    "MemoryAccessSession",
    "MemoryAccessRequest",
    "MemoryAccessResponse",
    "PublicationResult",
]