# Executive Adapter - Gordon Executive Network Audit Subsystem
# =============================================================

"""
Adapter layer for observing executive state without modifying it.

This module provides adapters that allow the audit subsystem to:
- Observe executive state and context
- Access program definitions and history
- Query conflict and demand information
- Retrieve performance metrics

The adapter pattern ensures the audit subsystem never directly modifies
executive state. All access is read-only through well-defined interfaces.
"""

from dataclasses import dataclass, field
from typing import Protocol, Optional, List, Dict, Any, Tuple
import time


# =============================================================================
# EXECUTIVE STATE ADAPTER - Read-only observation of executive state
# =============================================================================

@dataclass(frozen=True)
class ExecutiveStateSnapshot:
    """
    A read-only snapshot of executive state at a point in time.
    
    This is what the audit adapter produces - an immutable view of the
    executive state that can be analyzed without risk of modification.
    """
    
    timestamp_utc: float
    """When this snapshot was taken."""
    
    state_id: str
    """ID of the audited state."""
    
    revision: int
    """Revision number of the state."""
    
    mode: Optional[str]
    """Current executive mode."""
    
    active_task_set_ids: Tuple[str, ...]
    """IDs of currently active task sets."""
    
    active_goal_ids: Tuple[str, ...]
    """IDs of currently active goals."""
    
    active_commitment_ids: Tuple[str, ...]
    """IDs of currently active commitments."""
    
    strategy_id: Optional[str]
    """ID of current strategy."""
    
    conflict_count: int
    """Number of active conflicts."""
    
    demand_summary: Dict[str, Any]
    """Summary of control demand."""
    
    performance_summary: Dict[str, Any]
    """Summary of executive performance."""
    
    state_consistency_class: str
    """Consistency classification of the state."""
    
    @classmethod
    def from_state(cls, state_data: Dict[str, Any]) -> "ExecutiveStateSnapshot":
        """
        Create a snapshot from raw state data.
        
        Args:
            state_data: Raw executive state dictionary
            
        Returns:
            ExecutiveStateSnapshot instance
        """
        return cls(
            timestamp_utc=time.time(),
            state_id=state_data.get("state_id", "unknown"),
            revision=state_data.get("revision", 0),
            mode=state_data.get("mode"),
            active_task_set_ids=tuple(state_data.get("active_task_set_ids", [])),
            active_goal_ids=tuple(state_data.get("active_goal_ids", [])),
            active_commitment_ids=tuple(state_data.get("active_commitment_ids", [])),
            strategy_id=state_data.get("strategy_id"),
            conflict_count=len(state_data.get("conflicts", [])),
            demand_summary=state_data.get("demand_summary", {}),
            performance_summary=state_data.get("performance_summary", {}),
            state_consistency_class=state_data.get("consistency_class", "unknown"),
        )


class ExecutiveStateAdapter(Protocol):
    """
    Protocol for adapters that read executive state.
    
    These adapters provide read-only access to executive state information
    without any modification capabilities.
    """
    
    def get_state_snapshot(
        self,
        state_id: Optional[str] = None,
    ) -> Optional[ExecutiveStateSnapshot]:
        """
        Get a snapshot of current or specified executive state.
        
        Args:
            state_id: ID of state to snapshot (None for current)
            
        Returns:
            Snapshot if available, None otherwise
        """
        ...
    
    def get_state_history(
        self,
        limit: int = 10,
    ) -> Tuple[ExecutiveStateSnapshot, ...]:
        """
        Get recent executive state snapshots.
        
        Args:
            limit: Maximum number of snapshots to return
            
        Returns:
            Tuple of state snapshots (newest first)
        """
        ...
    
    def get_active_goals(self) -> Tuple[str, ...]:
        """Get IDs of currently active goals."""
        ...
    
    def get_active_commitments(self) -> Tuple[str, ...]:
        """Get IDs of currently active commitments."""
        ...
    
    def get_conflict_count(self) -> int:
        """Get count of active conflicts."""
        ...


# =============================================================================
# EXECUTIVE CONTEXT ADAPTER - Read-only observation of executive context
# =============================================================================

@dataclass(frozen=True)
class ExecutiveContextSnapshot:
    """
    A read-only snapshot of executive context at a point in time.
    """
    
    timestamp_utc: float
    """When this snapshot was taken."""
    
    context_id: str
    """ID of the audited context."""
    
    revision: int
    """Revision number of the context."""
    
    purpose: str
    """Purpose of this context."""
    
    projection_count: int
    """Number of projections included."""
    
    required_projections_missing: Tuple[str, ...]
    """IDs of required projections that are missing."""
    
    @classmethod
    def from_context(cls, context_data: Dict[str, Any]) -> "ExecutiveContextSnapshot":
        """
        Create a snapshot from raw context data.
        
        Args:
            context_data: Raw executive context dictionary
            
        Returns:
            ExecutiveContextSnapshot instance
        """
        return cls(
            timestamp_utc=time.time(),
            context_id=context_data.get("context_id", "unknown"),
            revision=context_data.get("revision", 1),
            purpose=context_data.get("purpose", "general_executive_assessment"),
            projection_count=len(context_data.get("projections", [])),
            required_projections_missing=tuple(
                context_data.get("required_projections_missing", [])
            ),
        )


class ExecutiveContextAdapter(Protocol):
    """Protocol for adapters that read executive context."""
    
    def get_context_snapshot(self) -> Optional[ExecutiveContextSnapshot]:
        """Get a snapshot of current executive context."""
        ...
    
    def get_projection_sources(self) -> Tuple[str, ...]:
        """
        Get identifiers of all projection sources in the current context.
        
        Returns:
            Tuple of source identifiers
        """
        ...


# =============================================================================
# EXECUTIVE PROGRAMS ADAPTER - Read-only observation of program state
# =============================================================================

@dataclass(frozen=True)
class ExecutiveProgramSnapshot:
    """A read-only snapshot of executive programs."""
    
    timestamp_utc: float
    """When this snapshot was taken."""
    
    program_id: str
    """ID of the program."""
    
    type_: str
    """Type of program (goal, task_set, etc.)."""
    
    status: str
    """Current status."""
    
    progress: Optional[float]
    """Progress percentage (0-1) if applicable."""
    
    completion_time_utc: Optional[float]
    """Completion timestamp if completed."""
    
    error_count: int = 0
    """Number of errors encountered."""
    
    @classmethod
    def from_program(cls, program_data: Dict[str, Any]) -> "ExecutiveProgramSnapshot":
        """
        Create a snapshot from raw program data.
        
        Args:
            program_data: Raw executive program dictionary
            
        Returns:
            ExecutiveProgramSnapshot instance
        """
        return cls(
            timestamp_utc=time.time(),
            program_id=program_data.get("program_id", "unknown"),
            type_=program_data.get("type_", "unknown"),
            status=program_data.get("status", "pending"),
            progress=program_data.get("progress"),
            completion_time_utc=program_data.get("completion_time_utc"),
            error_count=len(program_data.get("errors", [])),
        )


class ExecutiveProgramAdapter(Protocol):
    """Protocol for adapters that read executive programs."""
    
    def get_active_programs(self) -> Tuple[ExecutiveProgramSnapshot, ...]:
        """
        Get snapshots of currently active programs.
        
        Returns:
            Tuple of program snapshots
        """
        ...
    
    def get_program_history(
        self,
        program_id: str,
        limit: int = 10,
    ) -> Tuple[ExecutiveProgramSnapshot, ...]:
        """
        Get history snapshots for a specific program.
        
        Args:
            program_id: ID of the program
            limit: Maximum number of snapshots to return
            
        Returns:
            Tuple of program snapshots (newest first)
        """
        ...


# =============================================================================
# EXECUTIVE CONFLICTS ADAPTER - Read-only observation of conflicts
# =============================================================================

@dataclass(frozen=True)
class ExecutiveConflictSnapshot:
    """A read-only snapshot of an executive conflict."""
    
    timestamp_utc: float
    """When this snapshot was taken."""
    
    conflict_id: str
    """ID of the conflict."""
    
    kind: str
    """Kind of conflict (from ConflictKind enum)."""
    
    severity: str
    """Severity level."""
    
    subject: Optional[str]
    """Subject of the conflict."""
    
    evidence_count: int
    """Number of supporting evidence items."""
    
    @classmethod
    def from_conflict(cls, conflict_data: Dict[str, Any]) -> "ExecutiveConflictSnapshot":
        """
        Create a snapshot from raw conflict data.
        
        Args:
            conflict_data: Raw executive conflict dictionary
            
        Returns:
            ExecutiveConflictSnapshot instance
        """
        return cls(
            timestamp_utc=time.time(),
            conflict_id=conflict_data.get("conflict_id", "unknown"),
            kind=conflict_data.get("kind", "goal_conflict"),
            severity=conflict_data.get("severity", "low"),
            subject=conflict_data.get("subject"),
            evidence_count=len(conflict_data.get("evidence", [])),
        )


class ExecutiveConflictAdapter(Protocol):
    """Protocol for adapters that read executive conflicts."""
    
    def get_active_conflicts(self) -> Tuple[ExecutiveConflictSnapshot, ...]:
        """
        Get snapshots of currently active conflicts.
        
        Returns:
            Tuple of conflict snapshots
        """
        ...
    
    def get_conflict_by_id(self, conflict_id: str) -> Optional[ExecutiveConflictSnapshot]:
        """
        Get a specific conflict by ID.
        
        Args:
            conflict_id: ID of the conflict
            
        Returns:
            Snapshot if found, None otherwise
        """
        ...


# =============================================================================
# EXECUTIVE DEMAND ADAPTER - Read-only observation of demand state
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDemandSnapshot:
    """A read-only snapshot of executive demand state."""
    
    timestamp_utc: float
    """When this snapshot was taken."""
    
    demand_level: str
    """Level of control demand (low, medium, high, critical)."""
    
    estimated_cognitive_load: float
    """Estimated cognitive load (0-1)."""
    
    required_capacity: float
    """Required executive capacity (0-1)."""
    
    switch_count_24h: int = 0
    """Number of task switches in last 24 hours."""
    
    @classmethod
    def from_demand(cls, demand_data: Dict[str, Any]) -> "ExecutiveDemandSnapshot":
        """
        Create a snapshot from raw demand data.
        
        Args:
            demand_data: Raw executive demand dictionary
            
        Returns:
            ExecutiveDemandSnapshot instance
        """
        return cls(
            timestamp_utc=time.time(),
            demand_level=demand_data.get("demand_level", "medium"),
            estimated_cognitive_load=demand_data.get("estimated_cognitive_load", 0.5),
            required_capacity=demand_data.get("required_capacity", 0.5),
            switch_count_24h=demand_data.get("switch_count_24h", 0),
        )


class ExecutiveDemandAdapter(Protocol):
    """Protocol for adapters that read executive demand."""
    
    def get_demand_snapshot(self) -> Optional[ExecutiveDemandSnapshot]:
        """
        Get snapshot of current control demand.
        
        Returns:
            Snapshot if available, None otherwise
        """
        ...
    
    def get_demand_history(
        self,
        limit: int = 24,
    ) -> Tuple[ExecutiveDemandSnapshot, ...]:
        """
        Get recent demand snapshots.
        
        Args:
            limit: Maximum number of snapshots to return
            
        Returns:
            Tuple of demand snapshots (newest first)
        """
        ...