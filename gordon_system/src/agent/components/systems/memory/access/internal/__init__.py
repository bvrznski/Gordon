# Internal Access - Phase 5.1.3 Canonical Internal Memory Access

"""
Internal Access: Exposes Memory to Gordon's internal cognitive architecture.

Consumers include:
    - Reasoning
    - Planning
    - Knowledge
    - Workspace
    - Identity
    - Learning
    - Coordination
    - Governance

Internal access never bypasses Memory contracts.
"""

from gordon_system.src.agent.components.systems.memory.access.session import (
    MemoryAccessSession,
)
from gordon_system.src.agent.components.systems.memory.access.request import (
    MemoryAccessRequest,
    ProjectionType,
)
from gordon_system.src.agent.components.systems.memory.access.response import (
    MemoryAccessResponse,
)
from gordon_system.src.agent.components.systems.memory.access.authorization import (
    AuthorizationDecision,
)
from gordon_system.src.agent.components.systems.memory.access.visibility import (
    VisibilityResult,
)
from gordon_system.src.agent.components.systems.memory.access.publication import (
    PublicationResult,
)

# Engine classes
from gordon_system.src.agent.components.systems.memory.access.internal.engine import (
    InternalAccessEngine,
)

__all__ = [
    "MemoryAccessSession",
    "MemoryAccessRequest",
    "ProjectionType",
    "MemoryAccessResponse",
    "AuthorizationDecision",
    "VisibilityResult",
    "PublicationResult",
    "InternalAccessEngine",
]