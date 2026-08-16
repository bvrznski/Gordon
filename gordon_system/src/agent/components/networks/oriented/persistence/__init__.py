# Oriented Network Persistence Abstractions - Phase 4.7.8 Part 1 & 2
# ====================================================================

"""
Persistence Abstractions for the Oriented Network (Phase 4.7.8)

PHASE 4.7.8 MISSION:
    Construct canonical semantic representations describing orientation persistence,
    continuity, interruption, suspension, recovery, capacity, cognitive load,
    and resource requirements.

ARCHITECTURAL PRINCIPLES:
    - Persistence represents semantic continuity
    - It never implements runtime persistence mechanisms
    - No checkpointing, no storage ownership, no restart logic
    - Pure semantic representation only

CONTENTS:
    Base Persistence Models (Part 1)
        - BasePersistenceModel: Abstract base class
        - BasePersistenceReference: Base reference type
        - PersistenceIdentity, PersistenceRevision, PersistenceVersion
        
    Continuity Model (Part 1 & 2)
        - ContinuousOrientation: Uninterrupted semantic identity
        - InterruptedOrientation: Identity preserved across interruption
        - ResumedOrientation: Restarted after interruption
        - RestoredOrientation: Recovered from persistence state
        - InheritedOrientation: Continuity from source
        
    Interruption Model (Part 1 & 2)
        - ExpectedInterruption, UnexpectedInterruption
        - ExternalInterruption, InternalInterruption
        - ExecutiveInterruption, ResourceInterruption
        
    Recovery Model (Part 1 & 2)
        - RecoveryCandidate, RecoveredOrientation
        - RecoveryContext, RecoveryRequirement, RecoveryRelationship
        
    Capacity Model (Part 1 & 2)
        - OrientationCapacity, CurrentCapacity, RequiredCapacity
        - AvailableCapacity, ProjectedCapacity
        
    Cognitive Load Model (Part 1 & 2)
        - OrientationLoad, ExpectedLoad, CurrentLoad
        - ProjectedLoad, PeakLoad, ResidualLoad
        
    Requirement Model (Part 1 & 2)
        - Requirement, AttentionRequirement, WorkspaceRequirement
        - WorkingMemoryRequirement, ExecutiveRequirement, ReasoningRequirement
        - PlanningRequirement, MotivationRequirement, SalienceRequirement

NO RUNTIME BEHAVIOR:
    - No persistence engine
    - No checkpoint system
    - No recovery engine
    - No monitoring
    - No scheduling
"""

from __future__ import annotations

# =============================================================================
# BASE PERSISTENCE MODELS (PART 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.persistence.base import (
    BasePersistenceModel,
    BasePersistenceReference,
    PersistenceIdentity,
    PersistenceRevision,
    PersistenceVersion,
    PersistenceType,
)

# =============================================================================
# CONTINUITY MODEL (PART 1 & 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.persistence.continuity import (
    ContinuousOrientation,
    InterruptedOrientation as ContinuityInterrupted,
    ResumedOrientation,
    RestoredOrientation,
    InheritedOrientation,
    ContinuityReference,
    ContinuityRelationship,
    ContinuityRequirement,
    ContinuityAuthority,
    ContinuityOwner,
    ContinuityProjection,
)

# =============================================================================
# INTERRUPTION MODEL (PART 1 & 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.persistence.interruption import (
    ExpectedInterruption,
    UnexpectedInterruption,
    ExternalInterruption,
    InternalInterruption,
    ExecutiveInterruption,
    ResourceInterruption,
    InterruptionReference,
    InterruptionRelationship,
    InterruptionClassification,
    InterruptionAuthority,
    InterruptionOwner,
)

# =============================================================================
# RECOVERY MODEL (PART 1 & 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.persistence.recovery import (
    RecoveryCandidate,
    RecoveredOrientation,
    RecoveryContext,
    RecoveryRequirement,
    RecoveryRelationship,
    RecoveryReference,
    RecoveryProjection,
)

# =============================================================================
# CAPACITY MODEL (PART 1 & 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.persistence.capacity import (
    OrientationCapacity,
    CurrentCapacity,
    RequiredCapacity,
    AvailableCapacity,
    ProjectedCapacity,
    CapacityReference,
    CapacityProjection,
)

# =============================================================================
# COGNITIVE LOAD MODEL (PART 1 & 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.persistence.load import (
    OrientationLoad,
    ExpectedLoad,
    CurrentLoad,
    ProjectedLoad,
    PeakLoad,
    ResidualLoad,
    LoadReference,
    LoadProjection,
)

# =============================================================================
# REQUIREMENT MODEL (PART 1 & 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.persistence.requirement import (
    Requirement,
    AttentionRequirement,
    WorkspaceRequirement,
    WorkingMemoryRequirement,
    ExecutiveRequirement,
    ReasoningRequirement,
    PlanningRequirement,
    MotivationRequirement,
    SalienceRequirement,
    RequirementReference,
    RequirementProjection,
)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base Persistence Models (Part 1)
    "BasePersistenceModel",
    "BasePersistenceReference",
    "PersistenceIdentity",
    "PersistenceRevision",
    "PersistenceVersion",
    "PersistenceType",
    # Continuity Model (Part 1 & 2)
    "ContinuousOrientation",
    "ContinuityInterrupted",
    "ResumedOrientation",
    "RestoredOrientation",
    "InheritedOrientation",
    "ContinuityReference",
    "ContinuityRelationship",
    "ContinuityRequirement",
    "ContinuityAuthority",
    "ContinuityOwner",
    "ContinuityProjection",
    # Interruption Model (Part 1 & 2)
    "ExpectedInterruption",
    "UnexpectedInterruption",
    "ExternalInterruption",
    "InternalInterruption",
    "ExecutiveInterruption",
    "ResourceInterruption",
    "InterruptionReference",
    "InterruptionRelationship",
    "InterruptionClassification",
    "InterruptionAuthority",
    "InterruptionOwner",
    # Recovery Model (Part 1 & 2)
    "RecoveryCandidate",
    "RecoveredOrientation",
    "RecoveryContext",
    "RecoveryRequirement",
    "RecoveryRelationship",
    "RecoveryReference",
    "RecoveryProjection",
    # Capacity Model (Part 1 & 2)
    "OrientationCapacity",
    "CurrentCapacity",
    "RequiredCapacity",
    "AvailableCapacity",
    "ProjectedCapacity",
    "CapacityReference",
    "CapacityProjection",
    # Cognitive Load Model (Part 1 & 2)
    "OrientationLoad",
    "ExpectedLoad",
    "CurrentLoad",
    "ProjectedLoad",
    "PeakLoad",
    "ResidualLoad",
    "LoadReference",
    "LoadProjection",
    # Requirement Model (Part 1 & 2)
    "Requirement",
    "AttentionRequirement",
    "WorkspaceRequirement",
    "WorkingMemoryRequirement",
    "ExecutiveRequirement",
    "ReasoningRequirement",
    "PlanningRequirement",
    "MotivationRequirement",
    "SalienceRequirement",
    "RequirementReference",
    "RequirementProjection",
]