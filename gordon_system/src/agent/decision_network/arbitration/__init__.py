# Gordon Cognitive Architecture - Phase 4.5.6
# ===========================================
#
"""
Action Arbitration Subsystem

This module defines the canonical Action Arbitration architecture for the Gordon
autonomous cognitive agent.

CANONICAL DEFINITION
====================

Action Arbitration is the runtime-neutral, authority-aware semantic process that
reconciles evaluated Action Candidates into explicit preference, dominance,
compatibility, conflict, equivalence, incomparability, and selection-frontier
relationships without selecting or executing an Action.

Action Arbitration is NOT:
    - Action Generation (that's candidate creation)
    - Candidate Evaluation (evaluation is separate)
    - Final Selection (deferred to Phase 4.5.7)
    - Execution (runtime operation)
    - Scheduling (timing is external)

ARCHITECTURE
============

ArbitrationArtifact (base concept)
    ↓
ActionArbitrationRequest
    ├── Request Identity: unique arbitration identity
    ├── Revision: request revision number
    ├── ActionSelectionRequest Reference: parent selection context
    ├── Evaluated Pool Reference: candidates to arbitrate
    ├── Purpose: arbitration purpose
    ├── Scope: bounded arbitration scope
    ├── Context: semantic context
    ├── Criteria: arbitration criteria
    ├── Hard Constraints: prohibitions
    ├── Preferences: soft preferences
    └── Vetoes: hard vetoes

ActionArbitrationResult
    ├── Result Identity: unique result identity
    ├── Revision: result revision number
    ├── Request Reference: source request
    ├── Comparison Results: pairwise assessments
    ├── Preference Relations: left vs right relationships
    ├── Dominance Relations: candidate dominance
    ├── Partial Order: preference graph
    ├── Pareto Front: non-dominated candidates
    ├── Equivalence Groups: equivalent candidates
    ├── Incomparable Groups: incomparable candidates
    ├── Compatibility Groups: compatible candidates
    ├── Conflict Groups: conflicting candidates
    ├── Fallback Groups: fallback relationships
    ├── Candidate Dispositions: final status per candidate
    ├── Selection Frontiers: admissible frontiers
    └── Recommendation: advisory selection guidance

SelectionFrontier
    ├── Identity: frontier identity
    ├── Revision: frontier revision number
    ├── Frontier Kind: general, safety, Pareto, etc.
    ├── Candidate References: admissible candidates
    ├── Completeness: how complete is the frontier?
    └── Readiness: ready for selection?

ACTION-ARB-LAW-001: Arbitration determines the structured selection frontier.
                   It never creates the final SelectedAction.

ACTION-ARB-LAW-002: Arbitration consumes evaluation artifacts and does not
                   mutate Candidate evaluations.

ACTION-ARB-LAW-003: Hard constraints are distinct from soft preferences.

ACTION-ARB-LAW-004: Policy and Security prohibitions are vetoes or hard
                   constraints, not score penalties.

ACTION-ARB-LAW-005: Authority remains independent from preference and dominance.

ACTION-ARB-LAW-006: Arbitration supports partial order and incomparability.

ACTION-ARB-LAW-007: No total order is fabricated when Candidates are incomparable.

ACTION-ARB-LAW-008: Dominance is multidimensional and constraint-aware.

ACTION-ARB-LAW-009: Every evaluated Candidate receives an Arbitration disposition.

ACTION-ARB-LAW-010: Mandatory Candidates may be preserved without being preferred
                   or selected.

ACTION-ARB-LAW-011: Selection Frontiers are immutable, bounded, and revisioned.

ACTION-ARB-LAW-012: Tie-breaking requirements are explicit.

ACTION-ARB-LAW-013: Arbitration recommendations are advisory.

ACTION-ARB-LAW-014: Arbitration continuation performs no scheduling or invocation.

ACTION-ARB-LAW-015: Equivalent semantic inputs produce equivalent Arbitration artifacts.

ACTION-ARB-LAW-016: Capacity limitations are explicit.

ACTION-ARB-LAW-017: Arbitration does not invoke Policy, Security, Planning,
                   Reasoning, Selection, or Execution implementations.

ACTION-ARB-LAW-018: Arbitration contains no hidden randomness.

ACTION-ARB-LAW-019: Arbitration artifacts preserve authority, privacy, and provenance.

ACTION-ARB-LAW-020: Package import performs no Arbitration, Selection, or Execution work.

OWNERSHIP
=========

Action Arbitration Subsystem owns:
    - Canonical Arbitration architecture
    - Arbitration Request types
    - Arbitration Result types
    - Comparison contracts (preferences, dominance)
    - Partial order and Pareto front representations
    - Equivalence and incomparability groups
    - Selection Frontier definitions
    - Candidate Dispositions
    - Recommendations and Continuation

Action Arbitration Subsystem does NOT own:
    - Action candidate generation
    - Candidate evaluation
    - Final selection decision
    - Resource allocation
    - Runtime execution scheduling
    - Policy or Security rule enforcement (they provide constraints)

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
    "ActionArbitrationRequest",
    "ActionArbitrationRequestId",
    "ActionArbitrationRequestRevision",
    
    # Result types
    "ActionArbitrationResult",
    "ActionArbitrationResultId",
    "ActionArbitrationResultRevision",
    
    # Purpose and context
    "ActionArbitrationPurpose",
    "ActionArbitrationContext",
    "ActionArbitrationScope",
    
    # Criterion types
    "ActionArbitrationCriterion",
    "ActionArbitrationCriterionKind",
    "ActionArbitrationConstraint",
    "ActionArbitrationConstraintKind",
    "ActionArbitrationPreference",
    "ActionArbitrationPreferenceKind",
    "ActionPreferenceStrength",
    
    # Veto types
    "ActionArbitrationVeto",
    "ActionArbitrationVetoKind",
    "ActionArbitrationVetoStatus",
    "ActionMandatoryCandidateRequirement",
    
    # Comparison types
    "ActionCandidateComparabilityAssessment",
    "ActionArbitrationComparisonRequest",
    "ActionArbitrationComparisonResult",
    "ActionPreferenceRelation",
    
    # Dominance and order types
    "ActionDominanceAssessment",
    "ActionDominanceKind",
    "ActionParetoFront",
    "ActionArbitrationPartialOrder",
    
    # Group types
    "ActionIncomparableGroup",
    "ActionArbitrationEquivalenceGroup",
    "ActionArbitrationTie",
    "TieBreakingRequirement",
    "ActionArbitrationConflictGroup",
    "ActionArbitrationInterferenceGroup",
    "ActionCompatibilityGroup",
    "ActionComplementarityAssessment",
    "ActionConditionalCandidateRelation",
    "ActionFallbackGroup",
    
    # Frontier types
    "ActionSafetyFrontier",
    "ActionReversibilityFrontier",
    "ActionInformationFrontier",
    "ActionSelectionFrontier",
    "ActionSelectionFrontierIdentity",
    "ActionSelectionFrontierRevision",
    "ActionSelectionFrontierReference",
    "ActionSelectionFrontierKind",
    "ActionSelectionFrontierCompleteness",
    "ActionSelectionFrontierReadiness",
    
    # Disposition and recommendation types
    "ActionArbitrationCandidateDisposition",
    "ActionArbitrationRecommendation",
    "ActionArbitrationRecommendationKind",
    
    # Status types
    "ActionArbitrationCompleteness",
    "ActionArbitrationReadiness",
    "ActionArbitrationContinuation",
    "ActionArbitrationUnresolvedIssue",
    "ActionArbitrationEscalation",
    
    # State and history types
    "ActionArbitrationState",
    "ActionArbitrationHistory",
    "ActionArbitrationLineage",
    "ActionArbitrationPlan",
    "ActionArbitrationStageKind",
    "ActionArbitrationComparisonCoverage",
]

# Import all public symbols from submodules
from .request import (
    ActionArbitrationRequest,
    ActionArbitrationRequestId,
    ActionArbitrationRequestRevision,
)

from .context import (
    ActionArbitrationContext,
)

from .scope import (
    ActionArbitrationScope,
)

from .purpose import (
    ActionArbitrationPurpose,
)

from .criteria import (
    ActionArbitrationCriterion,
    ActionArbitrationCriterionKind,
)

from .constraints import (
    ActionArbitrationConstraint,
    ActionArbitrationConstraintKind,
)

from .preferences import (
    ActionArbitrationPreference,
    ActionArbitrationPreferenceKind,
    ActionPreferenceStrength,
)

from .vetoes import (
    ActionArbitrationVeto,
    ActionArbitrationVetoKind,
    ActionArbitrationVetoStatus,
    ActionMandatoryCandidateRequirement,
)

# Comparison submodule
from .comparison.comparability import (
    ActionCandidateComparabilityAssessment,
)

from .comparison.requests import (
    ActionArbitrationComparisonRequest,
)

from .comparison.results import (
    ActionArbitrationComparisonResult,
    ActionPreferenceRelation,
)

# Dominance and order submodule
from .dominance.dominance import (
    ActionDominanceAssessment,
    ActionDominanceKind,
)

from .dominance.pareto import (
    ActionParetoFront,
)

from .dominance.partial_order import (
    ActionArbitrationPartialOrder,
)

# Groups submodule
from .groups.equivalence import (
    ActionArbitrationEquivalenceGroup,
)

from .groups.incomparability import (
    ActionIncomparableGroup,
)

from .groups.ties import (
    ActionArbitrationTie,
    TieBreakingRequirement,
)

from .groups.conflicts import (
    ActionArbitrationConflictGroup,
)

from .groups.interference import (
    ActionArbitrationInterferenceGroup,
)

from .groups.compatibility import (
    ActionCompatibilityGroup,
    ActionComplementarityAssessment,
    ActionConditionalCandidateRelation,
    ActionFallbackGroup,
)

# Frontiers submodule
from .frontiers.safety import (
    ActionSafetyFrontier,
)

from .frontiers.reversibility import (
    ActionReversibilityFrontier,
)

from .frontiers.information import (
    ActionInformationFrontier,
)

from .frontiers.selection import (
    ActionSelectionFrontier,
    ActionSelectionFrontierIdentity,
    ActionSelectionFrontierRevision,
    ActionSelectionFrontierReference,
    ActionSelectionFrontierKind,
    ActionSelectionFrontierCompleteness,
    ActionSelectionFrontierReadiness,
)

# Result submodule
from .result import (
    ActionArbitrationResult,
    ActionArbitrationResultId,
    ActionArbitrationResultRevision,
)

from .recommendation import (
    ActionArbitrationRecommendation,
    ActionArbitrationRecommendationKind,
)

from .disposition import (
    ActionArbitrationCandidateDisposition,
)

# Status submodule
from .status.completeness import (
    ActionArbitrationCompleteness,
)

from .status.readiness import (
    ActionArbitrationReadiness,
)

from .status.continuation import (
    ActionArbitrationContinuation,
)

from .status.unresolved import (
    ActionArbitrationUnresolvedIssue,
)

from .status.escalation import (
    ActionArbitrationEscalation,
)

# State and history submodule
from .state import (
    ActionArbitrationState,
)

from .history import (
    ActionArbitrationHistory,
)

from .lineage import (
    ActionArbitrationLineage,
)

from .plan import (
    ActionArbitrationPlan,
    ActionArbitrationStageKind,
)

from .coverage import (
    ActionArbitrationComparisonCoverage,
)