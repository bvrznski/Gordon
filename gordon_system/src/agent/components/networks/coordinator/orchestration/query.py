# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Orchestration Query Models
==========================

Query models for orchestration information retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class QueryKind:
    """
    Kind of orchestration query.
    
    QUERY-LAW-001: All queries shall be read-only
    """
    
    ACTIVE_CYCLES = "active_cycles"
    """List active cycles."""
    
    PLAN_BY_ID = "plan_by_id"
    """Get plan by its identity."""
    
    STAGES_BY_CYCLE = "stages_by_cycle"
    """Get stages for a cycle."""
    
    PARTICIPANTS_BY_STAGE = "participants_by_stage"
    """Get participants for a stage."""
    
    RESOURCE_ALLOCATIONS = "resource_allocations"
    """List resource allocations."""
    
    ACTIVE_BARRIERS = "active_barriers"
    """List active synchronization barriers."""
    
    DEGRADED_CYCLES = "degraded_cycles"
    """List cycles in degraded mode."""
    
    UNKNOWN = "unknown"
    """Unknown query kind."""


@dataclass(frozen=True, slots=True)
class OrchestrationQuery:
    """
    Immutable orchestration query model.
    
    QUERY-LAW-001: All queries shall be read-only
    """
    
    kind: str  # QueryKind.*
    """Type of query."""
    
    filter_ref: str = ""
    """Reference for filtering results."""
    
    limit: int = 0
    """Maximum number of results (0 = no limit)."""
    
    offset: int = 0
    """Offset for pagination."""
    
    @classmethod
    def active_cycles(cls) -> OrchestrationQuery:
        return cls(kind=QueryKind.ACTIVE_CYCLES)
    
    @classmethod
    def plan_by_id(cls, identity_ref: str) -> OrchestrationQuery:
        return cls(kind=QueryKind.PLAN_BY_ID, filter_ref=identity_ref)
    
    @classmethod
    def stages_by_cycle(cls, cycle_ref: str) -> OrchestrationQuery:
        return cls(kind=QueryKind.STAGES_BY_CYCLE, filter_ref=cycle_ref)
    
    @classmethod
    def participants_by_stage(cls, stage_ref: str) -> OrchestrationQuery:
        return cls(kind=QueryKind.PARTICIPANTS_BY_STAGE, filter_ref=stage_ref)
    
    @classmethod
    def resource_allocations(cls) -> OrchestrationQuery:
        return cls(kind=QueryKind.RESOURCE_ALLOCATIONS)
    
    @classmethod
    def active_barriers(cls) -> OrchestrationQuery:
        return cls(kind=QueryKind.ACTIVE_BARRIERS)
    
    @classmethod
    def degraded_cycles(cls) -> OrchestrationQuery:
        return cls(kind=QueryKind.DEGRADED_CYCLES)