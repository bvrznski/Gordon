# Oriented Network Evaluation Framework - Phase 4.7.10
# =======================================================

"""
Evaluation Framework for Oriented Network Orientation Assessment.

ARCHITECTURAL ROLE:
    Semantic Quality Evaluation - Descriptive assessment only
    
FUNCTIONAL SCOPE:
    - Coherence evaluation (semantic compatibility)
    - Consistency evaluation (semantic agreement)
    - Alignment evaluation (semantic correspondence)
    - Conflict detection (semantic incompatibility)
    - Drift analysis (semantic divergence)
    - Integrity assessment (semantic soundness)
    - Validity assessment (semantic correctness)
    - Confidence expression (semantic certainty)
    
NOT RESPONSIBLE FOR:
    - Runtime monitoring
    - Correction or repair
    - Optimization or adaptation
    - Decision making or planning
    - Behavioural execution

SEMANTIC LAWS:
    ORIENTED-EVALUATION-LAW-001 through 010: Evaluation remains descriptive
"""

from __future__ import annotations

# =============================================================================
# PHASE 4.7.10: Canonical Metadata
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.__meta__ import (
    __version__,
)

# =============================================================================
# BASE EVALUATION MODELS (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.base.models import (
    BaseEvaluationModel,
    BaseCoherenceModel,
    BaseConsistencyModel,
    BaseConflictModel,
    BaseIntegrityModel,
    BaseAlignmentModel,
    BaseValidityModel,
)

# =============================================================================
# COHERENCE MODEL (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.coherence.models import (
    OrientationCoherence,
    HighCoherence,
    ModerateCoherence,
    LowCoherence,
    BrokenCoherence,
    UnknownCoherence,
)

from gordon_system.src.agent.components.networks.oriented.evaluation.coherence.contracts import (
    CoherenceReference,
    CoherenceRelationship,
    CoherenceRequirement,
    CoherenceAuthority,
    CoherenceOwner,
    CoherenceProjection,
)

# =============================================================================
# CONSISTENCY MODEL (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.consistency.models import (
    SemanticConsistency,
    GoalConsistency,
    MissionConsistency,
    TaskConsistency,
    ConstraintConsistency,
    RelationshipConsistency,
)

from gordon_system.src.agent.components.networks.oriented.evaluation.consistency.contracts import (
    ConsistencyReference,
    ConsistencyRelationship,
    ConsistencyRequirement,
    ConsistencyAuthority,
    ConsistencyOwner,
    ConsistencyProjection,
)

# =============================================================================
# ALIGNMENT MODEL (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.alignment.models import (
    MissionAlignment,
    GoalAlignment,
    TaskAlignment,
    ConstraintAlignment,
    ExecutiveAlignment,
    StrategyAlignment,
)

from gordon_system.src.agent.components.networks.oriented.evaluation.alignment.contracts import (
    AlignmentReference,
    AlignmentRelationship,
    AlignmentRequirement,
    AlignmentAuthority,
    AlignmentOwner,
    AlignmentProjection,
)

# =============================================================================
# CONFLICT MODEL (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.conflict.models import (
    GoalConflict,
    MissionConflict,
    TaskConflict,
    ConstraintConflict,
    PriorityConflict,
    OrientationConflict,
)

from gordon_system.src.agent.components.networks.oriented.evaluation.conflict.contracts import (
    ConflictReference,
    ConflictRelationship,
    ConflictRequirement,
    ConflictAuthority,
    ConflictOwner,
    ConflictProjection,
)

# =============================================================================
# DRIFT MODEL (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.drift.models import (
    SemanticDrift,
    GoalDrift,
    MissionDrift,
    ContextDrift,
    RequirementDrift,
    OrientationDrift,
)

from gordon_system.src.agent.components.networks.oriented.evaluation.drift.contracts import (
    DriftReference,
    DriftRelationship,
    DriftRequirement,
    DriftAuthority,
    DriftOwner,
    DriftProjection,
)

# =============================================================================
# INTEGRITY MODEL (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.integrity.models import (
    SemanticIntegrity,
    StructuralIntegrity,
    RelationshipIntegrity,
    OwnershipIntegrity,
    HierarchyIntegrity,
    ReferenceIntegrity,
)

from gordon_system.src.agent.components.networks.oriented.evaluation.integrity.contracts import (
    IntegrityReference,
    IntegrityRelationship,
    IntegrityRequirement,
    IntegrityAuthority,
    IntegrityOwner,
    IntegrityProjection,
)

# =============================================================================
# VALIDITY MODEL (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.validity.models import (
    ValidOrientation,
    ConditionallyValidOrientation,
    InvalidOrientation,
    DeprecatedOrientation,
    UnknownValidity,
)

from gordon_system.src.agent.components.networks.oriented.evaluation.validity.contracts import (
    ValidityReference,
    ValidityRelationship,
    ValidityRequirement,
    ValidityAuthority,
    ValidityOwner,
    ValidityProjection,
)

# =============================================================================
# CONFIDENCE MODEL (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.confidence.models import (
    OrientationConfidence,
    HighConfidence,
    MediumConfidence,
    LowConfidence,
    UnknownConfidence,
)

# =============================================================================
# COMPLETENESS MODEL (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.completeness.models import (
    CompleteOrientation,
    PartialOrientation,
    IncompleteOrientation,
    UnderspecifiedOrientation,
    UnknownCompleteness,
)

# =============================================================================
# STABILITY MODEL (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.stability.models import (
    StableOrientation,
    RecoveringOrientation,
    UnstableOrientation,
    FragileOrientation,
    RobustOrientation,
)

# =============================================================================
# EVALUATION CONTEXT (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.context import (
    EvaluationContext,
    MissionEvaluation,
    GoalEvaluation,
    TaskEvaluation,
    ConstraintEvaluation,
    ExecutiveEvaluation,
    StrategyEvaluation,
    LifecycleEvaluation,
    PersistenceEvaluation,
    ContinuityEvaluation,
)

# =============================================================================
# EVALUATION RELATIONSHIPS (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.relationships import (
    Orientation,
    Evaluation,
    Coherence,
    Consistency,
    Alignment,
    Integrity,
    Validity,
    Confidence,
)

# =============================================================================
# SEMANTIC INTERACTION MODEL (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.interactions import (
    SemanticInteractionGraph,
    EvaluationRelationship,
)

# =============================================================================
# VALIDATION FRAMEWORK (Part 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.validation import (
    EvaluationValidator,
    validate_coherence,
    validate_consistency,
    validate_alignment,
    validate_conflict,
    validate_drift,
    validate_integrity,
    validate_validity,
)

# =============================================================================
# SERIALIZATION (Part 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.serialization import (
    EvaluationSerializer,
    EvaluationDeserializer,
)

# =============================================================================
# DEPENDENCY RULES (Part 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.dependencies import (
    AllowedDependencies,
    ForbiddenDependencies,
    DependencyValidator,
)

__all__ = [
    # Metadata
    "__version__",
    # Base Models
    "BaseEvaluationModel",
    "BaseCoherenceModel",
    "BaseConsistencyModel",
    "BaseConflictModel",
    "BaseIntegrityModel",
    "BaseAlignmentModel",
    "BaseValidityModel",
    # Coherence Model
    "OrientationCoherence",
    "HighCoherence",
    "ModerateCoherence",
    "LowCoherence",
    "BrokenCoherence",
    "UnknownCoherence",
    "CoherenceReference",
    "CoherenceRelationship",
    "CoherenceRequirement",
    "CoherenceAuthority",
    "CoherenceOwner",
    "CoherenceProjection",
    # Consistency Model
    "SemanticConsistency",
    "GoalConsistency",
    "MissionConsistency",
    "TaskConsistency",
    "ConstraintConsistency",
    "RelationshipConsistency",
    "ConsistencyReference",
    "ConsistencyRelationship",
    "ConsistencyRequirement",
    "ConsistencyAuthority",
    "ConsistencyOwner",
    "ConsistencyProjection",
    # Alignment Model
    "MissionAlignment",
    "GoalAlignment",
    "TaskAlignment",
    "ConstraintAlignment",
    "ExecutiveAlignment",
    "StrategyAlignment",
    "AlignmentReference",
    "AlignmentRelationship",
    "AlignmentRequirement",
    "AlignmentAuthority",
    "AlignmentOwner",
    "AlignmentProjection",
    # Conflict Model
    "GoalConflict",
    "MissionConflict",
    "TaskConflict",
    "ConstraintConflict",
    "PriorityConflict",
    "OrientationConflict",
    "ConflictReference",
    "ConflictRelationship",
    "ConflictRequirement",
    "ConflictAuthority",
    "ConflictOwner",
    "ConflictProjection",
    # Drift Model
    "SemanticDrift",
    "GoalDrift",
    "MissionDrift",
    "ContextDrift",
    "RequirementDrift",
    "OrientationDrift",
    "DriftReference",
    "DriftRelationship",
    "DriftRequirement",
    "DriftAuthority",
    "DriftOwner",
    "DriftProjection",
    # Integrity Model
    "SemanticIntegrity",
    "StructuralIntegrity",
    "RelationshipIntegrity",
    "OwnershipIntegrity",
    "HierarchyIntegrity",
    "ReferenceIntegrity",
    "IntegrityReference",
    "IntegrityRelationship",
    "IntegrityRequirement",
    "IntegrityAuthority",
    "IntegrityOwner",
    "IntegrityProjection",
    # Validity Model
    "ValidOrientation",
    "ConditionallyValidOrientation",
    "InvalidOrientation",
    "DeprecatedOrientation",
    "UnknownValidity",
    "ValidityReference",
    "ValidityRelationship",
    "ValidityRequirement",
    "ValidityAuthority",
    "ValidityOwner",
    "ValidityProjection",
    # Confidence Model
    "OrientationConfidence",
    "HighConfidence",
    "MediumConfidence",
    "LowConfidence",
    "UnknownConfidence",
    # Completeness Model
    "CompleteOrientation",
    "PartialOrientation",
    "IncompleteOrientation",
    "UnderspecifiedOrientation",
    "UnknownCompleteness",
    # Stability Model
    "StableOrientation",
    "RecoveringOrientation",
    "UnstableOrientation",
    "FragileOrientation",
    "RobustOrientation",
    # Evaluation Context
    "EvaluationContext",
    "MissionEvaluation",
    "GoalEvaluation",
    "TaskEvaluation",
    "ConstraintEvaluation",
    "ExecutiveEvaluation",
    "StrategyEvaluation",
    "LifecycleEvaluation",
    "PersistenceEvaluation",
    "ContinuityEvaluation",
    # Evaluation Relationships
    "Orientation",
    "Evaluation",
    "Coherence",
    "Consistency",
    "Alignment",
    "Integrity",
    "Validity",
    "Confidence",
    # Semantic Interaction Model
    "SemanticInteractionGraph",
    "EvaluationRelationship",
    # Validation Framework
    "EvaluationValidator",
    "validate_coherence",
    "validate_consistency",
    "validate_alignment",
    "validate_conflict",
    "validate_drift",
    "validate_integrity",
    "validate_validity",
    # Serialization
    "EvaluationSerializer",
    "EvaluationDeserializer",
    # Dependency Rules
    "AllowedDependencies",
    "ForbiddenDependencies",
    "DependencyValidator",
]