# Workspace State Model Module
# =============================

"""
Canonical WorkspaceState and WorkspaceStateSnapshot types.

WorkspaceState represents the complete semantic state of the Workspace Network
at a point in time. It is immutable and revisioned.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class WorkspaceCandidateReference:
    """
    Reference to a workspace candidate without embedding full content.
    
    Used for state snapshots to maintain bounds while preserving traceability.
    """
    
    candidate_id: str = ""
    """Unique identifier for the candidate."""
    
    revision: int = 0
    """Revision at time of reference."""
    
    semantic_version: str = "1.0"
    """Semantic version for compatibility tracking."""
    
    def __str__(self) -> str:
        return f"CandidateRef({self.candidate_id}@v{self.revision})"


@dataclass(frozen=True)
class WorkspaceStateSnapshot:
    """
    Immutable, bounded semantic snapshot of the workspace state at a point in time.
    
    Snapshot semantics:
    - Captures all relevant state characteristics without runtime dependencies
    - Bounded by explicit limits (candidate count, content size, etc.)
    - Deterministic: same inputs produce identical snapshots
    - Versioned: each snapshot has an associated revision
    
    The Workspace State is the complete semantic representation of the workspace
    condition at a point in time. It does NOT contain runtime memory, thread state,
    scheduler state, cache, or message queues.
    """
    
    # Identity and Revisioning
    state_id: str = "workspace_state_initial"
    """Unique identifier for this state instance."""
    
    revision: int = 0
    """Current revision number (strictly monotonic)."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Candidate pool state (bounded view)
    candidate_count: int = 0
    """Number of candidates in the current pool."""
    
    active_candidate_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently active candidates (admitted to workspace)."""
    
    pending_candidate_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of candidates pending evaluation or admission."""
    
    candidate_pool_max_size: int = 100
    """Maximum capacity of the candidate pool."""
    
    # Broadcast state (semantic, not runtime)
    broadcast_active: bool = False
    """Whether broadcast is currently active."""
    
    last_broadcast_state_id: Optional[str] = None
    """State ID at time of last broadcast (if any)."""
    
    broadcast_audience_size: int = 0
    """Estimated size of broadcast audience."""
    
    # Selection state
    selection_authority_id: Optional[str] = None
    """Authority responsible for current selection decisions."""
    
    selected_candidate_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of candidates selected for activation/broadcast."""
    
    # Context reference (not full context - just references)
    context_reference_id: Optional[str] = None
    """Reference to semantic context used for this state assessment."""
    
    context_revision: int = 1
    """Revision of referenced context."""
    
    max_context_projections: int = 50
    """Maximum context projections in this snapshot."""
    
    # Summary metrics (bounded)
    evaluation_summary: dict[str, str] = field(default_factory=dict)
    """Summary of evaluation metrics for the current state."""
    
    competition_summary: dict[str, str] = field(default_factory=dict)
    """Summary of competition outcomes."""
    
    admission_summary: dict[str, str] = field(default_factory=dict)
    """Summary of admission decisions."""
    
    # State evaluation metrics
    confidence_class: str = "unknown"
    """Classification of state confidence."""
    
    completeness_class: str = "partial"
    """Classification of state completeness."""
    
    consistency_class: str = "unknown"
    """Classification of state consistency."""
    
    coherence_class: str = "unknown"
    """Classification of state coherence."""
    
    # Metadata
    privacy_classification: str = "internal"
    """Privacy classification of this state."""
    
    provenance_created_by: str = "workspace_state"
    """Who/what created this state."""
    
    provenance_created_at_utc: float = 0.0
    """When state was created (seconds since epoch)."""
    
    @classmethod
    def initial(cls) -> WorkspaceStateSnapshot:
        """
        Create an initial workspace state snapshot.
        
        This creates a clean starting point with empty collections and minimal
        projections for the current assessment purpose.
        """
        return cls(
            state_id="workspace_state_initial",
            revision=0,
            confidence_class="unknown",
            completeness_class="partial",
            consistency_class="unknown",
            coherence_class="unknown",
        )
    
    @property
    def is_empty(self) -> bool:
        """Check if this snapshot has no candidates."""
        return self.candidate_count == 0 and len(self.active_candidate_ids) == 0


@dataclass(frozen=True)
class WorkspaceState:
    """
    The complete, immutable, revisioned semantic representation of the
    Workspace Network's currently accepted state.
    
    Workspace State describes what the Workspace Network currently accepts about:
        - Active candidate pool (admitted candidates)
        - Pending candidates under evaluation
        - Selection and activation decisions
        - Broadcast state and scope
        - Context reference for assessment
        - State revision
    
    State properties:
        - Immutable: Cannot be modified in place; use transitions to create new states
        - Bounded: All collections have capacity limits
        - Revisioned: Each state has a strictly increasing revision number
        - Deterministic: Identical inputs produce identical outputs
        - Serializable: Can be converted to/from dict for storage/transmission
    
    State NOT owned:
        - Candidate content (external ownership maintained via references)
        - Source artifacts referenced by candidates
        - ExecutionThread, Loop, Cycle state (Execution owns these)
        - Runtime memory or thread state
    
    STATE IS DISTINCT FROM:
        - WorkspaceStateSnapshot: Snapshot is a bounded view for consumption
        - ExecutiveState: Executive Network has separate state
        - WorkingMemoryState: Active content is maintained separately
        - GlobalAgentState: State is bounded to workspace scope only
    
    ARCHITECTURAL INVARIANTS:
        WS-INV-001: Every state has exactly one unique identity
        WS-INV-002: Every state has exactly one revision number
        WS-INV-003: Revisions are strictly monotonic (n+1 > n)
        WS-INV-004: State is immutable once created
        WS-INV-005: No runtime dependencies in semantic state
    """
    
    # Identity and Revisioning
    state_id: str = "workspace_state_initial"
    """Unique identifier for this state instance."""
    
    revision: int = 0
    """Current revision number (strictly monotonic)."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Core state components
    snapshot: WorkspaceStateSnapshot = field(default_factory=WorkspaceStateSnapshot.initial)
    """Semantic snapshot of the current state."""
    
    # Previous state reference (for lineage)
    previous_state_id: Optional[str] = None
    """ID of the preceding state in history (if any)."""
    
    previous_revision: int = 0
    """Revision of preceding state."""
    
    # State evaluation metrics
    confidence_class: str = "unknown"
    """Classification of state confidence."""
    
    completeness_class: str = "partial"
    """Classification of state completeness."""
    
    consistency_class: str = "unknown"
    """Classification of state consistency."""
    
    coherence_class: str = "unknown"
    """Classification of state coherence."""
    
    # Metadata
    privacy_classification: str = "internal"
    """Privacy classification of this state."""
    
    provenance_created_by: str = "workspace_state"
    """Who/what created this state."""
    
    provenance_created_at_utc: float = 0.0
    """When state was created (seconds since epoch)."""
    
    @classmethod
    def initial(cls) -> WorkspaceState:
        """
        Create an initial workspace state.
        
        This creates a clean starting point with empty collections and minimal
        projections for the current assessment purpose.
        """
        return cls(
            state_id="workspace_state_initial",
            revision=0,
            snapshot=WorkspaceStateSnapshot.initial(),
            confidence_class="unknown",
            completeness_class="partial",
            consistency_class="unknown",
            coherence_class="unknown",
        )
    
    @property
    def is_terminal(self) -> bool:
        """Check if this state represents a terminal condition."""
        # Terminal states are determined by external authorities
        # This property exists for reference but doesn't determine termination
        return False


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "WorkspaceCandidateReference",
    "WorkspaceStateSnapshot",
    "WorkspaceState",
)