# Oriented Network Package
# ========================

"""
OrientedNetwork - Gordon's intentional orientation coordination network.

Canonical Definition:
    The OrientedNetwork is Gordon's cognitive coordination network responsible
    for maintaining persistent intentional orientation toward active Goals,
    objectives, tasks, constraints, missions, and externally directed cognition.
    
    It coordinates independent cognitive capabilities while preserving strict
    ownership boundaries. The subsystem maintains semantic orientation without
    owning the cognitive algorithms themselves.

Architectural Role:
    Cognitive Network Layer - Intentional Orientation Coordination

Public API (Phase 4.7.1):
    - OrientedNetwork: Canonical network facade entry point
    - BaseOrientedNetwork: Abstract base for canonical implementation
    - OrientedNetworkState: Immutable state container
    - OrientedNetworkConfiguration: Immutable configuration
    - OrientedNetworkError: Root error type

Computational State (Phase 4.7.x):
    - OrientationIdentity: Unique network identity
    - OrientationContext: Current orientation context
    - OrientationState: Complete bounded computational state
    
This package does NOT:
    - Implement cognitive capability algorithms (deferred to future phases)
    - Execute runtime scheduling or coordination (owned by Core)
    - Own planning, reasoning, decision formation (separate subsystems)
    - Maintain working memory or workspace (separate subsystems)
"""

from __future__ import annotations

# =============================================================================
# CANONICAL METADATA
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.__meta__ import (
    __version__,
)

# =============================================================================
# PHASE 4.7.1: Canonical Scaffold - Public API
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.configuration import (
    OrientedNetworkConfiguration,
)
from gordon_system.src.agent.components.networks.oriented.state import (
    OrientedNetworkState,
)
from gordon_system.src.agent.components.networks.oriented.exceptions import (
    OrientedNetworkError,
    OrientedNetworkConfigurationError,
    OrientedNetworkInitializationError,
    OrientedNetworkScaffoldError,
    OrientedNetworkUnsupportedOperationError,
)

# =============================================================================
# PHASE 4.7.1: Canonical Network Facade
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.network import (
    OrientedNetwork,
    BaseOrientedNetwork,
)

__all__ = [
    # Metadata
    "__version__",
    # Configuration (Phase 4.7.1)
    "OrientedNetworkConfiguration",
    # State (Phase 4.7.1)
    "OrientedNetworkState",
    # Errors (Phase 4.7.1)
    "OrientedNetworkError",
    "OrientedNetworkConfigurationError",
    "OrientedNetworkInitializationError",
    "OrientedNetworkScaffoldError",
    "OrientedNetworkUnsupportedOperationError",
    # Network Facade (Phase 4.7.1)
    "BaseOrientedNetwork",
    "OrientedNetwork",
]