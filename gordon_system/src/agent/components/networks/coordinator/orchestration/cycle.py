# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Cognitive Cycle Model
=====================

The CognitiveCycle represents one coordinated round of distributed cognition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from .identity import CycleIdentity
from .stage import CognitiveExecutionStage, StageStatus
from .participant import CycleParticipant, ParticipantStatus
from .barrier import SynchronizationBarrier
from .resource_allocation import ResourceAllocation
from .enums import CycleKind, Status


@dataclass(frozen=True, slots=True)
class CognitiveCycle:
    """
    Immutable cognitive cycle model.
    
    CYCLE-LAW-001: Every orchestration belongs to exactly one Cognitive Cycle
    CYCLE-LAW-002: Every Cognitive Cycle possesses explicit scope
    CYCLE-LAW-003: Cycle boundaries shall remain explicit
    CYCLE-LAW-004: Cycle participants shall remain explicit
    CYCLE-LAW-005: Cycle completion shall satisfy the selected completion policy
    CYCLE-LAW-006: Cycle status transitions shall preserve provenance
    CYCLE-LAW-007: Historical cycles shall remain inspectable
    
    CYCLE-INV-001: Cycle is immutable (deeply frozen)
    CYCLE-INV-002: Cycle has no runtime references
    """
    
    identity: CycleIdentity
    """Unique identity for this cycle."""
    
    kind: str  # CycleKind.*
    """Type of cognitive cycle."""
    
    goal_ref: str = ""
    """Reference to the goal being pursued."""
    
    scope_ref: str = ""
    """Reference to orchestration scope."""
    
    execution_plan_ref: str = ""
    """Reference to the orchestration plan."""
    
    participants: Tuple[CycleParticipant, ...] = ()
    """Participants in this cycle."""
    
    stages: Tuple[CognitiveExecutionStage, ...] = ()
    """Execution stages in this cycle."""
    
    barriers: Tuple[SynchronizationBarrier, ...] = ()
    """Synchronization barriers in this cycle."""
    
    resource_allocations: Tuple[ResourceAllocation, ...] = ()
    """Resource allocations for this cycle."""
    
    status: str = Status.CREATED.value
    """Current status of the cycle (from Status enum)."""
    
    semantic_time_ref: str = ""
    """Reference to semantic time for this cycle."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    def get_participant_status(self, network_ref: str) -> str:
        """
        Get the status of a participant by network reference.
        
        Args:
            network_ref: Reference to the cognitive network
            
        Returns:
            Status string for that participant
        """
        for participant in self.participants:
            if participant.identity.network_ref == network_ref:
                return participant.status
        return "unknown"
    
    def get_stage_status(self, stage_identity_value: str) -> str:
        """
        Get the status of a stage by its identity.
        
        Args:
            stage_identity_value: Identity value of the stage
            
        Returns:
            Status string for that stage
        """
        for stage in self.stages:
            if stage.identity.value == stage_identity_value:
                return stage.status
        return "unknown"
    
    def get_barrier_status(self, barrier_id: str) -> str:
        """
        Get the status of a synchronization barrier.
        
        Args:
            barrier_id: Identity of the barrier
            
        Returns:
            Status string for that barrier
        """
        for barrier in self.barriers:
            if barrier.identity == barrier_id:
                return barrier.status
        return "unknown"
    
    def is_completed(self) -> bool:
        """
        Check if all mandatory participants have completed.
        
        Returns:
            True if completed, False otherwise
        """
        for participant in self.participants:
            if participant.is_mandatory and participant.status != ParticipantStatus.COMPLETED.value:
                return False
        return True
    
    def __str__(self) -> str:
        return f"CognitiveCycle({self.identity}, kind={self.kind}, status={self.status})"