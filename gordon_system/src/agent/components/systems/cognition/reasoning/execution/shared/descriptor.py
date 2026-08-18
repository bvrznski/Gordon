# Execution Reasoning Descriptor - Phase 7.21
# ===========================================

"""
Canonical Execution Descriptor for Phase 7.21.

A descriptor exposes execution metadata independently of actual execution.
Execution Reasoning is Gordon's behavior orchestration engine - it governs
when, how and under which conditions actions are performed without performing
primitive actions itself.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ExecutionMode(Enum):
    """Modes of execution reasoning."""
    
    STRATEGIC_EXECUTION = "strategic_execution"     # High-level strategic action orchestration
    TACTICAL_EXECUTION = "tactical_execution"       # Mid-level tactical command sequencing
    OPERATIONAL_EXECUTION = "operational_execution"  # Detailed operational coordination
    HYBRID_EXECUTION = "hybrid_execution"            # Combined hierarchical execution
    DISTRIBUTED_EXECUTION = "distributed_execution"  # Multi-agent distributed orchestration


class ExecutionLifecycle(Enum):
    """Execution session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    AUTHORIZING = "authoring"
    EXECUTING = "executing"
    SUSPENDED = "suspended"
    ADAPTING = "adapting"
    ROLLING_BACK = "rolling_back"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class ExecutionDescriptor:
    """
    Descriptor exposing execution metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Execution goal and plan
        - Execution mode and constraints
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what execution occurred without
    needing to execute the full process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Execution goal
    execution_goal: str                       # What are we trying to achieve?
    
    # Execution mode and constraints
    execution_mode: ExecutionMode             # What kind of execution?
    execution_constraints: Tuple[str, ...] = ()  # Explicit execution constraints
    
    # Lifecycle state
    lifecycle_state: ExecutionLifecycle = ExecutionLifecycle.CREATED
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did execution originate?
    
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
        """Check if execution completed."""
        return self.lifecycle_state in (ExecutionLifecycle.COMPLETED, ExecutionLifecycle.ARCHIVED)
    
    @property
    def is_failed(self) -> bool:
        """Check if execution failed."""
        return self.lifecycle_state == ExecutionLifecycle.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if execution is archived."""
        return self.lifecycle_state == ExecutionLifecycle.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        execution_goal: str,
        execution_mode: ExecutionMode = ExecutionMode.STRATEGIC_EXECUTION,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        execution_constraints: Tuple[str, ...] = (),
    ) -> ExecutionDescriptor:
        """Create a new execution descriptor."""
        return cls(
            descriptor_id=f"execution:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            execution_goal=execution_goal,
            execution_mode=execution_mode,
            execution_constraints=execution_constraints,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: ExecutionLifecycle) -> ExecutionDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == ExecutionLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class ExecutionSessionIdentity:
    """
    Immutable identity for an execution session.
    
    Allows replay and verification of execution reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> ExecutionSessionIdentity:
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
    "ExecutionDescriptor",
    "ExecutionSessionIdentity",
    "ExecutionMode",
    "ExecutionLifecycle",
]