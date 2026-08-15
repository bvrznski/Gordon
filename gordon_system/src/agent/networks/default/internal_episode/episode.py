# Internal Episode Core Model
# ===========================

"""
Canonical InternalEpisode aggregate model.

InternalEpisode is an immutable-identity, bounded-lifecycle coordination unit
representing one internally generated cognitive undertaking performed using a
specific InternalContext.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


# =============================================================================
# IDENTITY TYPES
# =============================================================================

InternalEpisodeId = str
"""Stable identifier for an internal episode instance."""

InternalEpisodeRevision = int
"""Monotonically increasing revision number for the episode."""


# =============================================================================
# LIFECYCLE MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalEpisodeLifecycle:
    """
    Immutable record of episode lifecycle state.
    
    Lifecycle represents semantic coordination state, not runtime execution state.
    Core and Execution handle actual runtime mechanics.
    
    TRANSITIONS:
        PROPOSED -> VALIDATED -> READY -> ACTIVE
        ACTIVE -> WAITING_FOR_INPUT, WAITING_FOR_CAPABILITY, SUSPENDED, COMPLETING
        ACTIVE -> FAILED, CANCELLED, EXPIRED
        COMPLETING -> COMPLETED
        
    TERMINAL STATES:
        COMPLETED, FAILED, CANCELLED, EXPIRED, SUPERSEDED
    """
    
    state: str  # InternalEpisodeLifecycle.*
    """Current lifecycle state."""
    
    transition_id: Optional[str] = None
    """ID of the most recent transition."""
    
    reason: Optional[str] = None
    """Reason for current state (human-readable)."""
    
    @classmethod
    def proposed(cls) -> InternalEpisodeLifecycle:
        """Create a PROPOSED lifecycle state."""
        return cls(
            state="proposed",
            transition_id=None,
            reason="Initial request received",
        )
    
    @classmethod
    def validated(cls, transition_id: str, reason: Optional[str] = None) -> InternalEpisodeLifecycle:
        """Create a VALIDATED lifecycle state."""
        return cls(
            state="validated",
            transition_id=transition_id,
            reason=reason or "Request, purpose, scope, and context binding are valid",
        )
    
    @classmethod
    def ready(cls, transition_id: str) -> InternalEpisodeLifecycle:
        """Create a READY lifecycle state."""
        return cls(
            state="ready",
            transition_id=transition_id,
            reason="Episode may be processed when Execution and Core permit",
        )
    
    @classmethod
    def active(cls, transition_id: str) -> InternalEpisodeLifecycle:
        """Create an ACTIVE lifecycle state."""
        return cls(
            state="active",
            transition_id=transition_id,
            reason="Bounded episode progression is currently being coordinated",
        )
    
    @classmethod
    def completing(cls, transition_id: str) -> InternalEpisodeLifecycle:
        """Create a COMPLETING lifecycle state."""
        return cls(
            state="completing",
            transition_id=transition_id,
            reason="Outcome composition or final validation in progress",
        )
    
    @classmethod
    def completed(cls, transition_id: str) -> InternalEpisodeLifecycle:
        """Create a COMPLETED lifecycle state."""
        return cls(
            state="completed",
            transition_id=transition_id,
            reason="Valid terminal outcome produced",
        )
    
    @classmethod
    def failed(cls, transition_id: str, reason: Optional[str] = None) -> InternalEpisodeLifecycle:
        """Create a FAILED lifecycle state."""
        return cls(
            state="failed",
            transition_id=transition_id,
            reason=reason or "Terminated without valid successful outcome",
        )
    
    @classmethod
    def cancelled(cls, transition_id: str) -> InternalEpisodeLifecycle:
        """Create a CANCELLED lifecycle state."""
        return cls(
            state="cancelled",
            transition_id=transition_id,
            reason="Terminated by authority before normal completion",
        )
    
    @classmethod
    def expired(cls, transition_id: str) -> InternalEpisodeLifecycle:
        """Create an EXPIRED lifecycle state."""
        return cls(
            state="expired",
            transition_id=transition_id,
            reason="Context, scope, or deadline expired",
        )
    
    @classmethod
    def superseded(cls, transition_id: str) -> InternalEpisodeLifecycle:
        """Create a SUPERSEDED lifecycle state."""
        return cls(
            state="superseded",
            transition_id=transition_id,
            reason="Newer episode replaced this episode's purpose or authority",
        )


# =============================================================================
# EPISODE STATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalEpisodeState:
    """
    Immutable complete state snapshot of an internal episode.
    
    State contains all information needed to understand the current status
    of an episode without live runtime references.
    
    PROPERTIES:
        • lifecycle: Semantic coordination state
        • plan_step_ref: Current or last completed step (if any)
        • completed_steps: IDs of completed steps
        • pending_steps: IDs of pending steps
        • pending_capability_requests: IDs of requests awaiting results
        • received_results: IDs of capability results received
        • evidence_summary: Summary of evidence count and types
        • unresolved_conflicts: Count of unresolved conflicts
        • completion_progress: Fraction complete (0.0 to 1.0)
        • context_validity: Whether bound context is still valid
        • revision: Current episode revision number
        
    NOT INCLUDED:
        • Live coroutines, Futures, Tasks
        • Locks, queues, workers
        • Process or network handles
        • Model instances or providers
    """
    
    # Lifecycle state
    lifecycle: InternalEpisodeLifecycle
    
    # Plan tracking
    current_plan_step_id: Optional[str] = None
    """Current step being processed (if any)."""
    
    completed_steps: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of completed steps."""
    
    pending_steps: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of pending steps."""
    
    # Capability tracking
    pending_capability_requests: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of capability requests awaiting results."""
    
    received_results: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of capability results received."""
    
    # Evidence summary (counts only, not full items)
    evidence_item_count: int = 0
    """Total number of evidence items collected."""
    
    unresolved_conflicts: int = 0
    """Number of unresolved conflicts."""
    
    # Progress metrics
    completion_progress: float = 0.0
    """Fraction complete (0.0 to 1.0)."""
    
    # Context binding validity
    context_valid: bool = True
    """Whether bound context is still valid and fresh."""
    
    # Revision tracking
    revision: InternalEpisodeRevision = 1
    
    @classmethod
    def initial_state(
        cls,
        lifecycle: InternalEpisodeLifecycle,
        plan_step_ids: Tuple[str, ...],
    ) -> InternalEpisodeState:
        """
        Create an initial episode state.
        
        Args:
            lifecycle: Current lifecycle state
            plan_step_ids: IDs of all steps in the plan
            
        Returns:
            New InternalEpisodeState instance
        """
        return cls(
            lifecycle=lifecycle,
            pending_steps=plan_step_ids,
            revision=1,
        )
    
    @classmethod
    def completed_state(cls, outcome_id: str) -> InternalEpisodeState:
        """Create a completed state."""
        return cls(
            lifecycle=InternalEpisodeLifecycle.completed(outcome_id),
            evidence_item_count=0,
            unresolved_conflicts=0,
            completion_progress=1.0,
            revision=1,
        )


# =============================================================================
# PROVENANCE MODELS
# =============================================================================

@dataclass(frozen=True, slots=True)
class RequestProvenance:
    """
    Complete provenance record for an episode request.
    
    Tracks the origin and chain of custody for the request.
    """
    
    created_at_utc: datetime
    """When the request was created."""
    
    created_by: str  # InternalEpisodeRequester.*
    """Who/what created the request."""
    
    correlation_id: Optional[str] = None
    """Correlation ID for distributed tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID if this request results from another event."""
    
    parent_request_id: Optional[str] = None
    """ID of the parent request (if any)."""
    
    child_count: int = 0
    """Number of child requests derived from this one."""


@dataclass(frozen=True, slots=True)
class EpisodeProvenance:
    """
    Complete provenance record for an episode.
    
    Tracks how the episode came to be and its relationship to other episodes.
    """
    
    request_id: str
    """ID of the originating request."""
    
    created_at_utc: datetime
    """When the episode was created."""
    
    created_by: str  # InternalEpisodeRequester.*
    """Who/what caused the episode (usually DEFAULT_NETWORK)."""
    
    context_source: Optional[str] = None
    """Source of the bound context (e.g., 'memory_projection')."""
    
    parent_episode_id: Optional[str] = None
    """ID of parent episode (if derived from one)."""
    
    child_episode_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of child episodes derived from this one."""
    
    transition_count: int = 1
    """Number of lifecycle transitions recorded."""


# =============================================================================
# MAIN EPISODE AGGREGATE MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalEpisode:
    """
    Immutable canonical aggregate for internal cognitive coordination.
    
    An InternalEpisode represents one bounded internally generated cognitive
    undertaking performed using a specific InternalContext.
    
    WHAT IT ANSWERS:
        What bounded internally generated cognitive undertaking is being coordinated?
        
    WHAT IT DOES NOT ANSWER:
        Which runtime worker executes it?
        Which ExecutionThread should run?
        Which capability algorithm should be used internally?
        What final behavioral action should Gordon perform?
        What should enter persistent memory?
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-EPISODE-INV-001: Every InternalEpisode has exactly one stable identity
        DEFAULT-EPISODE-INV-002: Every InternalEpisode has exactly one explicit purpose
        DEFAULT-EPISODE-INV-003: Every InternalEpisode has one bounded scope
        DEFAULT-EPISODE-INV-004: Every InternalEpisode binds to one InternalContext revision at a time
        DEFAULT-EPISODE-INV-005: Context refresh is explicit
        DEFAULT-EPISODE-INV-006: InternalEpisode does not replace ExecutionThread
        DEFAULT-EPISODE-INV-007: InternalEpisode does not own runtime scheduling
        DEFAULT-EPISODE-INV-008: InternalEpisode does not implement capability algorithms
        DEFAULT-EPISODE-INV-009: Every episode has an explicit lifecycle state
        DEFAULT-EPISODE-INV-010: Every lifecycle transition is validated
        DEFAULT-EPISODE-INV-011: Every active episode has a valid plan or explicitly valid planless form
        DEFAULT-EPISODE-INV-012: Every capability request belongs to exactly one episode and one plan step
        DEFAULT-EPISODE-INV-013: Every accepted capability result references its request
        DEFAULT-EPISODE-INV-014: Every evidence item has provenance
        DEFAULT-EPISODE-INV-015: Evidence conflicts are never silently discarded
        DEFAULT-EPISODE-INV-016: Every terminal episode has exactly one terminal outcome
        DEFAULT-EPISODE-INV-017: Episode continuation is advisory
        DEFAULT-EPISODE-INV-018: Episode proposals do not directly mutate source systems
        DEFAULT-EPISODE-INV-019: Episode state is bounded
        DEFAULT-EPISODE-INV-020: Child-episode derivation is bounded
        
    PROPERTIES:
        • episode_id: Unique identifier (immutable, stable)
        • revision: Monotonically increasing revision number
        • created_at_utc: When the episode was created
        • updated_at_utc: When the episode state last changed
        
    CONTENT:
        • type: Category of internal cognition (InternalEpisodeType.*)
        • purpose: Concrete reason for this episode instance
        • scope: Bounded constraints on the episode
        • context_id: Bound context ID
        • context_revision: Bound context revision number
        
    COORDINATION:
        • lifecycle: Semantic coordination state
        • state: Complete state snapshot (plan steps, evidence counts, etc.)
        • plan: Declarative coordination plan
        • request: Original request that created the episode
        
    EVIDENCE AND OUTCOME:
        • evidence: Bounded collection of evidence items
        • outcome: Terminal result (if completed)
        
    RELATIONSHIPS:
        • parent_episode_id: Parent episode ID (if derived from one)
        • root_episode_id: Root ancestor episode ID
        • relationship: Relationship to parent (if any)
        
    CONFIDENCE AND PROVENANCE:
        • confidence: Structured confidence assessment
        • provenance: Complete provenance record
        
    NOT RESPONSIBLE FOR:
        • Executing reflection, imagination, simulation, etc.
        • Updating memory, identity, or other source data
        • Scheduling runtime execution
        • Allocating computational resources
        • Creating live worker tasks or threads
    """
    
    # Identity and revisioning (immutable-identity)
    episode_id: InternalEpisodeId
    """Unique identifier for this episode instance."""
    
    revision: InternalEpisodeRevision
    """Monotonically increasing revision number."""
    
    created_at_utc: datetime
    """When the episode was created."""
    
    updated_at_utc: datetime
    """When the episode state last changed."""
    
    # Definition (what this episode does)
    episode_type: str  # InternalEpisodeType.*
    """Category of internal cognition being performed."""
    
    purpose: str  # InternalEpisodePurpose.statement
    """Concrete reason for this episode instance."""
    
    scope: str  # Serialized InternalEpisodeScope as JSON-compatible dict or string reference
    """Bounded constraints on the episode (serialized)."""
    
    # Context binding
    context_id: str
    """Bound context ID."""
    
    context_revision: int
    """Bound context revision number at time of creation."""
    
    # Coordination state
    lifecycle: InternalEpisodeLifecycle
    """Semantic coordination state."""
    
    state: InternalEpisodeState
    """Complete state snapshot (plan, evidence counts, etc.)."""
    
    request_id: str
    """ID of the originating request."""
    
    plan_id: Optional[str] = None
    """ID of the active plan (if any)."""
    
    # Evidence tracking
    evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of evidence items collected."""
    
    conflict_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of conflicts detected."""
    
    outcome_id: Optional[str] = None
    """ID of terminal outcome (if completed)."""
    
    # Relationships
    parent_episode_id: Optional[InternalEpisodeId] = None
    """Parent episode ID (if derived from one)."""
    
    root_episode_id: InternalEpisodeId
    """Root ancestor episode ID."""
    
    relationship_kind: Optional[str] = None  # RelationshipKind.*
    """Relationship to parent (if any)."""
    
    # Quality assessment
    confidence: float = 0.5
    """Overall confidence level (0.0 to 1.0)."""
    
    completeness_status: str = "partial"
    """Completeness status (InternalOutcomeStatus.*)."""
    
    provenance: Optional[EpisodeProvenance] = None
    """Complete provenance record."""
    
    @classmethod
    def create_proposed(
        cls,
        episode_id: InternalEpisodeId,
        episode_type: str,
        purpose_statement: str,
        context_id: str,
        context_revision: int,
        request_id: str,
        root_episode_id: Optional[InternalEpisodeId] = None,
        parent_episode_id: Optional[InternalEpisodeId] = None,
        relationship_kind: Optional[str] = None,
    ) -> InternalEpisode:
        """
        Create a new episode in PROPOSED state.
        
        Args:
            episode_id: Unique identifier for the new episode
            episode_type: Category of internal cognition
            purpose_statement: Human-readable description of what this episode does
            context_id: Bound context ID
            context_revision: Bound context revision number
            request_id: ID of the originating request
            root_episode_id: Root ancestor episode ID (defaults to self)
            parent_episode_id: Parent episode ID if derived from another episode
            relationship_kind: Relationship kind if parent exists
            
        Returns:
            New InternalEpisode in PROPOSED state
        """
        now = datetime.utcnow()
        
        return cls(
            episode_id=episode_id,
            revision=1,
            created_at_utc=now,
            updated_at_utc=now,
            episode_type=episode_type,
            purpose=purpose_statement,
            scope="{}",
            context_id=context_id,
            context_revision=context_revision,
            lifecycle=InternalEpisodeLifecycle.proposed(),
            state=InternalEpisodeState.initial_state(
                lifecycle=InternalEpisodeLifecycle.proposed(),
                plan_step_ids=(),
            ),
            request_id=request_id,
            root_episode_id=root_episode_id or episode_id,
            parent_episode_id=parent_episode_id,
            relationship_kind=relationship_kind,
        )
    
    @classmethod
    def create_validated(
        cls,
        existing: InternalEpisode,
        transition_id: str,
        reason: Optional[str] = None,
    ) -> InternalEpisode:
        """
        Create a validated episode from an existing one.
        
        Args:
            existing: The PROPOSED episode to validate
            transition_id: ID of the validation transition
            reason: Reason for validation
            
        Returns:
            New InternalEpisode in VALIDATED state with incremented revision
        """
        now = datetime.utcnow()
        
        return cls(
            episode_id=existing.episode_id,
            revision=existing.revision + 1,
            created_at_utc=existing.created_at_utc,
            updated_at_utc=now,
            episode_type=existing.episode_type,
            purpose=existing.purpose,
            scope=existing.scope,
            context_id=existing.context_id,
            context_revision=existing.context_revision,
            lifecycle=InternalEpisodeLifecycle.validated(transition_id, reason),
            state=InternalEpisodeState.initial_state(
                lifecycle=InternalEpisodeLifecycle.validated(transition_id, reason),
                plan_step_ids=(),
            ),
            request_id=existing.request_id,
            root_episode_id=existing.root_episode_id,
            parent_episode_id=existing.parent_episode_id,
            relationship_kind=existing.relationship_kind,
        )
    
    def is_terminal(self) -> bool:
        """
        Check if this episode is in a terminal state.
        
        Returns:
            True if the episode has ended (completed, failed, cancelled, expired, superseded)
        """
        return self.lifecycle.state in {
            "completed",
            "failed",
            "cancelled",
            "expired",
            "superseded",
        }
    
    def can_produce_outcome(self) -> bool:
        """
        Check if this episode is eligible to produce an outcome.
        
        Episodes must be in ACTIVE or COMPLETING state and have a valid
        context binding to produce outcomes.
        
        Returns:
            True if the episode can produce an outcome
        """
        if self.is_terminal():
            return False
        
        if not self.state.context_valid:
            return False
        
        return self.lifecycle.state in {
            "active",
            "waiting_for_capability",
            "completing",
        }
    
    def is_root_episode(self) -> bool:
        """Check if this episode is a root (has no parent)."""
        return self.parent_episode_id is None


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def is_internal_episode(value: object) -> bool:
    """Check if a value is an InternalEpisode instance."""
    return isinstance(value, InternalEpisode)


def episode_state_key(episode: InternalEpisode) -> str:
    """
    Generate a state key for caching and lookup.
    
    The key combines episode_id and revision to enable efficient
    state management without storing full episodes.
    
    Args:
        episode: The episode to generate a key for
        
    Returns:
        State key string in format "episode_id:revision"
    """
    return f"{episode.episode_id}:{episode.revision}"