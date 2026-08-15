# Gordon Cognitive Architecture - Phase 4.5.5
# ===========================================

"""
Action Evaluation Subsystem

This module defines the canonical Action Evaluation architecture for the Gordon
autonomous cognitive agent.

CANONICAL DEFINITION
====================

Action Evaluation is the runtime-neutral process of assessing every Action
Candidate independently and comparatively to determine:

* How good it is (Feasibility, Suitability, Adequacy)
* How safe it is (Risk, Reversibility, Persistence, Safety)
* How compatible it is (Goals, Strategy, Plan, Policies, Security, Workspace)
* How complete it is (Evidence, Assumptions, Constraints)
* What the expected outcomes are
* The level of confidence and uncertainty
* Whether it dominates or conflicts with other candidates

Action Evaluation is NOT:
    - Action Generation (that's candidate creation)
    - Action Ranking (global ordering is deferred to Phase 4.5.6)
    - Action Arbitration (conflict resolution is separate)
    - Action Selection (final choice is external)
    - Execution (runtime operation)
    - Scheduling (timing is external)
    - Effector invocation (implementation is external)

ARCHITECTURE
============

EvaluationArtifact (base concept)
    ↓
ActionEvaluationResult
    ├── Identity: evaluation identity
    ├── Revision: evaluation revision number
    ├── CandidateReference: reference to evaluated candidate
    ├── Report: detailed evaluation report
    ├── DimensionResults: per-dimension assessments
    ├── Recommendation: advisory recommendation
    ├── Confidence: confidence level (0.0 to 1.0)
    ├── Uncertainty: uncertainty level (0.0 to 1.0)
    ├── Limitations: known limitations
    ├── Assumptions: evaluation assumptions
    └── EvidenceReferences: evidence references

ActionEvaluationReport
    ├── Per-Candidate Evaluation
    │   ├── Feasibility: can this actually work?
    │   ├── Suitability: is this appropriate?
    │   ├── Adequacy: does it satisfy the purpose?
    │   ├── Compatibility: how well does it fit?
    │   ├── Completeness: is it well-formed?
    │   ├── Risk: what could go wrong?
    │   ├── Benefit: what positive outcomes?
    │   └── Expected Utility: net expected value
    │
    ├── Conflict Analysis
    │   ├── Goal Conflicts
    │   ├── Policy Conflicts
    │   ├── Security Conflicts
    │   ├── Commitment Conflicts
    │   └── Action Conflicts
    │
    ├── Interference Analysis
    │   ├── Mutual Exclusion
    │   ├── Redundancy
    │   ├── Obstruction
    │   └── Synergy
    │
    ├── Expected Outcome Analysis
    │   ├── Intended Effects
    │   ├── Unintended Effects
    │   ├── Persistence
    │   └── Reversibility
    │
    ├── Confidence & Uncertainty
    │   ├── Evidence Quality
    │   ├── Model Confidence
    │   └── Environmental Uncertainty
    │
    └── Dominance Analysis
        ├── Strict Dominance
        ├── Weak Dominance
        └── Incomparable

EvaluatedActionCandidatePool
    ├── Original Candidate References
    ├── Evaluation Reports
    ├── Pairwise Comparisons
    ├── Dominance Relations
    ├── Recommendation Summary
    └── Provenance Record

ARCHITECTURAL LAWS
==================

ACTION-EVAL-LAW-001: Evaluation never selects. Selection belongs to Phase 4.5.6.

ACTION-EVAL-LAW-002: Evaluation never executes. Execution is external.

ACTION-EVAL-LAW-003: Evaluation is deterministic. Same inputs yield same outputs.

ACTION-EVAL-LAW-004: Evaluation preserves provenance. All evaluation evidence is
                     tracked and linkable to source.

ACTION-EVAL-LAW-005: Dimensions remain independent. Each dimension is assessed
                     separately without cross-dimension dependencies.

ACTION-EVAL-LAW-006: Confidence and uncertainty are distinct. Confidence measures
                     assessment reliability; uncertainty measures input ambiguity.

ACTION-EVAL-LAW-007: Recommendations are advisory. They guide but do not determine
                     selection.

ACTION-EVAL-LAW-008: Conflict detection is separate from conflict resolution.
                     Detection identifies conflicts; resolution happens later.

ACTION-EVAL-LAW-009: Evaluation never mutates Candidates. All evaluation artifacts
                     are immutable and independent of source candidates.

ACTION-EVAL-LAW-010: Evaluation is runtime-neutral. It works on semantic descriptions
                     without requiring runtime state.

OWNERSHIP
=========

Action Evaluation Subsystem owns:
    - Canonical Action Evaluation architecture
    - Evaluation Result types (per-candidate assessment)
    - Evaluation Report types (detailed evaluation artifacts)
    - EvaluatedActionCandidatePool (immutable collection)
    - All dimension assessments (feasibility, suitability, etc.)
    - Conflict analysis
    - Interference analysis
    - Expected outcome analysis
    - Confidence and uncertainty models
    - Dominance analysis
    - Recommendation generation

Action Evaluation Subsystem does NOT own:
    - Action candidate generation
    - Candidate ranking or ordering
    - Final selection decision
    - Resource allocation
    - Runtime execution scheduling
    - Effector invocation
    - Execution monitoring

IMPORT SAFETY
=============

This package is designed to be import-safe:
    - No filesystem access during import
    - No network access during import
    - No model loading during import
    - No runtime initialization during import
    - No random identity generation during import
    - No wall-clock acquisition during import

All construction is deterministic given identical semantic inputs.
"""

__all__ = [
    # Identity types
    "EvaluationId",
    "EvaluationRevision",
    
    # Result and report types
    "ActionEvaluationReport",
    "EvaluatedActionCandidatePool",
    "EvaluatedActionCandidatePoolSummary",
    "EvaluatedActionCandidate",
    
    # Dimension result types
    "FeasibilityResult",
    "SuitabilityResult",
    "AdequacyResult",
    "CompatibilityResult",
    "CompletenessResult",
    "RiskResult",
    "BenefitResult",
    "ExpectedUtilityResult",
    "ReversibilityResult",
    "PersistenceResult",
    
    # Conflict and interference types
    "ConflictType",
    "ConflictRecord",
    "InterferenceKind",
    "InterferenceRecord",
    
    # Expected outcome types
    "OutcomeEffectiveness",
    "OutcomeSideEffects",
    "ExpectedOutcomes",
    
    # Confidence/uncertainty types
    "ConfidenceLevel",
    "UncertaintyLevel",
    "ConfidenceAssessment",
    "UncertaintyAssessment",
    
    # Dominance and comparison types
    "DominanceKind",
    "PairwiseComparison",
    "DominanceRelation",
    
    # Recommendation types
    "RecommendationKind",
    "ActionRecommendation",
    
    # Context types
    "ActionEvaluationContext",
    "ActionEvaluationRequest",
    
    # Validation types
    "EvaluationValidationResult",
    "validate_dimension_score",
    "validate_confidence_uncertainty_pair",
    "validate_candidate_id",
    "validate_evaluation_revision",
    "EvaluationValidator",
]

# Import all public symbols from submodules
from .request import (
    ActionEvaluationRequest,
)

from .context import (
    ActionEvaluationContext,
)

from .dimensions import (
    FeasibilityResult,
    SuitabilityResult,
    AdequacyResult,
    CompatibilityResult,
    CompletenessResult,
    RiskResult,
    BenefitResult,
    ExpectedUtilityResult,
    ReversibilityResult,
    PersistenceResult,
)

from .conflicts import (
    ConflictType,
    ConflictRecord,
)

from .interference import (
    InterferenceKind,
    InterferenceRecord,
)

from .outcomes import (
    OutcomeEffectiveness,
    OutcomeSideEffects,
    ExpectedOutcomes,
)

from .confidence import (
    ConfidenceLevel,
    UncertaintyLevel,
    ConfidenceAssessment,
    UncertaintyAssessment,
)

from .dominance import (
    DominanceKind,
    PairwiseComparison,
    DominanceRelation,
)


# Type aliases for backward compatibility
EvaluationId = str
"""Identifier for an evaluation."""
EvaluationRevision = int
"""Revision number for an evaluation."""

from .recommendation import (
    RecommendationKind,
    ActionRecommendation,
)

from .reports import (
    EvaluationDisposition,
    ActionEvaluationReport,
    EvaluatedActionCandidatePool,
    EvaluatedActionCandidatePoolSummary,
    EvaluatedActionCandidate,
)

from .validation import (
    EvaluationValidationResult,
    validate_dimension_score,
    validate_confidence_uncertainty_pair,
    validate_candidate_id,
    validate_evaluation_revision,
    EvaluationValidator,
)
