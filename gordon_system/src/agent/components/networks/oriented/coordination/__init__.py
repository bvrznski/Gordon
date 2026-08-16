# Oriented Network Coordination Package
# =====================================

"""
Coordination Subsystem for Phase 4.7.5 of the Gordon Cognitive Architecture

PUBLIC API:
    - contracts: Coordination contract types
        * BaseCoordinator: Abstract base class for coordination contracts
        * PurposeCoordination, MissionCoordination, GoalCoordination
        * ObjectiveCoordination, TaskCoordination, ConstraintCoordination
        
    - lifecycle: Lifecycle state types
        * BaseLifecycleState: Abstract base for lifecycle states  
        * PurposeLifecycleState, MissionLifecycleState, GoalLifecycleState
        * ObjectiveLifecycleState, TaskLifecycleState

SEMANTIC LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-001 through ORIENTED-COORDINATION-LAW-040

ARCHITECTURAL PRINCIPLES:
    - Coordination is semantic only (no runtime execution)
    - External ownership of intentional artefacts
    - Explicit references and typed relationships
    - Immutable coordination contracts
"""

from __future__ import annotations

# =============================================================================
# PHASE 4.7.5: Coordination Package - Public API
# =============================================================================

# Import contract types from subpackage
from gordon_system.src.agent.components.networks.oriented.coordination.contracts import (
    BaseCoordinator,
    CoordinationAuthority,
    CoordinationOwner,
    CoordinationStatus,
    
    # Contract implementations (Phase 4.7.5)
    PurposeCoordination,
    MissionCoordination,
    GoalCoordination,
    ObjectiveCoordination,
    TaskCoordination,
    ConstraintCoordination,
)

# Import lifecycle types from subpackage
from gordon_system.src.agent.components.networks.oriented.coordination.lifecycle import (
    BaseLifecycleState,
    
    # Lifecycle states (Phase 4.7.5)
    PurposeLifecycleState,
    MissionLifecycleState,
    GoalLifecycleState,
    ObjectiveLifecycleState,
    TaskLifecycleState,
)

__all__ = [
    # Contract types
    "BaseCoordinator",
    "CoordinationAuthority",
    "CoordinationOwner",
    "CoordinationStatus",
    
    # Contract implementations (Phase 4.7.5)
    "PurposeCoordination",
    "MissionCoordination", 
    "GoalCoordination",
    "ObjectiveCoordination",
    "TaskCoordination",
    "ConstraintCoordination",
    
    # Lifecycle types
    "BaseLifecycleState",
    
    # Lifecycle states (Phase 4.7.5)
    "PurposeLifecycleState",
    "MissionLifecycleState",
    "GoalLifecycleState",
    "ObjectiveLifecycleState",
    "TaskLifecycleState",
]