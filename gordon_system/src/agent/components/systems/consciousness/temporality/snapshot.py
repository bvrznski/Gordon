# Gordon Phase 5.7.4-I: Temporal Context Engine - Temporal Snapshot
# ===============================================================================
"""
Temporal snapshot module for immutable publications of temporal state.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class TemporalSnapshot:
    """
    Immutable publication of the complete temporal context at a point in time.
    
    A temporal snapshot captures all bounded temporal elements (retention,
    presentation, protention) in their current state. Snapshots are versioned
    and may be superseded by newer generations through atomic transitions.
    
    Properties:
        - Immutable: Once published, never modified
        - Versioned: Has explicit generation number
        - Complete: Contains all temporal elements at time of publication
        - Bounded: All collections respect capacity limits
    """
    
    snapshot_id: str = field(default_factory=lambda: f"ts-{time.time()}")
    """Unique identifier for this snapshot."""
    
    # Temporal components
    retention_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to previous generation contexts (retention)."""
    
    presentation_reference: Optional[str] = None
    """Reference to current Experiential Field context (presentation)."""
    
    protention_expectations: Tuple[str, ...] = field(default_factory=tuple)
    """Expectations about immediate forthcoming context (protention)."""
    
    # Versioning and provenance
    generation: int = 0
    """Snapshot generation number."""
    
    previous_generation: Optional[int] = None
    """Previous snapshot generation for lineage tracking."""
    
    transition_id: Optional[str] = None
    """Transition that produced this snapshot (if any)."""
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    """When this snapshot was published."""
    
    valid_from_utc: float = 0.0
    """Timestamp when this snapshot became valid (for replay purposes)."""
    
    # Status
    state: str = "valid"
    """Snapshot state (valid, deprecated, invalid)."""
    
    provenance: Optional[str] = None
    """Provenance chain for this snapshot."""
    
    trust_summary: str = "medium"
    """Summary trust level of all temporal elements."""
    
    privacy_classification: str = "internal"
    """Privacy classification of this snapshot."""
    
    @classmethod
    def initial(
        cls,
        presentation_ref: Optional[str] = None,
        timestamp_utc: Optional[float] = None,
    ) -> "TemporalSnapshot":
        """
        Create an initial temporal snapshot.
        
        Args:
            presentation_ref: Optional current EF context reference
            timestamp_utc: Optional timestamp (uses current time if not provided)
            
        Returns:
            Initial snapshot at generation 0
        """
        return cls(
            generation=0,
            presentation_reference=presentation_ref,
            valid_from_utc=timestamp_utc if timestamp_utc is not None else 0.0,
        )
    
    def next_generation(
        self,
        transition_id: str,
        timestamp_utc: Optional[float] = None,
    ) -> "TemporalSnapshot":
        """
        Create the next generation snapshot from this one.
        
        Args:
            transition_id: Transition producing this generation
            timestamp_utc: Optional timestamp (uses 0.0 for replayability if not provided)
            
        Returns:
            New TemporalSnapshot with generation + 1
            
        Note:
            When creating snapshots for replay, use timestamp_utc=0.0 to ensure
            identical output for identical inputs.
        """
        return TemporalSnapshot(
            snapshot_id=self.snapshot_id,  # Same ID for replayability
            retention_references=self.retention_references,
            presentation_reference=self.presentation_reference,
            protention_expectations=self.protention_expectations,
            generation=self.generation + 1,
            previous_generation=self.generation,
            transition_id=transition_id,
            created_at_utc=timestamp_utc if timestamp_utc is not None else 0.0,
            valid_from_utc=timestamp_utc if timestamp_utc is not None else 0.0,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if this snapshot's state indicates validity."""
        return self.state == "valid"
    
    @property
    def is_deprecated(self) -> bool:
        """Check if this snapshot has been deprecated."""
        return self.state == "deprecated"


class TemporalSnapshotBuilder:
    """
    Builder for constructing temporal snapshots incrementally.
    
    Provides a fluent interface for building snapshots with proper validation
    before publication.
    """
    
    def __init__(self, snapshot_id: Optional[str] = None):
        """
        Initialize the builder.
        
        Args:
            snapshot_id: Optional ID (generated if not provided)
        """
        self._snapshot_id: Optional[str] = snapshot_id
        self._retention_refs: Tuple[str, ...] = tuple()
        self._presentation_ref: Optional[str] = None
        self._protentions: Tuple[str, ...] = tuple()
        self._generation: int = 0
        self._previous_generation: Optional[int] = None
        self._state: str = "valid"
        self._provenance: Optional[str] = None
        self._privacy_classification: str = "internal"
    
    def set_retention(self, refs: Tuple[str, ...]) -> "TemporalSnapshotBuilder":
        """Set retention references."""
        self._retention_refs = refs[:10]  # Bounded to 10
        return self
    
    def set_presentation(self, ref: str) -> "TemporalSnapshotBuilder":
        """Set presentation reference."""
        self._presentation_ref = ref
        return self
    
    def add_protention(self, expectation: str) -> "TemporalSnapshotBuilder":
        """Add a protentional expectation."""
        if len(self._protentions) < 5:  # Bounded to 5
            self._protentions += (expectation,)
        return self
    
    def set_generation(self, generation: int) -> "TemporalSnapshotBuilder":
        """Set the snapshot generation."""
        self._generation = generation
        return self
    
    def set_previous_generation(self, prev_gen: int) -> "TemporalSnapshotBuilder":
        """Set the previous generation for lineage tracking."""
        self._previous_generation = prev_gen
        return self
    
    def set_provenance(self, provenance: str) -> "TemporalSnapshotBuilder":
        """Set the provenance chain."""
        self._provenance = provenance
        return self
    
    def set_privacy_classification(
        self,
        classification: str,
    ) -> "TemporalSnapshotBuilder":
        """Set privacy classification."""
        self._privacy_classification = classification
        return self
    
    def build(self) -> TemporalSnapshot:
        """
        Build and validate the temporal snapshot.
        
        Returns:
            New TemporalSnapshot
            
        Raises:
            ValueError: If required fields are missing or validation fails
        """
        if self._presentation_ref is None:
            raise ValueError("Presentation reference is required")
        
        return TemporalSnapshot(
            snapshot_id=self._snapshot_id or f"ts-{time.time()}",
            retention_references=self._retention_refs,
            presentation_reference=self._presentation_ref,
            protention_expectations=self._protentions,
            generation=self._generation,
            previous_generation=self._previous_generation,
            state=self._state,
            provenance=self._provenance,
            privacy_classification=self._privacy_classification,
        )


@dataclass(frozen=True)
class SnapshotTransition:
    """
    Immutable record of a snapshot transition event.
    
    Tracks when and why a temporal snapshot was published, including any
    changes made during the transition.
    """
    
    transition_id: str = field(default_factory=lambda: f"st-{time.time()}")
    """Unique identifier for this transition."""
    
    previous_snapshot_id: Optional[str] = None
    """ID of the snapshot being superseded."""
    
    new_snapshot_id: str = ""
    """ID of the newly published snapshot."""
    
    transition_kind: str = "default"
    """Kind of transition (default, resume, reset, interruption, etc.)."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the transition occurred."""
    
    generation_change: int = 1
    """Change in generation number."""
    
    is_rollback: bool = False
    """Whether this was a rollback transition."""
    
    @classmethod
    def standard(
        cls,
        previous_snapshot_id: Optional[str],
        new_snapshot_id: str,
    ) -> "SnapshotTransition":
        """
        Create a standard snapshot transition.
        
        Args:
            previous_snapshot_id: ID of the superseded snapshot
            new_snapshot_id: ID of the new snapshot
            
        Returns:
            New SnapshotTransition for a normal generation advance
        """
        return cls(
            previous_snapshot_id=previous_snapshot_id,
            new_snapshot_id=new_snapshot_id,
            transition_kind="default",
        )
    
    @classmethod
    def rollback(
        cls,
        from_generation: int,
        to_generation: int,
    ) -> "SnapshotTransition":
        """
        Create a rollback snapshot transition.
        
        Args:
            from_generation: Generation rolling back from
            to_generation: Generation rolling back to
            
        Returns:
            New SnapshotTransition for a rollback
        """
        return cls(
            transition_kind="rollback",
            is_rollback=True,
            generation_change=to_generation - from_generation,
        )
    
    @classmethod
    def reset(cls) -> "SnapshotTransition":
        """
        Create a reset snapshot transition (new session).
        
        Returns:
            New SnapshotTransition for a reset
        """
        return cls(
            transition_kind="reset",
            is_rollback=False,
        )


__all__: Tuple[str, ...] = (
    "TemporalSnapshot",
    "TemporalSnapshotBuilder",
    "SnapshotTransition",
)