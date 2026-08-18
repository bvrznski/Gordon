# Monitoring Descriptor - Phase 7.22
# ====================================

"""
Canonical Monitoring Descriptor.

A descriptor exposes monitoring metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class MonitoringMode(Enum):
    """Modes of monitoring reasoning."""
    
    SESSION_BASED = "session_based"               # Session-based monitoring
    CONTINUOUS = "continuous"                     # Continuous operational monitoring
    EVENT_DRIVEN = "event_driven"                 # Event-driven monitoring
    SCHEDULED = "scheduled"                       # Scheduled monitoring


class MonitoringLifecycle(Enum):
    """Monitoring session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    CONFIGURING = "configuring"
    OBSERVING = "observing"
    TRACKING = "tracking"
    DETECTING = "detecting"
    VALIDATING = "validating"
    ACTIVE = "active"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class MonitoringDescriptor:
    """
    Descriptor exposing monitoring metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Monitoring goal
        - Monitoring mode and scope
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what monitoring occurred without
    needing to execute the full process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reasoning goal
    monitoring_goal: str                      # What are we observing?
    
    # Monitoring mode and scope
    monitoring_mode: MonitoringMode           # What kind of monitoring?
    observation_scope: List[str] = field(default_factory=list)  # Observed systems
    
    # Lifecycle state
    lifecycle_state: MonitoringLifecycle = MonitoringLifecycle.CREATED
    
    # Constraints
    sampling_interval_seconds: float = 1.0     # Observation sampling rate
    max_observation_history: int = 1000        # Maximum observations to retain
    anomaly_threshold: float = 0.95            # Anomaly detection threshold
    
    # Compatibility
    compatibility_revision: int = 1            # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did monitoring originate?
    
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
        """Check if monitoring completed."""
        return self.lifecycle_state == MonitoringLifecycle.ARCHIVED
    
    @property
    def is_failed(self) -> bool:
        """Check if monitoring failed."""
        return self.lifecycle_state == MonitoringLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        monitoring_goal: str,
        monitoring_mode: MonitoringMode = MonitoringMode.SESSION_BASED,
        observation_scope: Optional[List[str]] = None,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        sampling_interval_seconds: float = 1.0,
    ) -> MonitoringDescriptor:
        """Create a new monitoring descriptor."""
        return cls(
            descriptor_id=f"monitoring:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            monitoring_goal=monitoring_goal,
            monitoring_mode=monitoring_mode,
            observation_scope=observation_scope or [],
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            sampling_interval_seconds=sampling_interval_seconds,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: MonitoringLifecycle) -> MonitoringDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == MonitoringLifecycle.ARCHIVED else None,
        )


@dataclass(frozen=True)
class MonitoringSessionIdentity:
    """
    Immutable identity for a monitoring session.
    
    Allows replay and verification of monitoring results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> MonitoringSessionIdentity:
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
    "MonitoringDescriptor",
    "MonitoringSessionIdentity",
    "MonitoringMode",
    "MonitoringLifecycle",
]