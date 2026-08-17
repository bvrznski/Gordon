# Relational Reasoning Descriptor - Phase 7.11
# =============================================

"""
Canonical Relational Reasoning Descriptor.

A descriptor exposes relational reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class RelationalMode(Enum):
    """Relational reasoning modes."""
    
    RELATION_DISCOVERY = "relation_discovery"       # Discover relationships between entities
    GRAPH_CONSTRUCTION = "graph_construction"       # Build relational graphs
    STRUCTURAL_INFERENCE = "structural_inference"   # Infer structures from relations
    COMPOSITION_ANALYSIS = "composition_analysis"   # Analyze structural composition
    CONSTRAINT_PROPAGATION = "constraint_propagation"  # Propagate constraints through graph
    GRAPH_ANALYSIS = "graph_analysis"               # Analyze graph structure
    VALIDATION = "validation"                       # Validate relational structures
    GOVERNANCE = "governance"                       # Governance evaluation


class RelationalState(Enum):
    """Relational reasoning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    ENTITY_COLLECTION = "entity_collection"
    RELATION_DISCOVERY = "relation_discovery"
    GRAPH_CONSTRUCTION = "graph_construction"
    STRUCTURAL_INFERENCE = "structural_inference"
    CONSTRAINT_PROPAGATION = "constraint_propagation"
    COMPOSITION_ANALYSIS = "composition_analysis"
    VALIDATION = "validation"
    GOVERNANCE = "governance"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class RelationalDescriptor:
    """
    Descriptor exposing relational reasoning metadata independently of execution.
    
    A descriptor contains:
        - Relational identity (immutable, persistent across runs)
        - Reasoning goal
        - Relational mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what relational reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    relational_identity: str                # Relational identity (stable across runs)
    
    # Reasoning goal
    reasoning_goal: str                     # What are we reasoning about?
    
    # Relational mode
    relational_mode: RelationalMode = RelationalMode.RELATION_DISCOVERY
    
    # Lifecycle state
    lifecycle_state: RelationalState = RelationalState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did reasoning originate?
    
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
        """Check if reasoning completed."""
        return self.lifecycle_state == RelationalState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if reasoning failed."""
        return self.lifecycle_state == RelationalState.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if reasoning is archived."""
        return self.lifecycle_state == RelationalState.ARCHIVED
    
    @classmethod
    def create(
        cls,
        relational_identity: str,
        reasoning_goal: str,
        relational_mode: RelationalMode = RelationalMode.RELATION_DISCOVERY,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> RelationalDescriptor:
        """Create a new relational descriptor."""
        return cls(
            descriptor_id=f"relational_descriptor:{uuid.uuid4().hex[:16]}",
            relational_identity=relational_identity,
            reasoning_goal=reasoning_goal,
            relational_mode=relational_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: RelationalState) -> RelationalDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == RelationalState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RelationalDescriptor",
    "RelationalMode",
    "RelationalState",
]
