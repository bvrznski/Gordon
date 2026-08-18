# Monitoring Operational State Contract - Phase 7.22
# ==================================================

"""
Canonical Operational State.

Operational State represents the current state of the monitored system.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ConsistencyStatus(Enum):
    """Status of operational state consistency."""
    
    UNKNOWN = "unknown"                         # Not yet evaluated
    CONSISTENT = "consistent"                   # State is consistent
    INCONSISTENT = "inconsistent"               # State has inconsistencies
    PARTIAL = "partial"                         # Only partial information available


@dataclass(frozen=True)
class ActiveComponent:
    """
    An actively monitored component.
    """
    
    # Identity
    component_id: str                         # Unique component identifier
    
    # Component details
    component_type: str                       # Type (e.g., "tool", "reasoner", "service")
    component_name: str = ""                  # Human-readable name
    
    # State
    state: str = "unknown"                    # Current operational state
    status: str = "active"                    # active, paused, failed, completed
    
    # Timing
    started_at_utc: Optional[float] = None
    last_update_utc: float = field(default_factory=time.time)
    
    # Metadata
    resource_usage: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OperationalState:
    """
    The operational state at a point in time.
    
    An Operational State contains:
        - Identity and provenance
        - Active components being monitored
        - State snapshot (resource usage, execution status)
        - Consistency verification
        - Supporting observations
    
    Operational states remain explicit and inspectable.
    """
    
    # Identity
    state_id: str                             # Unique state identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # State components
    active_components: List[ActiveComponent] = field(default_factory=list)
    
    # State snapshot
    state_snapshot: Dict[str, Any] = field(default_factory=dict)
    
    # Consistency status
    consistency_status: ConsistencyStatus = ConsistencyStatus.UNKNOWN
    
    # Supporting observations
    supporting_observations: List[str] = field(default_factory=list)  # References to observation IDs
    
    # Timing
    recorded_at_utc: float = field(default_factory=time.time)
    previous_state_id: Optional[str] = None   # For state transition tracking
    
    # Provenance
    source_descriptor_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def component_count(self) -> int:
        """Get the number of active components."""
        return len(self.active_components)
    
    @property
    def is_consistent(self) -> bool:
        """Check if state is consistent."""
        return self.consistency_status == ConsistencyStatus.CONSISTENT
    
    @property
    def has_inconsistencies(self) -> bool:
        """Check if state has inconsistencies."""
        return self.consistency_status == ConsistencyStatus.INCONSISTENT
    
    def get_component_by_id(self, component_id: str) -> Optional[ActiveComponent]:
        """Get a specific component by ID."""
        for comp in self.active_components:
            if comp.component_id == component_id:
                return comp
        return None
    
    def get_components_by_type(self, component_type: str) -> List[ActiveComponent]:
        """Get all components of a specific type."""
        return [c for c in self.active_components if c.component_type == component_type]
    
    def update_component(
        self,
        component_id: str,
        state: Optional[str] = None,
        status: Optional[str] = None,
        resource_usage: Optional[Dict[str, Any]] = None,
    ) -> OperationalState:
        """Update an existing component."""
        new_components = list(self.active_components)
        
        for i, comp in enumerate(new_components):
            if comp.component_id == component_id:
                new_comp = dataclass_replace(
                    comp,
                    state=state or comp.state,
                    status=status or comp.status,
                    resource_usage=resource_usage or comp.resource_usage,
                    last_update_utc=time.time(),
                )
                new_components[i] = new_comp
                break
        
        return dataclass_replace(
            self,
            active_components=new_components,
        )
    
    def add_component(self, component: ActiveComponent) -> OperationalState:
        """Add a new active component."""
        new_components = list(self.active_components)
        if not any(c.component_id == component.component_id for c in new_components):
            new_components.append(component)
        
        return dataclass_replace(
            self,
            active_components=new_components,
        )
    
    def add_observation_reference(self, observation_id: str) -> OperationalState:
        """Add a reference to an observation supporting this state."""
        new_observations = list(self.supporting_observations)
        if observation_id not in new_observations:
            new_observations.append(observation_id)
        
        return dataclass_replace(
            self,
            supporting_observations=new_observations,
        )
    
    def update_consistency_status(self, status: ConsistencyStatus) -> OperationalState:
        """Update consistency status."""
        return dataclass_replace(
            self,
            consistency_status=status,
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        source_descriptor_id: Optional[str] = None,
    ) -> OperationalState:
        """Create a new operational state snapshot."""
        return cls(
            state_id=f"state:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            recorded_at_utc=time.time(),
            source_descriptor_id=source_descriptor_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "OperationalState",
    "ActiveComponent",
    "ConsistencyStatus",
]