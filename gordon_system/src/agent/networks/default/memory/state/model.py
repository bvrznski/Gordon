# Memory Integration State Models
# ===============================

"""
Immutable state models for memory integration.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - Bounded state only
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# MEMORY INTEGRATION STATE KINDS
# =============================================================================

class MemoryIntegrationStateKind:
    """
    Canonical state kinds for memory integration episodes.
    
    States represent coordination progress through the episode lifecycle.
    """
    
    PENDING = "pending"
    READY = "ready"
    STARTED = "started"
    PROJECTION_REQUESTED = "projection_requested"
    PROJECTION_ACCEPTED = "projection_accepted"
    REFERENCE_NORMALIZED = "reference_normalized"
    RELEVANCE_ASSESSED = "relevance_assessed"
    ASSOCIATION_IDENTIFIED = "association_identified"
    LINK_PROPOSED = "link_proposed"
    CLUSTER_PROPOSED = "cluster_proposed"
    CONFLICT_RECORDED = "conflict_recorded"
    GAP_RECORDED = "gap_recorded"
    DUPLICATE_RECORDED = "duplicate_recorded"
    INCONSISTENCY_RECORDED = "inconsistency_recorded"
    CONSOLIDATION_CANDIDATE_CREATED = "consolidation_candidate_created"
    ABSTRACTION_CANDIDATE_CREATED = "abstraction_candidate_created"
    RETRIEVAL_CUE_PROPOSED = "retrieval_cue_proposed"
    UPDATE_PROPOSED = "update_proposed"
    CORRECTION_PROPOSED = "correction_proposed"
    OUTCOME_COMPOSED = "outcome_composed"
    WAITING = "waiting"
    SUSPENDED = "suspended"
    RESUMED = "resumed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


# =============================================================================
# MEMORY INTEGRATION STATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryIntegrationState:
    """
    Immutable state of a memory integration episode.
    
    This represents the coordination progress without storing full records.
    """
    
    active_episode_id: Optional[str] = None
    """Reference to active MemoryIntegrationEpisode."""
    
    ready_episode_ids: Tuple[str, ...] = field(default_factory=tuple)
    """References to episodes ready for execution."""
    
    waiting_episode_ids: Tuple[str, ...] = field(default_factory=tuple)
    """References to episodes waiting for information."""
    
    current_projection_revisions: Tuple[int, ...] = field(default_factory=tuple)
    """Current revision numbers of projections."""
    
    recent_purposes: Tuple[str, ...] = field(default_factory=tuple)
    """Summary of recent purposes."""
    
    recent_subjects: Tuple[str, ...] = field(default_factory=tuple)
    """Summary of recent subjects."""
    
    recent_product_digests: Tuple[str, ...] = field(default_factory=tuple)
    """Digests of recently generated products."""
    
    association_count: int = 0
    """Count of associations identified."""
    
    link_count: int = 0
    """Count of links established."""
    
    cluster_count: int = 0
    """Count of clusters formed."""
    
    unresolved_conflict_count: int = 0
    """Count of conflicts awaiting resolution."""
    
    unresolved_gap_count: int = 0
    """Count of gaps awaiting attention."""
    
    duplicate_candidate_count: int = 0
    """Count of duplicate candidates identified."""
    
    inconsistency_count: int = 0
    """Count of inconsistencies identified."""
    
    pending_proposal_count: int = 0
    """Count of pending proposals."""
    
    retrieval_round_count: int = 0
    """Count of retrieval rounds used."""
    
    context_revision: int = 1
    """Current InternalContext revision."""
    
    state_revision: int = 1
    """State revision number."""
    
    no_result_count: int = 0
    """Count of no-result outcomes."""
    
    @classmethod
    def initial(cls) -> MemoryIntegrationState:
        """Create an initial (empty) state."""
        return cls()
    
    def can_accept_more_projections(self, limit: int) -> bool:
        """Check if more projections can be accepted."""
        return len(self.current_projection_revisions) < limit


# =============================================================================
# STATE TRANSITION KINDS
# =============================================================================

class StateTransitionKind:
    """
    Canonical state transition kinds.
    """
    
    MEMORY_INTEGRATION_REQUESTED = "memory_integration_requested"
    MEMORY_INTEGRATION_VALIDATED = "memory_integration_validated"
    MEMORY_INTEGRATION_READY = "memory_integration_ready"
    MEMORY_INTEGRATION_STARTED = "memory_integration_started"
    MEMORY_PROJECTION_REQUESTED = "memory_projection_requested"
    MEMORY_PROJECTION_ACCEPTED = "memory_projection_accepted"
    MEMORY_REFERENCE_NORMALIZED = "memory_reference_normalized"
    MEMORY_RELEVANCE_ASSESSED = "memory_relevance_assessed"
    ASSOCIATION_IDENTIFIED = "association_identified"
    LINK_PROPOSED = "link_proposed"
    CLUSTER_PROPOSED = "cluster_proposed"
    CONFLICT_RECORDED = "conflict_recorded"
    GAP_RECORDED = "gap_recorded"
    DUPLICATE_RECORDED = "duplicate_recorded"
    INCONSISTENCY_RECORDED = "inconsistency_recorded"
    CONSOLIDATION_CANDIDATE_CREATED = "consolidation_candidate_created"
    ABSTRACTION_CANDIDATE_CREATED = "abstraction_candidate_created"
    RETRIEVAL_CUE_PROPOSED = "retrieval_cue_proposed"
    UPDATE_PROPOSED = "update_proposed"
    CORRECTION_PROPOSED = "correction_proposed"
    OUTCOME_COMPOSED = "outcome_composed"
    MEMORY_INTEGRATION_WAITING = "memory_integration_waiting"
    MEMORY_INTEGRATION_SUSPENDED = "memory_integration_suspended"
    MEMORY_INTEGRATION_RESUMED = "memory_integration_resumed"
    MEMORY_INTEGRATION_COMPLETED = "memory_integration_completed"
    MEMORY_INTEGRATION_FAILED = "memory_integration_failed"
    MEMORY_INTEGRATION_CANCELLED = "memory_integration_cancelled"
    MEMORY_INTEGRATION_EXPIRED = "memory_integration_expired"
    MEMORY_INTEGRATION_SUPERSEDED = "memory_integration_superseded"


# =============================================================================
# STATE TRANSITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class StateTransition:
    """
    Immutable state transition record.
    
    Each transition records a coordination step without runtime execution.
    """
    
    transition_id: str
    """Unique identifier for this transition."""
    
    from_state: str  # MemoryIntegrationStateKind.*
    """Source state."""
    
    to_state: str  # MemoryIntegrationStateKind.*
    """Target state."""
    
    kind: str  # StateTransitionKind.*
    """Kind of transition."""
    
    episode_id: str
    """ID of the episode transitioning."""
    
    timestamp_utc: str = ""
    """When the transition occurred (ISO format)."""
    
    metadata: Tuple[str, ...] = field(default_factory=tuple)
    """Additional metadata about this transition."""
    
    @classmethod
    def new(
        cls,
        from_state: str,
        to_state: str,
        kind: str,
        episode_id: str,
    ) -> StateTransition:
        """Create a new state transition."""
        return cls(
            transition_id=f"transition_{id(cls)}",
            from_state=from_state,
            to_state=to_state,
            kind=kind,
            episode_id=episode_id,
        )


# =============================================================================
# STATE SNAPSHOT
# =============================================================================

@dataclass(frozen=True, slots=True)
class StateSnapshot:
    """
    Immutable snapshot of memory integration state at a point in time.
    
    Used for debugging and audit purposes.
    """
    
    snapshot_id: str
    """Unique identifier for this snapshot."""
    
    timestamp_utc: str = ""
    """When the snapshot was taken (ISO format)."""
    
    state_kind: str = ""
    """Current state kind."""
    
    active_episode_id: Optional[str] = None
    """Active episode reference."""
    
    projection_revision_summaries: Tuple[str, ...] = field(default_factory=tuple)
    """Summaries of projection revisions."""
    
    history_summary: Tuple[str, ...] = field(default_factory=tuple)
    """Summary of recent transitions."""
    
    product_count: int = 0
    """Count of products generated."""
    
    @classmethod
    def from_state(
        cls,
        state: MemoryIntegrationState,
        timestamp_utc: str = "",
    ) -> StateSnapshot:
        """Create a snapshot from current state."""
        return cls(
            snapshot_id=f"snapshot_{id(cls)}",
            timestamp_utc=timestamp_utc or "unknown",
            state_kind="active",  # Simplified
            active_episode_id=state.active_episode_id,
        )


# =============================================================================
# HISTORY ENTRY
# =============================================================================

@dataclass(frozen=True, slots=True)
class HistoryEntry:
    """
    Immutable entry in memory integration history.
    
    Bounded history for debugging and audit.
    """
    
    entry_id: str
    """Unique identifier for this history entry."""
    
    timestamp_utc: str = ""
    """When the event occurred (ISO format)."""
    
    kind: str = "unknown"  # StateTransitionKind.* or other event kinds
    """Event kind."""
    
    episode_id: Optional[str] = None
    """Episode reference if applicable."""
    
    details: Tuple[str, ...] = field(default_factory=tuple)
    """Additional details about the event."""
    
    @classmethod
    def from_transition(
        cls,
        transition: StateTransition,
    ) -> HistoryEntry:
        """Create a history entry from a state transition."""
        return cls(
            entry_id=f"history_{transition.transition_id}",
            timestamp_utc=transition.timestamp_utc or "unknown",
            kind=transition.kind,
            episode_id=transition.episode_id,
            details=(f"from:{transition.from_state}", f"to:{transition.to_state}"),
        )