# Gordon Executive Decision Core - Phase 4.4.10A
# ================================================

"""
Executive Decision Core Types and Classification.

This module defines the core decision types that represent executive
semantic commitments.


DECISION TYPES OVERVIEW
=======================

    ExecutiveDecision (abstract base)
           |
     +-----+-----+
     |           |
     v           v
Recommendation  Commitment
     |
     v
DecisionRevision


EXECUTIVE DECISION DEFINITION
=============================

An Executive Decision is an immutable semantic commitment describing
an intended future course of behavior under bounded operational conditions.

Key properties:
    - Immutable (never changes after creation)
    - Runtime-neutral (no execution state)
    - Deterministic (equal inputs produce equivalent representations)
    - Serializable (can be stored without runtime context)


ARCHITECTURAL LAWS
==================

E-001: Every Executive Decision possesses exactly one immutable Identity.
E-002: Every Executive Decision exists independently of runtime execution.
E-003: Every Executive Decision remains serializable without runtime state.
E-004: Executive Decisions shall never execute behavior.
E-005: Executive Decisions shall never invoke external capabilities.
E-006: Executive Decisions shall never contain executable code.

E-025: Every Executive Decision is immutable.
E-026: Identity survives every revision.
E-027: Revisions preserve semantic continuity.
E-028: Replacement creates a new Decision Identity.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Tuple, Literal
from enum import Enum, auto


# =============================================================================
# DECISION KINDS - Semantic categories of decisions
# =============================================================================

class DecisionKind(Enum):
    """
    Kinds of Executive Decisions.
    
    These classify the executive nature of the commitment. Kinds are semantic
    categories, not execution modes.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Strategic level decisions
    STRATEGIC = "strategic"
    """High-level organizational direction and long-term objectives."""
    
    OPERATIONAL = "operational"
    """Day-to-day operations and workflow management."""
    
    TACTICAL = "tactical"
    """Short-term actions to achieve strategic goals."""
    
    EXECUTIVE = "executive"
    """Executive-level commitments and authorizations."""
    
    # Administrative decisions
    ADMINISTRATIVE = "administrative"
    """Organizational and administrative matters."""
    
    RESOURCE = "resource"
    """Resource allocation and management decisions."""
    
    # Behavioral decisions
    BEHAVIORAL = "behavioral"
    """Behavioral patterns and responses."""
    
    # Domain-specific
    POLICY = "policy"
    """Policy definition and modification."""
    
    SECURITY = "security"
    """Security policy and enforcement decisions."""
    
    LEARNING = "learning"
    """Learning and adaptation decisions."""
    
    RECOVERY = "recovery"
    """Error recovery and failure response."""
    
    PLANNING = "planning"
    """Planning artifact creation and modification."""
    
    COMMUNICATION = "communication"
    """Communication strategy and message dispatch."""
    
    MONITORING = "monitoring"
    """Observation and monitoring configuration."""
    
    MAINTENANCE = "maintenance"
    """System maintenance and optimization."""


# =============================================================================
# DECISION STATES - Lifecycle positions
# =============================================================================

class DecisionState(Enum):
    """
    States in the Executive Decision lifecycle.
    
    State never describes runtime progress. It describes semantic position
    within the decision's existence.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Pre-commitment states
    DRAFT = "draft"
    """Initial formulation, not yet submitted."""
    
    CANDIDATE = "candidate"
    """Candidate for consideration, not yet recommended."""
    
    RECOMMENDED = "recommended"
    """Reviewed and recommended for commitment."""
    
    APPROVED = "approved"
    """Approved by authority, awaiting formal commitment."""
    
    # Commitment states
    COMMITTED = "committed"
    """Formally committed to executive state."""
    
    # Post-commitment states
    SUSPENDED = "suspended"
    """Temporarily suspended but not terminated."""
    
    RESTORED = "restored"
    """Restored after suspension."""
    
    REPLACED = "replaced"
    """Superseded by a new decision identity."""
    
    COMPLETED = "completed"
    """Objectives achieved, natural conclusion."""
    
    TERMINATED = "terminated"
    """Terminated before completion (abnormal)."""
    
    ARCHIVED = "archived"
    """Archived for historical reference."""


# =============================================================================
# DECISION HORIZONS - Temporal persistence expectations
# =============================================================================

class DecisionHorizon(Enum):
    """
    Temporal persistence horizons for decisions.
    
    Horizon answers: "How long should this commitment remain valid?"
    
    Note: This is NOT about execution duration but semantic validity period.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    IMMEDIATE = "immediate"
    """Valid until next executive evaluation cycle."""
    
    SHORT = "short"
    """Valid for minutes to hours of operation."""
    
    MEDIUM = "medium"
    """Valid for hours to days of operation."""
    
    LONG = "long"
    """Valid for days to weeks of operation."""
    
    PERSISTENT = "persistent"
    """Valid until explicitly replaced or terminated."""


# =============================================================================
# DECISION STABILITY - Expected volatility levels
# =============================================================================

class DecisionStability(Enum):
    """
    Stability levels for decisions.
    
    Stability describes the expected volatility of the commitment. Higher
    stability indicates less expected revision frequency.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    EXPLORATORY = "exploratory"
    """Highly provisional, likely to change."""
    
    TENTATIVE = "tentative"
    """Initial commitment, subject to confirmation."""
    
    PROVISIONAL = "provisional"
    """Based on current evidence, awaiting validation."""
    
    CONDITIONAL = "conditional"
    """Contingent on specific conditions being met."""
    
    STABLE = "stable"
    """Well-considered and expected to persist."""
    
    PERSISTENT = "persistent"
    """Strong commitment with minimal expected revision."""
    
    IRREVERSIBLE = "irreversible"
    """Effectively permanent; requires exceptional circumstances for change."""


# =============================================================================
# EXECUTIVE DECISION - Abstract base class
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecision:
    """
    Abstract base class for all Executive Decision types.
    
    This is the semantic root type. All concrete decision types derive from it.
    
    Runtime-neutral: Yes
    Executable: No
    
    Properties:
        identity_id: Permanent identifier across all revisions
        kind: Semantic category of the decision
        state: Current lifecycle position
        horizon: Expected temporal validity
        stability: Expected volatility level
        
    Invariants:
        - Always immutable
        - Never contains runtime state
        - Always serializable without execution context
        - Always has complete provenance
    """
    
    identity_id: str = field(default="")
    """Permanent identifier shared by all revisions of this decision."""
    
    kind: DecisionKind = DecisionKind.OPERATIONAL
    """Semantic category of the decision."""
    
    state: DecisionState = DecisionState.DRAFT
    """Current lifecycle position."""
    
    horizon: DecisionHorizon = DecisionHorizon.MEDIUM
    """Expected temporal validity period."""
    
    stability: DecisionStability = DecisionStability.PROVISIONAL
    """Expected volatility level."""
    
    @property
    def is_executive_decision(self) -> bool:
        """Return True for all executive decisions."""
        return True
    
    @property
    def can_be_revised(self) -> bool:
        """
        Check if this decision can be revised.
        
        A decision can be revised if it is not in a final state.
        """
        return self.state not in (
            DecisionState.COMPLETED,
            DecisionState.TERMINATED,
            DecisionState.ARCHIVED,
        )
    
    @property
    def can_be_committed(self) -> bool:
        """Check if this decision can be committed."""
        return self.state in (
            DecisionState.DRAFT,
            DecisionState.CANDIDATE,
            DecisionState.RECOMMENDED,
            DecisionState.APPROVED,
        )
    
    @classmethod
    def from_revision(cls, revision: "DecisionRevision") -> "ExecutiveDecision":
        """
        Create a decision from its revision.
        
        This extracts the semantic content while preserving identity.
        """
        return cls(
            identity_id=revision.identity_id,
            kind=revision.kind,
            state=revision.state,
            horizon=revision.horizon,
            stability=revision.stability,
        )


# =============================================================================
# DECISION REVISION - Semantic update record
# =============================================================================

@dataclass(frozen=True)
class DecisionRevision:
    """
    Immutable record of a semantic revision to an Executive Decision.
    
    A revision represents an updated understanding of the same decision.
    It never replaces identity; it extends it.
    
    Runtime-neutral: Yes
    Executable: No
    
    Example:
        >>> identity = DecisionIdentity.generate()
        >>> revision1 = DecisionRevision(
        ...     identity_id=identity.identity_id,
        ...     revision_number=1,
        ...     state=DecisionState.DRAFT
        ... )
        >>> revision2 = DecisionRevision(
        ...     identity_id=identity.identity_id,
        ...     revision_number=2,
        ...     parent_revision_id=revision1.revision_id,
        ...     state=DecisionState.RECOMMENDED
        ... )
    """
    
    identity_id: str = field(default="")
    """The decision identity this revision belongs to."""
    
    revision_number: int = 1
    """Sequential number within the identity's revision history."""
    
    parent_revision_id: Optional[str] = None
    """The revision this one directly updates (if any)."""
    
    kind: DecisionKind = DecisionKind.OPERATIONAL
    """Semantic category of the decision."""
    
    state: DecisionState = DecisionState.DRAFT
    """Current lifecycle position after this revision."""
    
    horizon: DecisionHorizon = DecisionHorizon.MEDIUM
    """Expected temporal validity period."""
    
    stability: DecisionStability = DecisionStability.PROVISIONAL
    """Expected volatility level."""
    
    @property
    def is_revision(self) -> bool:
        """Return True for all revisions."""
        return True
    
    @property
    def revision_id(self) -> str:
        """
        Generate a unique ID for this revision instance.
        
        This combines identity and revision number to form a unique
        reference to this specific snapshot in the revision history.
        """
        return f"{self.identity_id}:v{self.revision_number}"
    
    @property
    def lineage_path(self) -> Tuple[str, ...]:
        """
        Return the complete lineage path from root to this revision.
        
        This provides a traceable history of all revisions in sequence.
        """
        if self.parent_revision_id:
            return (self.identity_id, self.revision_id)
        return (self.identity_id,)
    
    @classmethod
    def initial(cls, identity: "DecisionIdentity") -> "DecisionRevision":
        """Create the first revision for a new decision."""
        return cls(
            identity_id=identity.identity_id,
            revision_number=1,
        )
    
    @classmethod
    def from_decision(cls, decision: ExecutiveDecision) -> "DecisionRevision":
        """
        Create a revision from an existing decision.
        
        This creates revision 1 from the initial decision state.
        """
        return cls(
            identity_id=decision.identity_id,
            revision_number=1,
            kind=decision.kind,
            state=decision.state,
            horizon=decision.horizon,
            stability=decision.stability,
        )


# =============================================================================
# DECISION COMMITMENT - Authoritative acceptance record
# =============================================================================

@dataclass(frozen=True)
class DecisionCommitment:
    """
    Record of authoritative acceptance of a decision recommendation.
    
    A commitment becomes part of Executive State. Commitments constrain
    future cognition until superseded by another valid executive commitment.
    
    Runtime-neutral: Yes
    Executable: No
    
    Key properties:
        - Commits to the semantic content of a decision
        - Constrains future executive processing
        - Is itself immutable and cannot be modified
        - Can only be superseded by a new commitment
        
    Example:
        >>> recommendation = DecisionRecommendation(
        ...     identity_id="decision_abc123",
        ...     kind=DecisionKind.OPERATIONAL,
        ...     state=DecisionState.RECOMMENDED,
        ... )
        >>> commitment = DecisionCommitment.from_recommendation(recommendation)
        >>> assert commitment.state == DecisionState.COMMITTED
    """
    
    identity_id: str = field(default="")
    """The decision identity being committed."""
    
    revision_number: int = 1
    """Revision number that was accepted."""
    
    committed_at_utc: float = field(default_factory=lambda: 0.0)
    """Timestamp when the commitment was made."""
    
    committing_authority_id: Optional[str] = None
    """ID of the authority that made the commitment."""
    
    @property
    def is_commitment(self) -> bool:
        """Return True for all commitments."""
        return True
    
    @property
    def commitment_id(self) -> str:
        """Generate a unique ID for this commitment instance."""
        return f"commitment_{self.identity_id}:v{self.revision_number}"
    
    @classmethod
    def from_revision(cls, revision: DecisionRevision) -> "DecisionCommitment":
        """
        Create a commitment from an accepted revision.
        
        This transforms a decision revision into a committed state.
        """
        import time
        return cls(
            identity_id=revision.identity_id,
            revision_number=revision.revision_number,
            committed_at_utc=time.time(),
        )
    
    @classmethod
    def from_recommendation(cls, recommendation: "DecisionRecommendation") -> "DecisionCommitment":
        """
        Create a commitment from a decision recommendation.
        
        This is the canonical path for accepting recommendations.
        """
        import time
        return cls(
            identity_id=recommendation.identity_id,
            revision_number=recommendation.revision_number,
            committed_at_utc=time.time(),
            committing_authority_id=recommendation.authority_id,
        )


# =============================================================================
# DECISION RECOMMENDATION - Advisory proposal record
# =============================================================================

@dataclass(frozen=True)
class DecisionRecommendation:
    """
    Record of an evaluated decision proposal for executive consideration.
    
    Recommendations remain advisory. They possess no behavioral authority
    until converted to commitments.
    
    Runtime-neutral: Yes
    Executable: No
    
    Example:
        >>> recommendation = DecisionRecommendation(
        ...     identity_id="decision_abc123",
        ...     kind=DecisionKind.OPERATIONAL,
        ...     state=DecisionState.RECOMMENDED,
        ... )
        >>> # Downstream system evaluates and converts to commitment
        >>> commitment = DecisionCommitment.from_recommendation(recommendation)
    """
    
    identity_id: str = field(default="")
    """The decision identity being recommended."""
    
    revision_number: int = 1
    """Revision number of the recommendation."""
    
    state: DecisionState = DecisionState.RECOMMENDED
    """Current lifecycle position."""
    
    authority_id: Optional[str] = None
    """ID of the evaluating authority (if any)."""
    
    @property
    def is_recommendation(self) -> bool:
        """Return True for all recommendations."""
        return True
    
    @classmethod
    def from_decision(cls, decision: ExecutiveDecision) -> "DecisionRecommendation":
        """
        Create a recommendation from an executive decision.
        
        This represents the decision as a proposal for commitment.
        """
        return cls(
            identity_id=decision.identity_id,
            revision_number=1,
            state=DecisionState.RECOMMENDED,
        )


# =============================================================================
# DECISION VALIDATION - Validation utilities
# =============================================================================

class DecisionValidation:
    """
    Static validation utilities for Executive Decisions.
    
    Runtime-neutral: Yes
    Executable: No
    
    All methods are pure and deterministic.
    """
    
    @staticmethod
    def is_valid_state_transition(
        from_state: DecisionState,
        to_state: DecisionState,
    ) -> bool:
        """
        Check if a state transition is semantically valid.
        
        This enforces the decision lifecycle constraints without any
        runtime dependencies.
        
        Valid transitions:
            DRAFT -> CANDIDATE, RECOMMENDED, TERMINATED
            CANDIDATE -> RECOMMENDED, TERMINATED, ARCHIVED
            RECOMMENDED -> APPROVED, TERMINATED, DRAFT (rework)
            APPROVED -> COMMITTED, TERMINATED, DRAFT (rework)
            COMMITTED -> SUSPENDED, REPLACED, COMPLETED
            SUSPENDED -> RESTORED, TERMINATED, REPLACED
            RESTORED -> COMMITTED, REPLACED
            REPLACED -> ARCHIVED
            COMPLETED -> ARCHIVED
            TERMINATED -> ARCHIVED
            ARCHIVED -> (no transitions)
        """
        valid_transitions = {
            DecisionState.DRAFT: {
                DecisionState.CANDIDATE,
                DecisionState.RECOMMENDED,
                DecisionState.TERMINATED,
            },
            DecisionState.CANDIDATE: {
                DecisionState.RECOMMENDED,
                DecisionState.TERMINATED,
                DecisionState.ARCHIVED,
            },
            DecisionState.RECOMMENDED: {
                DecisionState.APPROVED,
                DecisionState.TERMINATED,
                DecisionState.DRAFT,  # Rework
            },
            DecisionState.APPROVED: {
                DecisionState.COMMITTED,
                DecisionState.TERMINATED,
                DecisionState.DRAFT,  # Rework
            },
            DecisionState.COMMITTED: {
                DecisionState.SUSPENDED,
                DecisionState.REPLACED,
                DecisionState.COMPLETED,
            },
            DecisionState.SUSPENDED: {
                DecisionState.RESTORED,
                DecisionState.TERMINATED,
                DecisionState.REPLACED,
            },
            DecisionState.RESTORED: {
                DecisionState.COMMITTED,
                DecisionState.REPLACED,
            },
            DecisionState.REPLACED: {
                DecisionState.ARCHIVED,
            },
            DecisionState.COMPLETED: {
                DecisionState.ARCHIVED,
            },
            DecisionState.TERMINATED: {
                DecisionState.ARCHIVED,
            },
            DecisionState.ARCHIVED: set(),  # No transitions from archived
        }
        
        return to_state in valid_transitions.get(from_state, set())