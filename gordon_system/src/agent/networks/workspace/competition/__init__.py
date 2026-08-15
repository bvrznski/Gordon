# Workspace Competition Semantics
# ================================

"""
Canonical Workspace Competition definitions.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - External time providers only
    - Bounded collections
    - Semantic-time preservation

COMPETITION PIPELINE:
    
    EvaluatedWorkspaceCandidatePool
            ↓
    Competition Request
            ↓
    Competition Context
            ↓
    Eligibility Review
            ↓
    Constraint Resolution
            ↓
    Competition
            ↓
    Competition Frontier
            ↓
    Winner Selection
            ↓
    Coalition Formation
            ↓
    WorkspaceSelectionOutcome

Semantics stops here.

No broadcast, transport, scheduling, or execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum

# =============================================================================
# IDENTITY TYPES - Immutable references
# =============================================================================

WorkspaceCompetitionIdentity = str
"""Unique identifier for a workspace competition instance."""

WorkspaceCompetitionRevision = int
"""Monotonically increasing revision number for competitions."""

WorkspaceCompetitionReference = str
"""Immutable reference to Workspace Competition."""


# =============================================================================
# COMPETITION PURPOSE
# =============================================================================

class WorkspaceCompetitionPurpose(Enum):
    """Canonical competition purposes."""
    
    GLOBAL_SELECTION = "global_selection"
    COALITION_FORMATION = "coalition_formation"
    CONFLICT_RESOLUTION = "conflict_resolution"
    ELIGIBILITY_REVIEW = "eligibility_review"
    REEVALUATION = "reevaluation"


# =============================================================================
# COMPETITION REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCompetitionRequest:
    """Immutable request to initiate competition."""
    
    identity: str
    revision: int
    candidate_pool_ref: str
    context_ref: str
    purpose: WorkspaceCompetitionPurpose
    scope: Tuple[str, ...] = field(default_factory=tuple)
    authority_ref: str = ""
    hard_constraints: Tuple[str, ...] = field(default_factory=tuple)
    semantic_time_ref: str = "semantic_time_origin"
    privacy_class: str = "internal_only"
    provenance_ref: str = ""


# =============================================================================
# COMPETITION CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCompetitionContext:
    """Immutable context for competition."""
    
    source_network: str = ""
    correlation_id: str = ""
    causation_id: Optional[str] = None
    task_context: Optional[str] = None
    goal_context: Optional[str] = None
    decision_context: Optional[str] = None
    executive_context: Optional[str] = None
    motivation_context: Optional[str] = None
    temporal_context: Optional[str] = None
    reasoning_context: Optional[str] = None
    semantic_domain: str = ""
    audience_type: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# COMPETITION SCOPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCompetitionScope:
    """Immutable scope specification for competition."""
    
    target_audiences: Tuple[str, ...] = field(default_factory=tuple)
    minimum_confidence: float = 0.5
    broadcast_depth: int = 3
    disclosure_level: str = "internal_only"
    authority_constraints: Tuple[str, ...] = field(default_factory=tuple)
    privacy_classification: str = "internal_only"
    visibility_limitations: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# COMPETITION CANDIDATE (Competition View)
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCompetitionCandidate:
    """Competition view of a candidate."""
    
    candidate_identity: str
    candidate_revision: int
    candidate_reference: str
    evaluation_score: float
    evaluation_confidence: float = 1.0
    evaluation_uncertainty: float = 0.0
    dimensions: Tuple[Tuple[str, float], ...] = field(default_factory=tuple)
    hard_constraints_violated: Tuple[str, ...] = field(default_factory=tuple)
    is_eligible: bool = True
    semantic_time_ref: str = ""
    provenance_ref: str = ""

    @property
    def effective_score(self) -> float:
        """Calculate effective score considering uncertainty."""
        adjusted = self.evaluation_score * self.evaluation_confidence
        return max(0.0, min(1.0, adjusted))


# =============================================================================
# COMPETITION FRONTIER
# =============================================================================

WorkspaceFrontierIdentity = str
WorkspaceFrontierRevision = int
WorkspaceFrontierSnapshot = Tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WorkspaceCompetitionFrontier:
    """Immutable frontier containing eligible candidates after constraint filtering."""
    
    identity: WorkspaceFrontierIdentity
    revision: WorkspaceFrontierRevision
    competition_ref: str
    candidates: Tuple[WorkspaceCompetitionCandidate, ...]
    created_at_semantic_time: str
    total_candidates_evaluated: int
    candidates_excluded_by_hard_constraints: Tuple[str, ...] = field(default_factory=tuple)
    compatible_pairs: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    incompatible_pairs: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)

    @property
    def frontier_size(self) -> int:
        return len(self.candidates)

    @property
    def has_candidates(self) -> bool:
        return len(self.candidates) > 0


# =============================================================================
# WINNER SEMANTICS
# =============================================================================

WorkspaceWinnerIdentity = str
WorkspaceWinnerRevision = int
WorkspaceWinnerReference = str


@dataclass(frozen=True, slots=True)
class WorkspaceWinner:
    """Immutable semantic artifact representing a selected winner."""
    
    identity: WorkspaceWinnerIdentity
    revision: WorkspaceWinnerRevision
    candidate_reference: str
    evaluation_ref: str
    competition_ref: str
    selection_order: int
    selection_score: float
    selection_confidence: float
    selection_uncertainty: float
    justification: str
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    semantic_time_ref: str = ""
    provenance_ref: str = ""


# =============================================================================
# COALITION SEMANTICS
# =============================================================================

WorkspaceCoalitionIdentity = str
WorkspaceCoalitionRevision = int
WorkspaceCoalitionMemberRef = str


@dataclass(frozen=True, slots=True)
class WorkspaceCoalition:
    """Immutable semantic artifact representing a coalition of winners."""
    
    identity: WorkspaceCoalitionIdentity
    revision: WorkspaceCoalitionRevision
    competition_ref: str
    members: Tuple[WorkspaceWinner, ...]
    coalition_type: str = "singleton"
    compatibility_status: str = "compatible"
    justification: str = ""
    compatibility_analysis: Tuple[str, ...] = field(default_factory=tuple)
    conflicts_resolved: Tuple[str, ...] = field(default_factory=tuple)
    semantic_time_ref: str = ""
    provenance_ref: str = ""

    @property
    def member_count(self) -> int:
        return len(self.members)

    @property
    def is_singleton(self) -> bool:
        return self.member_count == 1


# =============================================================================
# COMPATIBILITY TYPES
# =============================================================================

class WorkspaceCompatibilityKind(Enum):
    """Canonical compatibility relationships between candidates."""
    
    COMPATIBLE = "compatible"
    COMPLEMENTARY = "complementary"
    INDEPENDENT = "independent"
    MUTUALLY_EXCLUSIVE = "mutually_exclusive"
    DEPENDENT = "dependent"
    CONFLICTING = "conflicting"
    REDUNDANT = "redundant"
    DUPLICATE = "duplicate"


# =============================================================================
# CONFLICT TYPES
# =============================================================================

class WorkspaceConflictKind(Enum):
    """Canonical conflict types between candidates."""
    
    DIRECT_CONFLICT = "direct_conflict"
    RESOURCE_CONFLICT = "resource_conflict"
    ATTENTION_CONFLICT = "attention_conflict"
    POLICY_CONFLICT = "policy_conflict"
    SECURITY_CONFLICT = "security_conflict"
    TEMPORAL_CONFLICT = "temporal_conflict"
    SEMANTIC_CONFLICT = "semantic_conflict"
    OWNERSHIP_CONFLICT = "ownership_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    MOTIVATIONAL_CONFLICT = "motivational_conflict"
    EXECUTIVE_CONFLICT = "executive_conflict"


# =============================================================================
# SELECTION OUTCOME
# =============================================================================

WorkspaceSelectionOutcomeIdentity = str
WorkspaceSelectionOutcomeRevision = int


@dataclass(frozen=True, slots=True)
class WorkspaceSelectionReason:
    """Immutable semantic reason for a selection decision."""
    
    reason_kind: str
    justification: str
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 1.0
    uncertainty: float = 0.0


@dataclass(frozen=True, slots=True)
class WorkspaceSelectionEvidence:
    """Immutable evidence supporting selection decisions."""
    
    evidence_type: str
    value: float
    source_ref: str
    semantic_time_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceSelectionJustification:
    """Immutable justification for a selection outcome."""
    
    justification_kind: str
    explanation: str
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 1.0
    uncertainty: float = 0.0


@dataclass(frozen=True, slots=True)
class WorkspaceSelectionOutcome:
    """Immutable semantic artifact representing the final selection outcome."""
    
    identity: WorkspaceSelectionOutcomeIdentity
    revision: WorkspaceSelectionOutcomeRevision
    competition_ref: str
    
    # Required tuples (no defaults)
    winners: Tuple[WorkspaceWinner, ...]
    rejected_candidates: Tuple[str, ...] = field(default_factory=tuple)
    deferred_candidates: Tuple[str, ...] = field(default_factory=tuple)
    
    # Tuples with defaults
    coalitions: Tuple[WorkspaceCoalition, ...] = field(default_factory=tuple)
    hard_exclusions: Tuple[str, ...] = field(default_factory=tuple)
    selection_evidence: Tuple[WorkspaceSelectionEvidence, ...] = field(
        default_factory=tuple
    )
    
    # Complex types with defaults (must come last in dataclass)
    selection_justification: WorkspaceSelectionJustification = None  # type: ignore
    semantic_time_ref: str = ""
    provenance_ref: str = ""

    @property
    def winner_count(self) -> int:
        return len(self.winners)

    @property
    def coalition_count(self) -> int:
        return len(self.coalitions)


# =============================================================================
# HISTORY AND LINEAGE
# =============================================================================

@dataclass(frozen=True, slots=True)
class CompetitionHistoryEntry:
    """History entry for competition events."""
    
    entry_id: str
    entry_type: str
    timestamp_semantic_time: str
    data_ref: Optional[str] = None
    metadata: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class CompetitionHistory:
    """Immutable history record for a competition."""
    
    identity: str
    revision: int
    competition_ref: str
    entries: Tuple[CompetitionHistoryEntry, ...]
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class LineageNode:
    """Node in a competition lineage graph."""
    
    node_id: str
    node_kind: str
    reference: str
    semantic_time_ref: str = ""


@dataclass(frozen=True, slots=True)
class LineageRelation:
    """Relation between lineage nodes."""
    
    relation_id: str
    relation_type: str
    source_node_id: str
    target_node_id: str
    metadata: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class CompetitionLineage:
    """Immutable lineage record for a competition."""
    
    identity: str
    revision: int
    competition_ref: str
    nodes: Tuple[LineageNode, ...]
    relations: Tuple[LineageRelation, ...]
    provenance_ref: str = ""


# =============================================================================
# INVALIDATION AND CONTINUATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class CompetitionInvalidation:
    """Immutable record of competition invalidation."""
    
    invalidation_id: str
    invalidation_kind: str
    invalidating_ref: str
    invalidated_competition_ref: str
    reason: str
    semantic_time_ref: str = ""


@dataclass(frozen=True, slots=True)
class CompetitionContinuation:
    """Immutable record of a semantic continuation request."""
    
    continuation_id: str
    continuation_kind: str
    target_ref: Optional[str] = None
    reason: str = ""
    semantic_time_ref: str = ""


# =============================================================================
# ARCHITECTURAL LAWS
# =============================================================================

ARCHITECTURAL_LAWS = """
COMPETITION CONSUMERS:
    - Competition consumes evaluated Candidates
    - Competition never mutates Candidates
    - Competition never mutates Evaluations
    
COMPETITION PRODUCERS:
    - Competition produces Winners
    - Competition produces Coalitions  
    - Competition produces Selection Outcomes

RUNTIME BOUNDARY:
    - Competition never performs Broadcast
    - Competition never executes Actions
    - Competition never schedules tasks
    - Competition never transports messages

SEMANTIC INVARIANTS:
    - Competition preserves provenance
    - Competition preserves ownership
    - Competition preserves authority
    - Hard constraints dominate scoring
    
COALITION SEMANTICS:
    - Coalitions are explicit (never implicit)
    - Selection Outcomes are immutable
    - Replay produces identical outcomes
"""

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Identity types
    "WorkspaceCompetitionIdentity",
    "WorkspaceCompetitionRevision", 
    "WorkspaceCompetitionReference",
    
    # Competition purpose
    "WorkspaceCompetitionPurpose",
    
    # Core request/context/scope
    "WorkspaceCompetitionRequest",
    "WorkspaceCompetitionContext",
    "WorkspaceCompetitionScope",
    
    # Competition candidate
    "WorkspaceCompetitionCandidate",
    
    # Frontier
    "WorkspaceFrontierIdentity",
    "WorkspaceFrontierRevision",
    "WorkspaceFrontierSnapshot",
    "WorkspaceCompetitionFrontier",
    
    # Winner
    "WorkspaceWinnerIdentity",
    "WorkspaceWinnerRevision",
    "WorkspaceWinnerReference",
    "WorkspaceWinner",
    
    # Coalition
    "WorkspaceCoalitionIdentity",
    "WorkspaceCoalitionRevision",
    "WorkspaceCoalitionMemberRef",
    "WorkspaceCoalition",
    
    # Compatibility and conflict
    "WorkspaceCompatibilityKind",
    "WorkspaceConflictKind",
    
    # Selection outcome
    "WorkspaceSelectionOutcomeIdentity",
    "WorkspaceSelectionOutcomeRevision",
    "WorkspaceSelectionReason", 
    "WorkspaceSelectionEvidence",
    "WorkspaceSelectionJustification",
    "WorkspaceSelectionOutcome",
    
    # History and Lineage
    "CompetitionHistoryEntry",
    "CompetitionHistory",
    "LineageNode",
    "LineageRelation",
    "CompetitionLineage",
    
    # Invalidation and continuation
    "CompetitionInvalidation",
    "CompetitionContinuation",
]