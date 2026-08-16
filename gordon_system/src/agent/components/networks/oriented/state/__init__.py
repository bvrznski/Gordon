# Oriented Network State Model - Phase 4.7.4
# =============================================

"""
Canonical State Model for the Oriented Network.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Versionable and serializable
    - Repository-independent

STATE CATEGORIES:
    - Identity: Stable semantic identity for state instances
    - Revision: Monotonic revision tracking for state evolution
    - Lineage: Immutable ancestral chain of states
    - Provenance: Immutable origin and validation history
    - Composition: Reference to Content objects (not ownership)
    - Metadata: State-level metadata and summaries

SEMANTIC LAWS:
    ORIENTED-STATE-LAW-001 through ORIENTED-STATE-LAW-040

ARCHITECTURAL INVARIANTS:
    STATE-INV-001 through STATE-INV-038
"""

from __future__ import annotations

# =============================================================================
# BASE STATE ABSTRACTIONS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.state.base import (
    BaseState,
    StateIdentity,
    StateRevision,
    StateVersion,
    StateAuthority,
    StateOwner,
)

# =============================================================================
# STATE METADATA TYPES
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.state.metadata import (
    StateMetadata,
    StateProvenance,
    StateLineage,
    StateOrigin,
    StateIdentityMetadata,
    StateRevisionMetadata,
    StateVersionMetadata,
    StateAuthorityMetadata,
    StateOwnerMetadata,
)

# =============================================================================
# STATE COMPOSITION TYPES
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.state.composition import (
    OrientedNetworkState,
    OrientationState,
    GoalState,
    ObjectiveState,
    TaskState,
    ContextState,
    ConstraintState,
    AssessmentState,
    RelationshipState,
    RequirementState,
)

# =============================================================================
# STATE SNAPSHOT TYPES
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.state.snapshots import (
    CurrentState,
    HistoricalState,
    CandidateState,
    SuspendedState,
    RecoveredState,
    ReferenceState,
)

# =============================================================================
# STATE VALIDATION
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.state.validation import (
    StateValidator,
    validate_state_structure,
    validate_state_composition,
    validate_state_lineage,
    validate_state_provenance,
    StateValidationError,
)

# =============================================================================
# STATE SERIALIZATION
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.state.serialization import (
    StateSerializer,
    StateDeserializer,
    serialize_state,
    deserialize_state,
)

__all__ = [
    # Base abstractions
    "BaseState",
    "StateIdentity",
    "StateRevision",
    "StateVersion",
    "StateAuthority",
    "StateOwner",
    # Metadata types
    "StateMetadata",
    "StateProvenance",
    "StateLineage",
    "StateOrigin",
    "StateIdentityMetadata",
    "StateRevisionMetadata",
    "StateVersionMetadata",
    "StateAuthorityMetadata",
    "StateOwnerMetadata",
    # Composition types
    "OrientedNetworkState",
    "OrientationState",
    "GoalState",
    "ObjectiveState",
    "TaskState",
    "ContextState",
    "ConstraintState",
    "AssessmentState",
    "RelationshipState",
    "RequirementState",
    # Snapshot types
    "CurrentState",
    "HistoricalState",
    "CandidateState",
    "SuspendedState",
    "RecoveredState",
    "ReferenceState",
    # Validation
    "StateValidator",
    "validate_state_structure",
    "validate_state_composition",
    "validate_state_lineage",
    "validate_state_provenance",
    "StateValidationError",
    # Serialization
    "StateSerializer",
    "StateDeserializer",
    "serialize_state",
    "deserialize_state",
]