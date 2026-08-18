# Planning Reasoning Descriptor - Phase 7.20
# ===========================================

"""
Canonical Planning Descriptor for Phase 7.20.

A descriptor exposes planning reasoning metadata independently of execution.
Planning is Gordon's operational synthesis engine - it transforms commitments 
into executable operational structures without performing execution itself.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class PlanningMode(Enum):
    """Modes of planning reasoning."""
    
    STRATEGIC_PLANNING = "strategic_planning"           # High-level strategic plans
    TACTICAL_PLANNING = "tactical_planning"             # Mid-level tactical execution plans
    OPERATIONAL_PLANNING = "operational_planning"       # Detailed operational tasks
    HYBRID_PLANNING = "hybrid_planning"                 # Combined hierarchical planning
    PARTIAL_ORDER_PLANNING = "partial_order_planning"   # Partial-order (nonlinear) planning


class PlanningLifecycle(Enum):
    """Planning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    OBJECTIVE_ANALYSIS = "objective_analysis"
    TASK_DECOMPOSITION = "task_decomposition"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    RESOURCE_ALLOCATION = "resource_allocation"
    CONTINGENCY_PLANNING = "contingency_planning"
    VALIDATION = "validation"
    READY = "ready"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class PlanningDescriptor:
    """
    Descriptor exposing planning reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Planning goal
        - Planning mode and constraints
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what planning occurred without
    needing to execute the full planning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Planning goal
    planning_goal: str                        # What are we trying to achieve?
    
    # Planning mode and constraints
    planning_mode: PlanningMode               # What kind of planning?
    planning_constraints: Tuple[str, ...] = ()  # Explicit planning constraints
    
    # Lifecycle state
    lifecycle_state: PlanningLifecycle = PlanningLifecycle.CREATED
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did planning originate?
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if planning completed."""
        return self.lifecycle_state in (PlanningLifecycle.READY, PlanningLifecycle.PUBLISHED)
    
    @property
    def is_failed(self) -> bool:
        """Check if planning failed."""
        return self.lifecycle_state == PlanningLifecycle.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if planning is archived."""
        return self.lifecycle_state == PlanningLifecycle.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        planning_goal: str,
        planning_mode: PlanningMode = PlanningMode.STRATEGIC_PLANNING,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        planning_constraints: Tuple[str, ...] = (),
    ) -> PlanningDescriptor:
        """Create a new planning descriptor."""
        return cls(
            descriptor_id=f"planning:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            planning_goal=planning_goal,
            planning_mode=planning_mode,
            planning_constraints=planning_constraints,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: PlanningLifecycle) -> PlanningDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == PlanningLifecycle.PUBLISHED else None,
        )


@dataclass(frozen=True)
class PlanningSessionIdentity:
    """
    Immutable identity for a planning session.
    
    Allows replay and verification of planning reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> PlanningSessionIdentity:
        """Create a new session identity."""
        return cls(
            semantic_identity=semantic_identity,
            session_number=session_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "PlanningDescriptor",
    "PlanningSessionIdentity",
    "PlanningMode",
    "PlanningLifecycle",
]