# Oriented Network Content Model - Phase 4.7.3
# ==============================================

"""
Canonical Content Model for the Oriented Network.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Versionable and serializable
    - Repository-independent

CONTENT CATEGORIES:
    - Orientation Content: Current, desired, candidate, historical orientations
    - Reference Content: Pointers to external concepts (Goals, Tasks, etc.)
    - Context Content: Semantic surroundings for orientation
    - Requirement Content: Semantic necessity conditions
    - Constraint Content: Boundary conditions
    - Assessment Content: Observations and evaluations
    - Relationship Content: Explicit semantic connections
    - Metadata Content: Identity, lineage, provenance

SEMANTIC LAWS:
    ORIENTED-CONTENT-LAW-001 through ORIENTED-CONTENT-LAW-040
"""

from __future__ import annotations

# =============================================================================
# BASE CONTENT ABSTRACTIONS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.content.base import (
    BaseContent,
    ContentIdentity,
    ContentRevision,
    ContentVersion,
    ContentAuthority,
    ContentOwner,
)

# =============================================================================
# REFERENCE CONTENT TYPES
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.content.references import (
    GoalReference,
    ObjectiveReference,
    TaskReference,
    MissionReference,
    PurposeReference,
    ConstraintReference,
    DependencyReference,
    PlanReference,
    DecisionReference,
    WorkspaceReference,
    WorkingMemoryReference,
    StrategyReference,
    ReasoningReference,
    EvaluationReference,
)

# =============================================================================
# CONTEXT CONTENT TYPES
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.content.context import (
    MissionContext,
    GoalContext,
    ObjectiveContext,
    TaskContext,
    OperationalContext,
    StrategicContext,
    EnvironmentalContext,
    RecoveryContext,
    ConstraintContext,
    EvaluationContext,
)

# =============================================================================
# REQUIREMENT CONTENT TYPES
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.content.requirements import (
    AttentionRequirement,
    WorkspaceRequirement,
    WorkingMemoryRequirement,
    PlanningRequirement,
    ReasoningRequirement,
    EvaluationRequirement,
    SchedulerRequirement,
)

# =============================================================================
# CONSTRAINT CONTENT TYPES
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.content.constraints import (
    HardConstraint,
    SoftConstraint,
    RequirementConstraint,
    PolicyConstraint,
    DependencyConstraint,
    RiskConstraint,
)

# =============================================================================
# ASSESSMENT CONTENT TYPES
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.content.assessments import (
    ProgressAssessment,
    AlignmentAssessment,
    ConfidenceAssessment,
    RiskAssessment,
    RecoveryAssessment,
    CompletionAssessment,
    DriftAssessment,
)

# =============================================================================
# RELATIONSHIP CONTENT TYPES
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.content.relationships import (
    GoalRelationship,
    ObjectiveRelationship,
    TaskRelationship,
    DependencyRelationship,
    ConstraintRelationship,
    ContextRelationship,
    OrientationRelationship,
)

# =============================================================================
# ORIENTATION CONTENT TYPES
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.content.orientation import (
    CurrentOrientation,
    DesiredOrientation,
    CandidateOrientation,
    HistoricalOrientation,
    SuspendedOrientation,
    RecoveredOrientation,
)

# =============================================================================
# METADATA CONTENT TYPES
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.content.metadata import (
    ContentIdentityMetadata,
    ContentRevisionMetadata,
    ContentVersionMetadata,
    ContentAuthorityMetadata,
    ContentOwnerMetadata,
    ContentSourceMetadata,
    ContentOriginMetadata,
    ContentProvenanceMetadata,
    ContentLineageMetadata,
)

__all__ = [
    # Base abstractions
    "BaseContent",
    "ContentIdentity",
    "ContentRevision",
    "ContentVersion",
    "ContentAuthority",
    "ContentOwner",
    # Reference content
    "GoalReference",
    "ObjectiveReference",
    "TaskReference",
    "MissionReference",
    "PurposeReference",
    "ConstraintReference",
    "DependencyReference",
    "PlanReference",
    "DecisionReference",
    "WorkspaceReference",
    "WorkingMemoryReference",
    "StrategyReference",
    "ReasoningReference",
    "EvaluationReference",
    # Context content
    "MissionContext",
    "GoalContext",
    "ObjectiveContext",
    "TaskContext",
    "OperationalContext",
    "StrategicContext",
    "EnvironmentalContext",
    "RecoveryContext",
    "ConstraintContext",
    "EvaluationContext",
    # Requirement content
    "AttentionRequirement",
    "WorkspaceRequirement",
    "WorkingMemoryRequirement",
    "PlanningRequirement",
    "ReasoningRequirement",
    "EvaluationRequirement",
    "SchedulerRequirement",
    # Constraint content
    "HardConstraint",
    "SoftConstraint",
    "RequirementConstraint",
    "PolicyConstraint",
    "DependencyConstraint",
    "RiskConstraint",
    # Assessment content
    "ProgressAssessment",
    "AlignmentAssessment",
    "ConfidenceAssessment",
    "RiskAssessment",
    "RecoveryAssessment",
    "CompletionAssessment",
    "DriftAssessment",
    # Relationship content
    "GoalRelationship",
    "ObjectiveRelationship",
    "TaskRelationship",
    "DependencyRelationship",
    "ConstraintRelationship",
    "ContextRelationship",
    "OrientationRelationship",
    # Orientation content
    "CurrentOrientation",
    "DesiredOrientation",
    "CandidateOrientation",
    "HistoricalOrientation",
    "SuspendedOrientation",
    "RecoveredOrientation",
    # Metadata content
    "ContentIdentityMetadata",
    "ContentRevisionMetadata",
    "ContentVersionMetadata",
    "ContentAuthorityMetadata",
    "ContentOwnerMetadata",
    "ContentSourceMetadata",
    "ContentOriginMetadata",
    "ContentProvenanceMetadata",
    "ContentLineageMetadata",
]