# Executive Program Snapshots
# ===========================

"""
Executive Program Snapshots - Immutable dataclass for program state snapshots.

Snapshots capture a point-in-time view of a program's state, not semantic memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveProgramSnapshot:
    """
    Immutable snapshot of an ExecutiveProgram at a specific point in time.
    
    Snapshots are NOT:
        - Semantic Memory (which stores knowledge)
        - Runtime state dumps
        - Complete program history
    
    Snapshots ARE:
        - Point-in-time captures of program state
        - Bounded to preserve essential information only
        - Revisioned for deterministic reconstruction
    
    Snapshot properties:
        - Immutable: No in-place modification
        - Bounded: Only essential state captured
        - Deterministic: Same inputs produce same outputs
        - Serializable: Can be converted to/from dict
    """
    
    # Identity and revisioning
    snapshot_id: str = "exec_snapshot_initial"
    """Unique identifier for this snapshot."""
    
    program_id: str = "exec_program_initial"
    """ID of the program this snapshot represents."""
    
    schema_version: str = "1.0.0"
    """Schema version at time of snapshot."""
    
    revision_at_snapshot: int = 1
    """Program revision at time of snapshot."""
    
    # Timestamp
    captured_at_utc: float = 0.0
    """When snapshot was taken (seconds since epoch)."""
    
    # Core state (essential information only)
    state_kind: str = "created"
    """The program's lifecycle state kind."""
    
    priority: int = 50
    """Priority level at time of snapshot."""
    
    activation: float = 1.0
    """Activation strength at time of snapshot."""
    
    # Task set reference (not full content)
    task_set_id: str = "exec_taskset_initial"
    """ID of the task set at time of snapshot."""
    
    task_set_revision: int = 1
    """Task set revision at time of snapshot."""
    
    # Key references (only IDs, not full objects)
    goal_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of goals in the program."""
    
    commitment_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of commitments in the program."""
    
    child_program_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of child programs at time of snapshot."""
    
    # Semantic evaluations
    confidence: float = 0.5
    """Confidence at time of snapshot."""
    
    consistency: float = 1.0
    """Consistency at time of snapshot."""
    
    coherence: float = 1.0
    """Coherence at time of snapshot."""
    
    # Hierarchy info
    parent_program_id: Optional[str] = None
    """ID of parent program (if any)."""
    
    @classmethod
    def initial(
        cls,
        snapshot_id: str = "exec_snapshot_initial",
        program_id: str = "exec_program_initial",
    ) -> ExecutiveProgramSnapshot:
        """
        Create an initial empty snapshot.
        
        Args:
            snapshot_id: Unique identifier for this snapshot
            program_id: ID of the program
            
        Returns:
            New snapshot with minimal state
        """
        return cls(
            snapshot_id=snapshot_id,
            program_id=program_id,
            revision_at_snapshot=1,
            captured_at_utc=0.0,
            state_kind="created",
            priority=50,
            activation=1.0,
        )
    
    def to_dict(self) -> dict:
        """
        Convert snapshot to a dictionary representation.
        
        Returns:
            Dictionary with all snapshot fields
        """
        return {
            "snapshot_id": self.snapshot_id,
            "program_id": self.program_id,
            "schema_version": self.schema_version,
            "revision_at_snapshot": self.revision_at_snapshot,
            "captured_at_utc": self.captured_at_utc,
            "state_kind": self.state_kind,
            "priority": self.priority,
            "activation": self.activation,
            "task_set_id": self.task_set_id,
            "task_set_revision": self.task_set_revision,
            "goal_reference_ids": list(self.goal_reference_ids),
            "commitment_reference_ids": list(self.commitment_reference_ids),
            "child_program_ids": list(self.child_program_ids),
            "confidence": self.confidence,
            "consistency": self.consistency,
            "coherence": self.coherence,
            "parent_program_id": self.parent_program_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> ExecutiveProgramSnapshot:
        """
        Create a snapshot from a dictionary representation.
        
        Args:
            data: Dictionary with snapshot data
            
        Returns:
            New snapshot instance
        """
        return cls(
            snapshot_id=data.get("snapshot_id", "exec_snapshot_initial"),
            program_id=data.get("program_id", "exec_program_initial"),
            schema_version=data.get("schema_version", "1.0.0"),
            revision_at_snapshot=data.get("revision_at_snapshot", 1),
            captured_at_utc=data.get("captured_at_utc", 0.0),
            state_kind=data.get("state_kind", "created"),
            priority=data.get("priority", 50),
            activation=data.get("activation", 1.0),
            task_set_id=data.get("task_set_id", "exec_taskset_initial"),
            task_set_revision=data.get("task_set_revision", 1),
            goal_reference_ids=tuple(data.get("goal_reference_ids", [])),
            commitment_reference_ids=tuple(data.get("commitment_reference_ids", [])),
            child_program_ids=tuple(data.get("child_program_ids", [])),
            confidence=data.get("confidence", 0.5),
            consistency=data.get("consistency", 1.0),
            coherence=data.get("coherence", 1.0),
            parent_program_id=data.get("parent_program_id"),
        )


@dataclass(frozen=True)
class ExecutiveProgramRevision:
    """
    Immutable revision record for an ExecutiveProgram.
    
    Revisions track all changes to a program, enabling deterministic
    reconstruction and replay of program history.
    """
    
    # Identity
    revision_id: str = "exec_revision_initial"
    """Unique identifier for this revision."""
    
    program_id: str = "exec_program_initial"
    """ID of the program this revision belongs to."""
    
    revision_number: int = 0
    """Strictly increasing revision number."""
    
    schema_version: str = "1.0.0"
    """Schema version at time of revision."""
    
    # Timestamp
    created_at_utc: float = 0.0
    """When this revision was created (seconds since epoch)."""
    
    # State before and after
    from_state: Optional[str] = None
    """State before revision."""
    
    to_state: Optional[str] = None
    """State after revision."""
    
    # Transition details
    transition_kind: str = "created"
    """
    Kind of transition:
        'created' - Initial program creation
        'updated' - State updated without state change
        'state_changed' - Lifecycle state changed
        'priority_changed' - Priority was modified
        'goal_added' - Goal added to task set
        'goal_removed' - Goal removed from task set
        'commitment_created' - Commitment was established
        'constraint_added' - Constraint was added
    """
    
    # Revision chain
    parent_revision_id: Optional[str] = None
    """ID of the previous revision in history chain."""
    
    # Metadata
    created_by: str = "executive_network"
    """Who/what created this revision."""
    
    reason: Optional[str] = None
    """Reason for the revision."""
    
    @classmethod
    def initial(cls) -> ExecutiveProgramRevision:
        """
        Create an initial revision.
        
        Returns:
            Revision with number 0 and schema version "1.0.0"
        """
        return cls(
            revision_id="exec_revision_initial",
            program_id="exec_program_initial",
            revision_number=0,
            schema_version="1.0.0",
            transition_kind="created",
        )
    
    def next(self, to_state: str, created_at_utc: float) -> ExecutiveProgramRevision:
        """
        Create the next revision in sequence.
        
        Args:
            to_state: State after this revision
            created_at_utc: Timestamp for this revision
            
        Returns:
            New revision with incremented number and this as parent
        """
        return cls(
            revision_id=f"rev_{self.revision_number + 1}",
            program_id=self.program_id,
            revision_number=self.revision_number + 1,
            schema_version=self.schema_version,
            created_at_utc=created_at_utc,
            from_state=None if self.to_state is None else self.to_state,
            to_state=to_state,
            parent_revision_id=self.revision_id,
            transition_kind="updated",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveProgramSnapshot",
    "ExecutiveProgramRevision",
)