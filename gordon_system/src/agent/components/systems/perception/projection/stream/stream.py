# Perception Stream Projection - Phase 5.2.4
# ==========================================

"""
Stream Projection: Publishes a sequence of perceptual updates.

A Stream Projection publishes a sequence of perceptual updates. Streams expose
dropped, delayed or reordered updates and provide gap detection capabilities.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# STREAM PROJECTION
# =============================================================================


@dataclass(frozen=True)
class PerceptionProjectionStream:
    """
    Stream of perceptual updates from the Projection Engine.
    
    A stream is a publication channel. It does not own the underlying Projection
    artifacts but provides continuous updates to consumers.
    
    Fields:
        stream_identity:          Unique identifier for this stream
        request_reference:        Reference to the original request
        subscription_scope:       Subscription parameters
        starting_revision:        Revision where stream starts
        current_revision:         Current revision of the stream
        ordering_guarantees:      Ordering guarantees provided
        backpressure_policy:      How backpressure is handled
        gap_policy:               How gaps are detected and reported
        status:                   Stream status (active, suspended, terminated)
        health:                   Stream health metrics
    """
    
    stream_identity: str
    
    # Request reference
    request_reference: Optional[str] = None
    
    # Subscription scope
    subscription_scope: Dict[str, Any] = field(default_factory=dict)  # Scope parameters
    
    # Revision tracking
    starting_revision: int = 1
    current_revision: int = 1
    latest_acknowledged_revision: int = 0
    
    # Ordering guarantees
    ordering_guarantees: str = "best_effort"  # strict, per_source, causal, partial, best_effort, unordered
    
    # Backpressure and gap handling
    backpressure_policy: str = "buffer"  # buffer, drop_oldest, drop_newest, coalesce, snapshot_recovery, suspend, fail
    gap_policy: str = "detect_and_notify"  # detect, ignore, auto_recovery
    
    # Status
    status: str = "active"  # active, suspended, terminated, error
    
    # Health metrics
    buffer_capacity: int = 1000
    current_backlog: int = 0
    dropped_update_count: int = 0
    coalesced_update_count: int = 0
    gap_count: int = 0
    last_heartbeat_utc: float = field(default_factory=_time.time)
    
    @classmethod
    def create(
        cls,
        request_ref: str,
        starting_revision: int = 1,
        ordering_guarantees: str = "best_effort",
        backpressure_policy: str = "buffer",
        gap_policy: str = "detect_and_notify",
    ) -> "PerceptionProjectionStream":
        """
        Create a new Stream Projection.
        
        Args:
            request_ref: Reference to the original projection request
            starting_revision: Revision where stream starts
            ordering_guarantees: Ordering guarantees
            backpressure_policy: How backpressure is handled
            gap_policy: How gaps are detected and reported
            
        Returns:
            New PerceptionProjectionStream instance
        """
        return cls(
            stream_identity=f"stream:{uuid.uuid4().hex[:24]}",
            request_reference=request_ref,
            starting_revision=starting_revision,
            ordering_guarantees=ordering_guarantees,
            backpressure_policy=backpressure_policy,
            gap_policy=gap_policy,
        )
    
    @classmethod
    def strict_ordering(
        cls,
        request_ref: str,
        starting_revision: int = 1,
    ) -> "PerceptionProjectionStream":
        """Create a stream with strict total ordering guarantees."""
        return cls.create(
            request_ref=request_ref,
            starting_revision=starting_revision,
            ordering_guarantees="strict_total_order",
            backpressure_policy="buffer",
            gap_policy="detect_and_notify",
        )
    
    @property
    def is_active(self) -> bool:
        """Check if the stream is active."""
        return self.status == "active"
    
    @property
    def has_gaps(self) -> bool:
        """Check if gaps have been detected in this stream."""
        return self.gap_count > 0
    
    @property
    def is_buffer_full(self) -> bool:
        """Check if the backpressure buffer is full."""
        return self.current_backlog >= self.buffer_capacity


__all__ = ["PerceptionProjectionStream"]