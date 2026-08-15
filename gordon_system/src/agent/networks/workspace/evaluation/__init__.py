# Workspace Candidate Evaluation Semantics
# =========================================

"""
Canonical Workspace Candidate Evaluation definitions.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - External time providers only
    - External identity providers only
    - Bounded collections
    - Semantic-time preservation
    - Deterministic outputs for equivalent inputs

EVALUATION ARCHITECTURE OVERVIEW
================================

Evaluation is the process of characterizing admitted Workspace Candidates 
relative to an exact Workspace context, without determining winners or 
constructing Broadcasts.

PIPELINE:
    
    WorkspaceCandidatePool
            ↓
    WorkspaceEvaluationRequest
            ↓
    WorkspaceEvaluationContext
            ↓
    Dimension applicability
            ↓
    Evidence collection references
            ↓
    Candidate evaluation
            ↓
    Dimension results
            ↓
    Candidate-level findings
            ↓
    EvaluatedWorkspaceCandidate
            ↓
    EvaluatedWorkspaceCandidatePool

CONSUMER INPUTS (Later Phases):
    
    EvaluatedWorkspaceCandidatePool
            ↓
    Workspace Competition
            ↓
    Workspace Competition Frontier
            ↓
    Broadcast Selection

EVALUATION IS NOT:
    - Winner selection
    - Competition execution
    - Broadcast construction
    - Runtime delivery
"""

from __future__ import annotations

# =============================================================================
# CANONICAL EVALUATION DEFINITION
# =============================================================================

from .identities import (
    WorkspaceEvaluationIdentity,
    WorkspaceEvaluationRevision,
    WorkspaceEvaluationReference,
)

from .request import (
    WorkspaceEvaluationRequest,
    WorkspaceEvaluationPurpose,
)

from .context import (
    WorkspaceEvaluationContext,
    WorkspaceEvaluationContextIdentity,
    WorkspaceEvaluationContextRevision,
    WorkspaceEvaluationContextReference,
)

from .scope import (
    WorkspaceEvaluationScope,
)

from .authority import (
    WorkspaceEvaluationAuthority,
    WorkspaceEvaluationAuthorityRequirement,
    WorkspaceEvaluationAuthorityStatus,
)

# =============================================================================
# DIMENSION ARCHITECTURE
# =============================================================================

from .dimensions.base import (
    WorkspaceEvaluationDimension,
    WorkspaceEvaluationDimensionIdentity,
    WorkspaceEvaluationDimensionRevision,
    WorkspaceEvaluationDimensionReference,
)

from .dimensions.set import (
    WorkspaceEvaluationDimensionSet,
    WorkspaceEvaluationDimensionSetIdentity,
    WorkspaceEvaluationDimensionSetRevision,
    WorkspaceEvaluationDimensionSetReference,
)

# =============================================================================
# SCALE, DIRECTION, APPLICABILITY
# =============================================================================

from .scales import (
    WorkspaceEvaluationScale,
    WorkspaceEvaluationScaleKind,
)

from .direction import (
    WorkspaceEvaluationDirection,
)

from .applicability import (
    WorkspaceEvaluationApplicability,
    WorkspaceEvaluationApplicabilityStatus,
)

# =============================================================================
# VALUES AND EVIDENCE
# =============================================================================

from .values import (
    WorkspaceEvaluationValue,
)

from .evidence import (
    WorkspaceEvaluationEvidence,
    WorkspaceEvaluationEvidenceReference,
    WorkspaceEvaluationEvidenceKind,
)

# =============================================================================
# ASSUMPTIONS, CONSTRAINTS, CONFIDENCE, UNCERTAINTY, MISSINGNESS
# =============================================================================

from .assumptions import (
    WorkspaceEvaluationAssumption,
)

from .constraints import (
    WorkspaceEvaluationConstraint,
    WorkspaceEvaluationConstraintKind,
)

from .confidence import (
    WorkspaceEvaluationConfidence,
)

from .uncertainty import (
    WorkspaceEvaluationUncertainty,
    WorkspaceEvaluationUncertaintyKind,
)

from .missingness import (
    WorkspaceEvaluationMissingness,
    WorkspaceEvaluationMissingnessReason,
)

# =============================================================================
# CALIBRATION AND NORMALIZATION
# =============================================================================

from .calibration import (
    WorkspaceEvaluationCalibration,
    WorkspaceEvaluationCalibrationIdentity,
    WorkspaceEvaluationCalibrationRevision,
    WorkspaceEvaluationCalibrationReference,
)

from .normalization import (
    WorkspaceEvaluationNormalization,
    WorkspaceEvaluationNormalizationKind,
)

# =============================================================================
# RESULTS, FINDINGS, LIMITATIONS
# =============================================================================

from .result import (
    WorkspaceEvaluationDimensionResult,
)

from .findings import (
    WorkspaceEvaluationFinding,
    WorkspaceEvaluationFindingKind,
)

from .limitations import (
    WorkspaceEvaluationLimitation,
    WorkspaceEvaluationLimitationKind,
)

# =============================================================================
# EVALUATED ENTITIES
# =============================================================================

from .evaluated_candidate import (
    EvaluatedWorkspaceCandidate,
    EvaluatedWorkspaceCandidateIdentity,
    EvaluatedWorkspaceCandidateRevision,
    EvaluatedWorkspaceCandidateReference,
)

from .completeness import (
    WorkspaceEvaluationCompleteness,
)

from .validity import (
    WorkspaceEvaluationValidity,
)

from .evaluated_pool import (
    EvaluatedWorkspaceCandidatePool,
    EvaluatedWorkspaceCandidatePoolIdentity,
    EvaluatedWorkspaceCandidatePoolRevision,
    EvaluatedWorkspaceCandidatePoolReference,
)

# =============================================================================
# DISPOSITIONS
# =============================================================================

from .disposition import (
    WorkspaceEvaluationDisposition,
    WorkspaceEvaluationDispositionKind,
)

# =============================================================================
# AGGREGATE EVALUATION AND WEIGHTS
# =============================================================================

from .aggregate import (
    WorkspaceAggregateEvaluation,
    WorkspaceAggregateEvaluationMethod,
)

from .weights import (
    WorkspaceEvaluationWeight,
    WorkspaceEvaluationWeightSet,
    WorkspaceEvaluationWeightSetRevision,
)

# =============================================================================
# MODULATION PROJECTIONS
# =============================================================================

from .projections import (
    WorkspaceExecutiveEvaluationProjection,
    WorkspaceAttentionEvaluationProjection,
    WorkspaceMotivationEvaluationProjection,
    WorkspaceAlertEvaluationProjection,
)

# =============================================================================
# HISTORY AND LINEAGE
# =============================================================================

from .history import (
    WorkspaceEvaluationHistory,
    WorkspaceEvaluationHistoryEntry,
)

from .lineage import (
    WorkspaceEvaluationLineage,
    WorkspaceEvaluationLineageRelation,
)

# =============================================================================
# INVALIDATION AND CONTINUATION
# =============================================================================

from .invalidation import (
    WorkspaceEvaluationInvalidation,
    WorkspaceEvaluationInvalidationReason,
)

from .continuation import (
    WorkspaceEvaluationContinuation,
    WorkspaceEvaluationContinuationKind,
)

# =============================================================================
# VALIDATION
# =============================================================================

from .validation import (
    WorkspaceEvaluationValidationResult,
)

# =============================================================================
# EXCEPTIONS
# =============================================================================

from .exceptions import (
    WorkspaceEvaluationError,
    WorkspaceEvaluationIdentityError,
    WorkspaceEvaluationRevisionError,
    WorkspaceEvaluationRequestError,
    WorkspaceEvaluationContextError,
    WorkspaceEvaluationScopeError,
    WorkspaceEvaluationAuthorityError,
    WorkspaceEvaluationDimensionError,
    WorkspaceEvaluationScaleError,
    WorkspaceEvaluationApplicabilityError,
    WorkspaceEvaluationEvidenceError,
    WorkspaceEvaluationAssumptionError,
    WorkspaceEvaluationConstraintError,
    WorkspaceEvaluationConfidenceError,
    WorkspaceEvaluationUncertaintyError,
    WorkspaceEvaluationMissingnessError,
    WorkspaceEvaluationCalibrationError,
    WorkspaceEvaluationNormalizationError,
    WorkspaceEvaluationResultError,
    WorkspaceEvaluatedCandidateError,
    WorkspaceEvaluatedPoolError,
    WorkspaceEvaluationHistoryError,
    WorkspaceEvaluationLineageError,
    WorkspaceEvaluationInvalidationError,
    WorkspaceEvaluationCapacityError,
    WorkspaceEvaluationDeterminismError,
    WorkspaceEvaluationInvariantViolation,
)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Canonical evaluation definitions
    "WorkspaceEvaluationIdentity",
    "WorkspaceEvaluationRevision",
    "WorkspaceEvaluationReference",
    
    # Request
    "WorkspaceEvaluationRequest",
    "WorkspaceEvaluationPurpose",
    
    # Context
    "WorkspaceEvaluationContext",
    "WorkspaceEvaluationContextIdentity",
    "WorkspaceEvaluationContextRevision",
    "WorkspaceEvaluationContextReference",
    
    # Scope
    "WorkspaceEvaluationScope",
    
    # Authority
    "WorkspaceEvaluationAuthority",
    "WorkspaceEvaluationAuthorityRequirement",
    "WorkspaceEvaluationAuthorityStatus",
    
    # Dimension architecture
    "WorkspaceEvaluationDimension",
    "WorkspaceEvaluationDimensionIdentity",
    "WorkspaceEvaluationDimensionRevision",
    "WorkspaceEvaluationDimensionReference",
    "WorkspaceEvaluationDimensionSet",
    "WorkspaceEvaluationDimensionSetIdentity",
    "WorkspaceEvaluationDimensionSetRevision",
    "WorkspaceEvaluationDimensionSetReference",
    
    # Scale, Direction, Applicability
    "WorkspaceEvaluationScale",
    "WorkspaceEvaluationScaleKind",
    "WorkspaceEvaluationDirection",
    "WorkspaceEvaluationApplicability",
    "WorkspaceEvaluationApplicabilityStatus",
    
    # Values and Evidence
    "WorkspaceEvaluationValue",
    "WorkspaceEvaluationEvidence",
    "WorkspaceEvaluationEvidenceReference",
    "WorkspaceEvaluationEvidenceKind",
    
    # Assumptions, Constraints, Confidence, Uncertainty, Missingness
    "WorkspaceEvaluationAssumption",
    "WorkspaceEvaluationConstraint",
    "WorkspaceEvaluationConstraintKind",
    "WorkspaceEvaluationConfidence",
    "WorkspaceEvaluationUncertainty",
    "WorkspaceEvaluationUncertaintyKind",
    "WorkspaceEvaluationMissingness",
    "WorkspaceEvaluationMissingnessReason",
    
    # Calibration and Normalization
    "WorkspaceEvaluationCalibration",
    "WorkspaceEvaluationCalibrationIdentity",
    "WorkspaceEvaluationCalibrationRevision",
    "WorkspaceEvaluationCalibrationReference",
    "WorkspaceEvaluationNormalization",
    "WorkspaceEvaluationNormalizationKind",
    
    # Results, Findings, Limitations
    "WorkspaceEvaluationDimensionResult",
    "WorkspaceEvaluationFinding",
    "WorkspaceEvaluationFindingKind",
    "WorkspaceEvaluationLimitation",
    "WorkspaceEvaluationLimitationKind",
    
    # Evaluated entities
    "EvaluatedWorkspaceCandidate",
    "EvaluatedWorkspaceCandidateIdentity",
    "EvaluatedWorkspaceCandidateRevision",
    "EvaluatedWorkspaceCandidateReference",
    "WorkspaceEvaluationCompleteness",
    "WorkspaceEvaluationValidity",
    "EvaluatedWorkspaceCandidatePool",
    "EvaluatedWorkspaceCandidatePoolIdentity",
    "EvaluatedWorkspaceCandidatePoolRevision",
    "EvaluatedWorkspaceCandidatePoolReference",
    
    # Dispositions
    "WorkspaceEvaluationDisposition",
    "WorkspaceEvaluationDispositionKind",
    
    # Aggregate and Weights
    "WorkspaceAggregateEvaluation",
    "WorkspaceAggregateEvaluationMethod",
    "WorkspaceEvaluationWeight",
    "WorkspaceEvaluationWeightSet",
    "WorkspaceEvaluationWeightSetRevision",
    
    # Projections
    "WorkspaceExecutiveEvaluationProjection",
    "WorkspaceAttentionEvaluationProjection",
    "WorkspaceMotivationEvaluationProjection",
    "WorkspaceAlertEvaluationProjection",
    
    # History and Lineage
    "WorkspaceEvaluationHistory",
    "WorkspaceEvaluationHistoryEntry",
    "WorkspaceEvaluationLineage",
    "WorkspaceEvaluationLineageRelation",
    
    # Invalidation and Continuation
    "WorkspaceEvaluationInvalidation",
    "WorkspaceEvaluationInvalidationReason",
    "WorkspaceEvaluationContinuation",
    "WorkspaceEvaluationContinuationKind",
    
    # Validation
    "WorkspaceEvaluationValidationResult",
    
    # Exceptions
    "WorkspaceEvaluationError",
    "WorkspaceEvaluationIdentityError",
    "WorkspaceEvaluationRevisionError",
    "WorkspaceEvaluationRequestError",
    "WorkspaceEvaluationContextError",
    "WorkspaceEvaluationScopeError",
    "WorkspaceEvaluationAuthorityError",
    "WorkspaceEvaluationDimensionError",
    "WorkspaceEvaluationScaleError",
    "WorkspaceEvaluationApplicabilityError",
    "WorkspaceEvaluationEvidenceError",
    "WorkspaceEvaluationAssumptionError",
    "WorkspaceEvaluationConstraintError",
    "WorkspaceEvaluationConfidenceError",
    "WorkspaceEvaluationUncertaintyError",
    "WorkspaceEvaluationMissingnessError",
    "WorkspaceEvaluationCalibrationError",
    "WorkspaceEvaluationNormalizationError",
    "WorkspaceEvaluationResultError",
    "WorkspaceEvaluatedCandidateError",
    "WorkspaceEvaluatedPoolError",
    "WorkspaceEvaluationHistoryError",
    "WorkspaceEvaluationLineageError",
    "WorkspaceEvaluationInvalidationError",
    "WorkspaceEvaluationCapacityError",
    "WorkspaceEvaluationDeterminismError",
    "WorkspaceEvaluationInvariantViolation",
]