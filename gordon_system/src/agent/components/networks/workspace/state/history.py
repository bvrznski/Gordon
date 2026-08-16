# Workspace History Module
# ========================

"""
Canonical WorkspaceHistory and related types.

WorkspaceHistory represents an immutable append-only record of all state events,
including creation, revision, transition, invalidation, restoration, and certification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class HistoryRecord:
    """
    A single record in the workspace history append-only log.
    
    Each record represents one semantic event in the lifecycle of a workspace state.
    Records are never deleted or modified - they can only be appended.
    
    Record kinds:
        - state_created: Initial state creation
        - revision_produced: New revision from transition
        - delta_applied: Delta was applied to produce transition
        - snapshot_taken: Snapshot captured for diagnostic/restore purposes
        - invalidated: Content marked as semantically invalid
        - restored: Previously invalid content restored
        - certified: State certification recorded
    """
    
    # Record identity
    record_id: str = ""
    """Unique identifier for this history record."""
    
    record_kind: str = "state_created"
    """Type of event recorded."""
    
    # Timestamp (semantic, not runtime state)
    timestamp_utc: float = 0.0
    """When event occurred (seconds since epoch)."""
    
    # State reference
    state_id: str = ""
    """ID of the state at time of event."""
    
    revision: int = 0
    """Revision of state at time of event."""
    
    # Event details
    produced_by: str = "workspace_history"
    """Who/what produced this record."""
    
    evidence: dict = field(default_factory=dict)
    """Evidence supporting this record (semantic only)."""
    
    @classmethod
    def for_state_created(cls, state_id: str, timestamp_utc: float) -> HistoryRecord:
        return cls(
            record_kind="state_created",
            state_id=state_id,
            revision=0,
            timestamp_utc=timestamp_utc,
        )
    
    @classmethod
    def for_revision_produced(cls, state_id: str, revision: int, timestamp_utc: float) -> HistoryRecord:
        return cls(
            record_kind="revision_produced",
            state_id=state_id,
            revision=revision,
            timestamp_utc=timestamp_utc,
        )


@dataclass(frozen=True)
class InvalidationRecord:
    """
    Record of a state or content invalidation event.
    
    Invalidations never delete history - they mark content as semantically
    invalid while preserving all traceability through lineage.
    
    ARCHITECTURAL INVARIANT: Invalidation never removes history, only marks
    content as invalid within the semantic model.
    """
    
    # Reference to what was invalidated
    invalidation_target_id: str = ""
    """ID of the state/content that was invalidated."""
    
    invalidation_kind: str = "content"
    """Kind of item invalidated (state, delta, snapshot, continuity)."""
    
    # Invalidation details
    invalidation_reason: str = ""
    """Reason for invalidation."""
    
    invalidating_authority: str = ""
    """Authority that performed the invalidation."""
    
    invalidation_timestamp_utc: float = 0.0
    """When invalidation occurred."""
    
    # Recovery information (for potential restoration)
    can_be_restored: bool = True
    """Whether this content can be restored to valid state."""
    
    restoration_evidence: dict = field(default_factory=dict)
    """Evidence needed for restoration if applicable."""


@dataclass(frozen=True)
class WorkspaceHistory:
    """
    Append-only immutable history log of all workspace semantic events.
    
    History semantics:
        - Append-only: never delete or modify existing records
        - Complete: captures all state lifecycle events
        - Deterministic: same inputs produce identical histories
        - Traceable: every event is linked to its cause
    
    ARCHITECTURAL INVARIANT: History is append-only. Every operation that would
    "modify" history instead creates a new record while preserving the old.
    """
    
    # Identity and metadata
    history_id: str = "workspace_history_initial"
    """Unique identifier for this history instance."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Records (append-only log)
    records: Tuple[HistoryRecord, ...] = field(default_factory=tuple)
    """Ordered sequence of all historical records."""
    
    # Invalidation records
    invalidation_records: Tuple[InvalidationRecord, ...] = field(default_factory=tuple)
    """All invalidation events."""
    
    # History metadata
    total_events: int = 0
    """Total number of events recorded."""
    
    first_event_utc: float = 0.0
    """Timestamp of the first event."""
    
    last_event_utc: float = 0.0
    """Timestamp of the most recent event."""
    
    # Integrity
    history_intact: bool = True
    """Whether the history log is intact (no gaps or inconsistencies)."""
    
    @classmethod
    def initial(cls) -> WorkspaceHistory:
        """
        Create an initial history record.
        
        This represents a fresh start with no events yet recorded.
        """
        return cls(
            first_event_utc=0.0,
            last_event_utc=0.0,
            history_intact=True,
        )
    
    def with_record(self, record: HistoryRecord) -> WorkspaceHistory:
        """
        Return a new history with the given record appended.
        
        This preserves immutability by creating a new instance.
        """
        return WorkspaceHistory(
            records=self.records + (record,),
            total_events=self.total_events + 1,
            first_event_utc=min(self.first_event_utc, record.timestamp_utc) if self.first_event_utc > 0 else record.timestamp_utc,
            last_event_utc=max(self.last_event_utc, record.timestamp_utc),
            history_intact=True,
        )
    
    def with_invalidation(self, invalidation: InvalidationRecord) -> WorkspaceHistory:
        """
        Return a new history with the given invalidation added.
        
        Invalidations are stored separately but preserve traceability
        through the state_id references.
        """
        return WorkspaceHistory(
            records=self.records,
            invalidation_records=self.invalidation_records + (invalidation,),
            total_events=self.total_events + 1,
            last_event_utc=max(self.last_event_utc, invalidation.invalidation_timestamp_utc),
            history_intact=True,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "HistoryRecord",
    "InvalidationRecord",
    "WorkspaceHistory",
)