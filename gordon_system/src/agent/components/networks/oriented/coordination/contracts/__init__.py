# Oriented Network Coordination Contracts Package
# ===============================================

"""
Coordination Contracts for Phase 4.7.5

PUBLIC API:
    - BaseCoordinator: Abstract base for coordination contracts
    - PurposeCoordination: Purpose orientation coordination
    - MissionCoordination: Mission orientation coordination  
    - GoalCoordination: Goal orientation coordination
    - ObjectiveCoordination: Objective orientation coordination
    - TaskCoordination: Task orientation coordination
    - ConstraintCoordination: Constraint influence coordination

SEMANTIC LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-001 through ORIENTED-COORDINATION-LAW-040
"""

from __future__ import annotations

# =============================================================================
# PHASE 4.7.5: Coordination Contracts - Base Interface
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.coordination.contracts.base import (
    BaseCoordinator,
    CoordinationAuthority,
    CoordinationOwner,
    CoordinationStatus,
)

from gordon_system.src.agent.components.networks.oriented.coordination.contracts.purpose import (
    PurposeCoordination,
    PurposeCoordinationStatus,
)

from gordon_system.src.agent.components.networks.oriented.coordination.contracts.mission import (
    MissionCoordination,
    MissionCoordinationStatus,
)

from gordon_system.src.agent.components.networks.oriented.coordination.contracts.goal import (
    GoalCoordination,
    GoalCoordinationStatus,
)

from gordon_system.src.agent.components.networks.oriented.coordination.contracts.objective import (
    ObjectiveCoordination,
    ObjectiveCoordinationStatus,
)

from gordon_system.src.agent.components.networks.oriented.coordination.contracts.task import (
    TaskCoordination,
    TaskCoordinationStatus,
)

from gordon_system.src.agent.components.networks.oriented.coordination.contracts.constraint import (
    ConstraintCoordination,
    ConstraintCoordinationStatus,
    ConstraintType,
)

__all__ = [
    # Base coordination interface
    "BaseCoordinator",
    "CoordinationAuthority",
    "CoordinationOwner",
    "CoordinationStatus",
    # Purpose Coordination (Phase 4.7.5)
    "PurposeCoordination",
    "PurposeCoordinationStatus",
    # Mission Coordination (Phase 4.7.5)
    "MissionCoordination",
    "MissionCoordinationStatus",
    # Goal Coordination (Phase 4.7.5)
    "GoalCoordination",
    "GoalCoordinationStatus",
    # Objective Coordination (Phase 4.7.5)
    "ObjectiveCoordination",
    "ObjectiveCoordinationStatus",
    # Task Coordination (Phase 4.7.5)
    "TaskCoordination",
    "TaskCoordinationStatus",
    # Constraint Coordination (Phase 4.7.5)
    "ConstraintCoordination",
    "ConstraintCoordinationStatus",
    "ConstraintType",
]
