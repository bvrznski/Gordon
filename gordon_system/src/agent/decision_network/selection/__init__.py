# Gordon Cognitive Architecture - Phase 4.5.7
# ===========================================
#
"""
Final Action Selection Subsystem

This module defines the canonical Final Action Selection architecture for the Gordon
autonomous cognitive agent.

CANONICAL DEFINITION
====================

Final Action Selection is the runtime-neutral, authority-aware semantic process that
accepts one validated Action Candidate from an ActionSelectionFrontier as the Action
to be proposed for downstream Execution review, or produces an explicit no-selection
outcome.

Final Action Selection is NOT:
    - Action Generation (candidate creation)
    - Candidate Evaluation (evaluation is separate)
    - Arbitration (arbitration constructs frontiers)
    - Final Selection (this phase selects from frontiers)
    - Execution (runtime operation)
    - Scheduling (timing is external)

ARCHITECTURE
============

SelectionArtifact (base concept)
    ↓
FinalActionSelectionRequest
    ├── Request Identity: unique selection request identity
    ├── Revision: request revision number
    ├── ActionSelectionRequest Reference: parent context
    ├── Arbitration Result Reference: source frontier
    ├── Selection Frontier Reference: candidates to select from
    ├── Purpose: what kind of selection is needed
    ├── Context: semantic context references
    ├── Scope: bounded selection scope
    └── Completion Requirements: how complete must selection be

ActionSelectionPolicy
    ├── Policy Kind: canonical selection strategy
    ├── Reference: policy identity and version
    └── Authority Scope: what authorities this applies to

SelectedAction
    ├── Identity: unique selected action identity
    ├── Revision: selected action revision number
    ├── Candidate Reference: exact candidate accepted
    ├── Action Reference: exact action representation
    ├── Selection Mode: how selection was made
    ├── Conditions: explicit conditions for validity
    ├── Authority Requirements: authority validation needed
    └── Execution Review Readiness: downstream readiness

ActionSelectionOutcome
    ├── Kind: selected, no-selection, deferred, blocked
    ├── Status: complete, incomplete, invalid, etc.
    ├── Selected Action Reference: if selection occurred
    ├── No Selection Reason: if no selection made
    ├── Candidate Dispositions: final status for each frontier candidate
    └── Continuation: what should happen next

FinalActionSelectionRequest → FinalActionSelectionResult → SelectedAction/NoSelection
                             ↓
                        ExecutionReviewBoundary

SELECTION LAWS
==============

ACTION-SEL-LAW-001: Final Action Selection produces one SelectedAction or an explicit
                   no-selection outcome. It never executes the selected Action.

ACTION-SEL-LAW-002: Final Action Selection never executes the selected Action.

ACTION-SEL-LAW-003: Selection consumes one exact ActionSelectionFrontier revision.

ACTION-SEL-LAW-004: Selection consumes one exact ActionSelectionRequest revision.

ACTION-SEL-LAW-005: Selection does not generate, reevaluate, or rearbitrate Candidates
                   silently.

ACTION-SEL-LAW-006: Selection policy is explicit, versioned, authority-scoped, and
                   replayable.

ACTION-SEL-LAW-007: Policy and Security prohibitions remain authoritative.

ACTION-SEL-LAW-008: Selection authority is distinct from Action authorization and
                   Execution authority.

ACTION-SEL-LAW-009: Unresolved substantive ties never resolve through incidental ordering.

ACTION-SEL-LAW-010: Incomparable Candidates require explicit higher-order policy or
                   authority.

ACTION-SEL-LAW-011: No-selection is a valid semantic outcome.

ACTION-SEL-LAW-012: Every frontier Candidate receives a final-selection disposition.

ACTION-SEL-LAW-013: SelectedAction preserves exact Candidate and Action revisions.

ACTION-SEL-LAW-014: SelectedAction is distinct from ExecutionRequest and Execution.

ACTION-SEL-LAW-015: Selection conditions remain explicit downstream.

ACTION-SEL-LAW-016: Selection limitations and uncertainty remain explicit.

ACTION-SEL-LAW-017: SelectedAction invalidation is explicit and immutable.

ACTION-SEL-LAW-018: Execution-review readiness is declarative and does not authorize
                   or perform Execution.

ACTION-SEL-LAW-019: Equivalent semantic inputs produce equivalent selection artifacts.

ACTION-SEL-LAW-020: Package import performs no selection, authorization, scheduling,
                   or Execution work.

OWNERSHIP
=========

Final Action Selection Subsystem owns:
    - Canonical Final Action Selection architecture
    - FinalSelectionRequest types
    - SelectionPolicy types
    - SelectedAction types
    - ActionSelectionOutcome types
    - SelectionMode types
    - SelectionAuthority types
    - NoSelection and Deferral types
    - SelectionDispositions
    - ExecutionReviewBoundary projections

Final Action Selection Subsystem does NOT own:
    - Action candidate generation
    - Candidate evaluation
    - Arbitration (frontier construction)
    - Policy or Security rule interpretation
    - Resource allocation
    - Runtime execution scheduling
    - Tool invocation

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
    # Request types
    "FinalActionSelectionRequest",
    "FinalActionSelectionRequestId",
    "FinalActionSelectionRequestRevision",
    
    # Policy types
    "ActionSelectionPolicy",
    "ActionSelectionPolicyKind",
    "ActionSelectionPolicyReference",
    
    # Selection modes and authorities
    "ActionSelectionMode",
    "ActionSelectionAuthority",
    "ActionSelectionAuthorityRequirement",
    "ActionSelectionAuthorityReview",
    "ActionSelectionAuthorityStatus",
    "ActionSelectionAuthorityChoice",
    "ActionSelectionUserChoice",
    "ActionSelectionExecutiveChoice",
    
    # Preconditions and eligibility
    "ActionSelectionPrecondition",
    "ActionSelectionPreconditionKind",
    "ActionSelectionPreconditionStatus",
    "ActionSelectionFrontierEligibilityAssessment",
    "FinalActionCandidateEligibilityAssessment",
    
    # Conditions and fallbacks
    "ActionSelectionCondition",
    "ActionSelectionConditionKind",
    "ConditionalSelectedAction",
    "ActionFallbackSelection",
    "ActionSelectionRandomnessReference",
    "ActionSelectionRandomDrawRecord",
    
    # No-selection types
    "ActionNoSelection",
    "ActionNoSelectionReason",
    "ActionSelectionDeferral",
    
    # SelectedAction types
    "SelectedAction",
    "SelectedActionIdentity",
    "SelectedActionRevision",
    "SelectedActionReference",
    "SelectedActionCondition",
    "SelectedActionExpiration",
    "SelectedActionInvalidation",
    "SelectedActionInvalidationReason",
    "SelectedActionReplacement",
    "SelectedActionSupersession",
    
    # Execution review types
    "ActionExecutionReviewRequirement",
    "ActionExecutionReviewRequirementKind",
    "ActionExecutionReviewReadiness",
    "SelectedActionExecutionReviewProjection",
    
    # Justification and assessment types
    "ActionSelectionJustification",
    "ActionSelectionConfidence",
    "ActionSelectionUncertainty",
    "ActionSelectionUncertaintySource",
    "ActionSelectionLimitation",
    "FinalActionSelectionDisposition",
    
    # Outcome types
    "ActionSelectionOutcome",
    "ActionSelectionOutcomeIdentity",
    "ActionSelectionOutcomeRevision",
    "ActionSelectionOutcomeKind",
    "ActionSelectionOutcomeStatus",
    "ActionSelectionCompleteness",
    "ActionSelectionContinuation",
    
    # State and history types
    "ActionSelectionState",
    "ActionSelectionHistory",
    "ActionSelectionHistoryEntry",
    "ActionSelectionLineage",
    "ActionSelectionLineageRelation",
    "ActionSelectionDelta",
    "ActionSelectionTransition",
    "ActionSelectionTransitionKind",
    
    # Plan and validation types
    "FinalActionSelectionPlan",
    "FinalActionSelectionStageKind",
    "ActionSelectionValidationResult",
]

# Import all public symbols from submodules

from .request import (
    FinalActionSelectionRequest,
    FinalActionSelectionRequestId,
    FinalActionSelectionRequestRevision,
)

from .policy import (
    ActionSelectionPolicy,
    ActionSelectionPolicyKind,
    ActionSelectionPolicyReference,
)

from .modes import (
    ActionSelectionMode,
)

from .authority import (
    ActionSelectionAuthority,
    ActionSelectionAuthorityRequirement,
    ActionSelectionAuthorityReview,
    ActionSelectionAuthorityStatus,
    ActionSelectionAuthorityChoice,
    ActionSelectionUserChoice,
    ActionSelectionExecutiveChoice,
)

from .preconditions import (
    ActionSelectionPrecondition,
    ActionSelectionPreconditionKind,
    ActionSelectionPreconditionStatus,
)

from .eligibility import (
    ActionSelectionFrontierEligibilityAssessment,
    FinalActionCandidateEligibilityAssessment,
)

from .conditions import (
    ActionSelectionCondition,
    ActionSelectionConditionKind,
    ConditionalSelectedAction,
    ActionFallbackSelection,
    ActionSelectionRandomnessReference,
    ActionSelectionRandomDrawRecord,
)

from .no_selection import (
    ActionNoSelection,
    ActionNoSelectionReason,
    ActionSelectionDeferral,
)

from .selected_action import (
    SelectedAction,
    SelectedActionIdentity,
    SelectedActionRevision,
    SelectedActionReference,
    SelectedActionCondition,
    SelectedActionExpiration,
    SelectedActionInvalidation,
    SelectedActionInvalidationReason,
    SelectedActionReplacement,
    SelectedActionSupersession,
)

from .execution_boundary import (
    ActionExecutionReviewRequirement,
    ActionExecutionReviewRequirementKind,
    ActionExecutionReviewReadiness,
    SelectedActionExecutionReviewProjection,
)

from .justification import (
    ActionSelectionJustification,
    ActionSelectionConfidence,
    ActionSelectionUncertainty,
    ActionSelectionUncertaintySource,
    ActionSelectionLimitation,
    FinalActionSelectionDisposition,
)

from .outcome import (
    ActionSelectionOutcome,
    ActionSelectionOutcomeIdentity,
    ActionSelectionOutcomeRevision,
    ActionSelectionOutcomeKind,
    ActionSelectionOutcomeStatus,
    ActionSelectionCompleteness,
    ActionSelectionContinuation,
)

from .state import (
    ActionSelectionState,
    ActionSelectionHistory,
    ActionSelectionHistoryEntry,
)

from .lineage import (
    ActionSelectionLineage,
    ActionSelectionLineageRelation,
)

from .delta import (
    ActionSelectionDelta,
)

from .transition import (
    ActionSelectionTransition,
    ActionSelectionTransitionKind,
)

from .plan import (
    FinalActionSelectionPlan,
    FinalActionSelectionStageKind,
)

from .validation import (
    ActionSelectionValidationResult,
)
