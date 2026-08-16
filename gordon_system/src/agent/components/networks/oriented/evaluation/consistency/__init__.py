# Oriented Network Consistency Model - Phase 4.7.10
# ===================================================

"""
Consistency evaluation models and contracts for semantic quality assessment.

SEMANTIC ROLE:
    - Describes semantic agreement between orientation elements
    - Never enforces correctness
    - Never modifies relationships
    
OWNERSHIP CONTRACT:
    - Owns: consistency semantics, relationships, validation
    - Never owns: enforcement, correction, behavioural modification

CONSISTENCY LAWS:
    ORIENTED-CONSISTENCY-LAW-001 through 006: Consistency semantics and constraints
"""

from __future__ import annotations

# =============================================================================
# CONSISTENCY MODELS (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.consistency.models import (
    SemanticConsistency,
    GoalConsistency,
    MissionConsistency,
    TaskConsistency,
    ConstraintConsistency,
    RelationshipConsistency,
)

# =============================================================================
# CONSISTENCY CONTRACTS (Part 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.consistency.contracts import (
    ConsistencyReference,
    ConsistencyRelationship,
    ConsistencyRequirement,
    ConsistencyAuthority,
    ConsistencyOwner,
    ConsistencyProjection,
)

__all__ = [
    # Consistency Models
    "SemanticConsistency",
    "GoalConsistency",
    "MissionConsistency",
    "TaskConsistency",
    "ConstraintConsistency",
    "RelationshipConsistency",
    # Consistency Contracts
    "ConsistencyReference",
    "ConsistencyRelationship",
    "ConsistencyRequirement",
    "ConsistencyAuthority",
    "ConsistencyOwner",
    "ConsistencyProjection",
]