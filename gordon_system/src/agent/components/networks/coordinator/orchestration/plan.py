# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Cognitive Orchestration Plan Model
==================================

The orchestration plan for executing a cognitive cycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from .identity import OrchestrationIdentity
from .enums import Status
from .stage import CognitiveExecutionStage
from .participant import CycleParticipant
from .barrier import SynchronizationBarrier
from .resource_allocation import ResourceAllocation


@dataclass(frozen=True, slots=True)
class PlanStatus:
    """
    Immutable orchestration plan status.
    
    PLAN-STATUS-LAW-001: Status transitions shall preserve provenance
    """
    
    value: str = ""
    """Plan status string."""
    
    timestamp_ref: str = ""
    """Reference to semantic time of this status change."""
    
    @classmethod
    def created(cls, timestamp_ref: str = "") -> PlanStatus:
        return cls(value=Status.CREATED.value, timestamp_ref=timestamp_ref)
    
    @classmethod
    def validated(cls, timestamp_ref: str = "") -> PlanStatus:
        return cls(value=Status.VALIDATED.value, timestamp_ref=timestamp_ref)
    
    @classmethod
    def ready(cls, timestamp_ref: str = "") -> PlanStatus:
        return cls(value=Status.READY.value, timestamp_ref=timestamp_ref)
    
    @classmethod
    def active(cls, timestamp_ref: str = "") -> PlanStatus:
        return cls(value=Status.ACTIVE.value, timestamp_ref=timestamp_ref)
    
    @classmethod
    def completed(cls, timestamp_ref: str = "") -> PlanStatus:
        return cls(value=Status.COMPLETED.value, timestamp_ref=timestamp_ref)


@dataclass(frozen=True, slots=True)
class CognitiveOrchestrationPlan:
    """
    Immutable orchestration plan model.
    
    ORCHESTRATION-LAW-001: Every orchestration plan possesses one stable semantic identity
    ORCHESTRATION-LAW-007: Published orchestration plans shall remain immutable
    
    Suggested fields per spec:
        identity
        orchestration_request
        execution_graph
        stages
        participants
        barriers
        resource_allocations
        degraded_mode
        completion_policy
        provenance
    """
    
    identity: OrchestrationIdentity
    """Unique identity for this plan."""
    
    request_ref: str = ""
    """Reference to the orchestration request."""
    
    execution_graph_ref: str = ""
    """Reference to the execution dependency graph."""
    
    stages: Tuple[CognitiveExecutionStage, ...] = ()
    """Execution stages in this plan."""
    
    participants: Tuple[CycleParticipant, ...] = ()
    """Participants in this cycle."""
    
    barriers: Tuple[SynchronizationBarrier, ...] = ()
    """Synchronization barriers."""
    
    resource_allocations: Tuple[ResourceAllocation, ...] = ()
    """Resource allocations for this plan."""
    
    degraded_mode_ref: str = ""
    """Reference to degraded mode (empty if not degraded)."""
    
    completion_policy_ref: str = ""
    """Reference to completion policy."""
    
    execution_policy_ref: str = ""
    """Reference to execution policy."""
    
    status: str = Status.CREATED.value
    """Current plan status."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    def __str__(self) -> str:
        return f"CognitiveOrchestrationPlan({self.identity}, stages={len(self.stages)}, participants={len(self.participants)})"