# Monitoring Observation Set - Phase 7.22
# =========================================

"""
Canonical Monitoring Observation Set.

Observation Sets define the scope and policies for monitoring observations.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class Observation:
    """
    A single observation from the monitored system.
    
    Observations provide explicit operational evidence about what is happening.
    """
    
    # Identity
    observation_id: str                       # Unique observation identifier
    
    # Source information
    observation_source: str                   # Where did this come from?
    source_type: str = "unknown"              # Type of observation source (e.g., "tool_output", "resource_metric")
    
    # Observed value
    observed_value: Any                       # The actual observation data
    observation_type: str = "generic"         # Type of observation
    
    # Timing
    timestamp_utc: float = field(default_factory=time.time)
    received_at_utc: float = field(default_factory=time.time)
    
    # Metadata
    confidence: Optional[float] = 1.0         # Confidence in this observation
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    @property
    def age_seconds(self) -> float:
        """Calculate age of this observation."""
        return time.time() - self.timestamp_utc


@dataclass(frozen=True)
class ObservationSet:
    """
    A set of observations with shared scope and policies.
    
    An Observation Set defines:
        - Which systems are being observed
        - Sampling policies for each system
        - Consistency constraints
        - Retention policies
    
    Observation Sets remain immutable during analysis.
    """
    
    # Identity
    observation_set_id: str                   # Unique observation set identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Participation
    participating_observations: List[Observation] = field(default_factory=list)
    
    # Scope definition
    observation_scope: List[str] = field(default_factory=list)  # Observed systems
    observation_streams: Dict[str, str] = field(default_factory=dict)  # stream_name -> system_id
    
    # Consistency constraints
    consistency_constraints: List[str] = field(default_factory=list)
    
    # Retention policy
    max_observations: int = 1000
    retention_seconds: float = 3600.0         # Keep observations for 1 hour by default
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_descriptor_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def observation_count(self) -> int:
        """Get the number of observations in this set."""
        return len(self.participating_observations)
    
    @property
    def is_empty(self) -> bool:
        """Check if this observation set is empty."""
        return self.observation_count == 0
    
    @property
    def oldest_observation(self) -> Optional[Observation]:
        """Get the oldest observation in this set."""
        if not self.participating_observations:
            return None
        return min(self.participating_observations, key=lambda o: o.timestamp_utc)
    
    @property
    def newest_observation(self) -> Optional[Observation]:
        """Get the newest observation in this set."""
        if not self.participating_observations:
            return None
        return max(self.participating_observations, key=lambda o: o.timestamp_utc)
    
    def get_observations_by_source(self, source: str) -> List[Observation]:
        """Get all observations from a specific source."""
        return [o for o in self.participating_observations if o.observation_source == source]
    
    def get_observations_by_type(self, obs_type: str) -> List[Observation]:
        """Get all observations of a specific type."""
        return [o for o in self.participating_observations if o.observation_type == obs_type]
    
    def add_observation(self, observation: Observation) -> ObservationSet:
        """Add an observation and return updated set."""
        new_observations = list(self.participating_observations)
        
        # Enforce max observations limit
        while len(new_observations) >= self.max_observations:
            # Remove oldest observation
            if new_observations:
                oldest_idx = min(range(len(new_observations)), 
                               key=lambda i: new_observations[i].timestamp_utc)
                new_observations.pop(oldest_idx)
        
        new_observations.append(observation)
        
        return dataclass_replace(
            self,
            participating_observations=new_observations,
        )
    
    def filter_by_time_range(self, start_utc: float, end_utc: float) -> ObservationSet:
        """Filter observations to a time range."""
        filtered = [
            o for o in self.participating_observations
            if start_utc <= o.timestamp_utc <= end_utc
        ]
        
        return dataclass_replace(
            self,
            participating_observations=filtered,
        )
    
    def filter_by_source(self, source: str) -> ObservationSet:
        """Filter observations by source."""
        filtered = [
            o for o in self.participating_observations
            if o.observation_source == source
        ]
        
        return dataclass_replace(
            self,
            participating_observations=filtered,
        )
    
    def to_state(self, new_identity: str) -> ObservationSet:
        """Return a copy with updated semantic identity."""
        return dataclass_replace(
            self,
            semantic_identity=new_identity,
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        observation_scope: Optional[List[str]] = None,
        observation_streams: Optional[Dict[str, str]] = None,
        max_observations: int = 1000,
        retention_seconds: float = 3600.0,
        source_descriptor_id: Optional[str] = None,
    ) -> ObservationSet:
        """Create a new observation set."""
        return cls(
            observation_set_id=f"obsset:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            observation_scope=observation_scope or [],
            observation_streams=observation_streams or {},
            max_observations=max_observations,
            retention_seconds=retention_seconds,
            source_descriptor_id=source_descriptor_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "Observation",
    "ObservationSet",
]