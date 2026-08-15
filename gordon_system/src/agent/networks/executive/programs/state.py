# Executive Program State
# =======================

"""
Executive Program State - Immutable enum of semantic program lifecycle states.

This module defines the canonical states through which an ExecutiveProgram
progresses during its lifetime. These are semantic states describing the
program's organizational role, not runtime execution state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum


# =============================================================================
# EXECUTIVE PROGRAM STATE ENUMERATION
# =============================================================================


class ExecutiveProgramState(Enum):
    """
    Semantic lifecycle states for an ExecutiveProgram.
    
    These describe the organizational state of a program - what it represents
    in terms of ongoing cognition - not its runtime execution status.
    
    State transitions are deterministic and follow strict rules:
        CREATED -> PREPARING -> READY -> ACTIVE -> WAITING -> INTERRUPTED -> RESUMING -> COMPLETING -> COMPLETED/FAILED/ABANDONED
    
    States that may be reached from multiple paths:
        - SUSPENDED: May be entered from any active state
        - TERMINATED: May replace any state when program is forcefully ended
        - RESTARTING: May follow FAILED or ABANDONED to attempt recovery
    """
    
    # Initial states - before execution begins
    CREATED = "created"
    """Program has been instantiated but not yet prepared."""
    
    PREPARING = "preparing"
    """Program is preparing its task set and acquiring resources."""
    
    READY = "ready"
    """Program is fully prepared and ready for activation."""
    
    # Active states - during execution
    ACTIVE = "active"
    """Program currently owns executive resources and is pursuing objectives."""
    
    WAITING = "waiting"
    """Program is waiting for external conditions or results before proceeding."""
    
    # Interrupted states - execution paused
    BLOCKED = "blocked"
    """Program cannot proceed due to unmet constraints or dependencies."""
    
    INTERRUPTED = "interrupted"
    """Program was interrupted by higher-priority activity."""
    
    SUSPENDED = "suspended"
    """Program's execution is temporarily suspended. State is preserved for resumption."""
    
    RESUMING = "resuming"
    """Program is being resumed from suspension or interruption."""
    
    # Completion states - program termination
    COMPLETING = "completing"
    """Program has completed and is finalizing results."""
    
    COMPLETED = "completed"
    """Program successfully achieved its objectives."""
    
    FAILED = "failed"
    """Program could not achieve its objectives due to failure conditions."""
    
    ABANDONED = "abandoned"
    """Program was explicitly abandoned before completion."""
    
    TERMINATED = "terminated"
    """Program was forcefully terminated (e.g., by authority decision)."""
    
    REPLACED = "replaced"
    """Program was replaced by another program with the same objective."""
    
    MERGED = "merged"
    """Program was merged into another program."""
    
    SPLIT = "split"
    """Program was split into multiple child programs."""
    
    ARCHIVED = "archived"
    """Program is complete and archived for reference but not active."""
    
    # Delegation states - program ownership
    DELEGATED = "delegated"
    """Program's execution has been delegated to another program."""
    
    RECOVERY = "recovery"
    """Program is a recovery program activated after failure."""
    
    MAINTENANCE = "maintenance"
    """Program is performing routine maintenance tasks."""
    
    BACKGROUND = "background"
    """Program operates in background without direct user interaction."""


@dataclass(frozen=True)
class ExecutiveProgramRevision:
    """
    Immutable revision identifier for an ExecutiveProgram.
    
    Revisions track all changes to a program, enabling deterministic
    reconstruction and replay of program history.
    """
    
    revision_number: int = 0
    """Strictly increasing revision number."""
    
    schema_version: str = "1.0.0"
    """Schema version at time of revision creation."""
    
    transition_kind: Optional[str] = None
    """Kind of transition that produced this revision (e.g., 'created', 'updated')."""
    
    parent_revision_id: Optional[str] = None
    """ID of the previous revision in history chain."""
    
    @classmethod
    def initial(cls) -> ExecutiveProgramRevision:
        """
        Create the initial revision for a new program.
        
        Returns:
            Revision with number 0, schema version "1.0.0"
        """
        return cls(revision_number=0, schema_version="1.0.0")
    
    def next(self, transition_kind: Optional[str] = None) -> ExecutiveProgramRevision:
        """
        Create the next revision in sequence.
        
        Args:
            transition_kind: Kind of transition producing this revision
            
        Returns:
            New revision with incremented number and this as parent
        """
        return ExecutiveProgramRevision(
            revision_number=self.revision_number + 1,
            schema_version=self.schema_version,
            transition_kind=transition_kind,
            parent_revision_id=f"rev_{self.revision_number}",
        )
    
    def __str__(self) -> str:
        """Return string representation of the revision."""
        return f"revision-{self.revision_number}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveProgramState",
    "ExecutiveProgramRevision",
)