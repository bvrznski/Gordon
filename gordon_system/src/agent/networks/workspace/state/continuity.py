# Workspace Continuity Module
# ============================

"""
Canonical WorkspaceContinuity and related types.

WorkspaceContinuity preserves identity, lineage, provenance, revisions,
active context, selected content, and pending continuations across state transitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class ContinuationContext:
    """
    Context for semantic continuation from one workspace state to the next.
    
    Captures what should be preserved and how during state evolution while
    maintaining architectural bounds and runtime neutrality.
    """
    
    # Identity preservation
    identity_preserved: bool = True
    """Whether workspace identity is maintained across continuation."""
    
    lineage_preserved: bool = True
    """Whether lineage is preserved."""
    
    provenance_preserved: bool = True
    """Whether provenance is preserved."""
    
    # Active context continuation
    active_candidates_continued: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of candidates that continue into the next state."""
    
    pending_evaluations_continued: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of evaluations continuing from previous state."""
    
    # Selection continuity
    selected_candidates_continued: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of candidates that remain selected for broadcast/activation."""
    
    # Revision continuity
    revision_strategy: str = "incremental"
    """Strategy for revision management (incremental, checkpointed, etc.)"""
    
    max_continuation_history: int = 100
    """Maximum history entries to preserve for continuation analysis."""
    
    @property
    def has_active_continuations(self) -> bool:
        """Check if there are any active continuations."""
        return len(self.active_candidates_continued) > 0


@dataclass(frozen=True)
class ContinuationHistoryEntry:
    """
    Record of a single continuation event in workspace history.
    
    Captures the semantic continuity between states without runtime dependencies.
    """
    
    from_state_id: str = ""
    """ID of the state that produced the continuation."""
    
    to_state_id: str = ""
    """ID of the state that receives the continuation."""
    
    continuation_type: str = "incremental"
    """Type of continuation (incremental, restoration, invalidation, etc.)"""
    
    continuity_preserved: bool = True
    """Whether full continuity was maintained."""
    
    continuity_loss_reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Reasons for any continuity loss (if any)."""
    
    timestamp_utc: float = 0.0
    """When continuation occurred (seconds since epoch)."""


@dataclass(frozen=True)
class WorkspaceContinuity:
    """
    Semantic model of workspace continuity across state transitions.
    
    Continuity semantics:
    - Identity preservation: workspace identity is never lost
    - Lineage preservation: all transitions are traceable
    - Provenance preservation: source information is maintained
    - Revision tracking: monotonic revision progression
    - Active context preservation: relevant content continues
    
    ARCHITECTURAL INVARIANT: Continuity never depends on runtime timing.
    """
    
    # Current state
    current_state_id: str = ""
    """ID of the currently active workspace state."""
    
    current_revision: int = 0
    """Revision of the current state."""
    
    # Continuity record
    continuity_history: Tuple[ContinuationHistoryEntry, ...] = field(default_factory=tuple)
    """Complete history of continuation events."""
    
    # Active continuations (for pending transitions)
    pending_continuations: Tuple[ContinuationContext, ...] = field(default_factory=tuple)
    """Any pending continuation contexts."""
    
    # Continuity metrics
    total_transitions: int = 0
    """Total number of state transitions in history."""
    
    continuity_maintained_count: int = 0
    """Number of transitions that maintained full continuity."""
    
    last_continuation_loss_utc: float = 0.0
    """When the last continuity loss occurred (if any)."""
    
    # Continuity validation
    continuity_valid: bool = True
    """Whether current continuity is valid."""
    
    lineage_intact: bool = True
    """Whether the lineage chain is intact."""
    
    @classmethod
    def initial(cls) -> WorkspaceContinuity:
        """
        Create an initial continuity record.
        
        This represents a fresh start with no history.
        """
        return cls(
            current_state_id="workspace_state_initial",
            current_revision=0,
            total_transitions=0,
            continuity_maintained_count=0,
            continuity_valid=True,
            lineage_intact=True,
        )
    
    def with_continuation(self, entry: ContinuationHistoryEntry) -> WorkspaceContinuity:
        """
        Return a new continuity record with the given continuation added.
        
        This preserves immutability by creating a new instance.
        """
        return WorkspaceContinuity(
            current_state_id=entry.to_state_id,
            current_revision=self.current_revision + 1,
            continuity_history=self.continuity_history + (entry,),
            pending_continuations=(),
            total_transitions=self.total_transitions + 1,
            continuity_maintained_count=(
                self.continuity_maintained_count + (1 if entry.continuity_preserved else 0)
            ),
            last_continuation_loss_utc=(
                entry.timestamp_utc
                if not entry.continuity_preserved and entry.timestamp_utc > self.last_continuation_loss_utc
                else self.last_continuation_loss_utc
            ),
            continuity_valid=entry.continuity_preserved,
            lineage_intact=self.lineage_intact and entry.continuity_preserved,
        )


@dataclass(frozen=True)
class ContinuityViolation:
    """
    Record of a continuity violation in the workspace state history.
    
    Captures when and why continuity was lost, for diagnostic and recovery purposes.
    """
    
    violation_type: str = "unknown"
    """Type of continuity violation."""
    
    from_state_id: str = ""
    """State where violation originated."""
    
    to_state_id: str = ""
    """State affected by the violation."""
    
    timestamp_utc: float = 0.0
    """When violation occurred."""
    
    description: str = ""
    """Human-readable description of the violation."""
    
    recovery_possible: bool = True
    """Whether the state can be recovered."""


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "ContinuationContext",
    "ContinuationHistoryEntry",
    "WorkspaceContinuity",
    "ContinuityViolation",
)