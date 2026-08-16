# Memory Access - Phase 5.1.3 Canonical Memory Visibility Layer

"""
Memory Access: The architectural layer responsible for controlling visibility,
availability, authorization, projection, and publication of Memory.

Access governs visibility - not ownership. Not transformation.
"""

# =============================================================================
# SHARED CONTRACTS
# =============================================================================

from gordon_system.src.agent.components.systems.memory.access.session import (
    MemoryAccessSession,
    AccessPermission,
    MemoryAccessSessionFactory,
)

from gordon_system.src.agent.components.systems.memory.access.request import (
    MemoryAccessRequest,
    ProjectionType,
    MemoryAccessRequestBuilder,
)

from gordon_system.src.agent.components.systems.memory.access.response import (
    MemoryAccessResponse,
    AuthorizationOutcome,
    MemoryAccessResponseBuilder,
)

# =============================================================================
# ACCESS ENGINE COMPONENTS
# =============================================================================

from gordon_system.src.agent.components.systems.memory.access.authorization import (
    AuthorizationPolicy,
    PolicyRule,
    PolicyAction,
    MemoryAuthorizer,
    AuthorizationDecision,
)

from gordon_system.src.agent.components.systems.memory.access.visibility import (
    VisibilityFilter,
    VisibilityPolicy,
    VisibilityFilterKind,
    MemoryVisibilityEngine,
    VisibilityResult,
)

from gordon_system.src.agent.components.systems.memory.access.publication import (
    PublicationFormat,
    PublicationResult,
    MemoryPublisher,
)

# =============================================================================
# ACCESS DOMAINS
# =============================================================================

from gordon_system.src.agent.components.systems.memory.access.internal import (
    InternalAccessEngine,
)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Shared contracts
    "MemoryAccessSession",
    "AccessPermission",
    "MemoryAccessSessionFactory",
    "MemoryAccessRequest",
    "ProjectionType",
    "MemoryAccessRequestBuilder",
    "MemoryAccessResponse",
    "AuthorizationOutcome",
    "MemoryAccessResponseBuilder",
    # Engine components
    "AuthorizationPolicy",
    "PolicyRule",
    "PolicyAction",
    "MemoryAuthorizer",
    "AuthorizationDecision",
    "VisibilityFilter",
    "VisibilityPolicy",
    "VisibilityFilterKind",
    "MemoryVisibilityEngine",
    "VisibilityResult",
    "PublicationFormat",
    "PublicationResult",
    "MemoryPublisher",
    # Access domains
    "InternalAccessEngine",
]