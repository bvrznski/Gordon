# Transient Access - Phase 5.1.3 Canonical Short-Term Memory Access

"""
Transient Access: Exposes temporary cognitive views for active processing.

Supports:
    - Working memory operations
    - Active dialogue
    - Reasoning
    - Planning
    - Simulation
    - Execution

Transient access expires naturally. Persistent Memory remains unchanged.
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