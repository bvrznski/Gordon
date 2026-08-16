# External Access - Phase 5.1.3 Canonical External Memory Access

"""
External Access: Exposes Memory beyond Gordon's architecture.

Consumers include:
    - REST API endpoints
    - RPC interfaces
    - Plugins
    - Distributed agents
    - Persistence connectors
    - Monitoring tools
    - Human interfaces

External access always operates through projections.
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