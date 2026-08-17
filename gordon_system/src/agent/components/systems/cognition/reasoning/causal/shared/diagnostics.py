# Causal Diagnostics - Phase 7.5
# ==============================

"""
Canonical Causal Diagnostics.

Diagnostics provide insight into the causal reasoning process.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class DiagnosticEvent:
    """
    A single diagnostic event during causal reasoning.
    """
    
    # Identity
    event_id: str                       # Unique event identifier
    
    # Event type
    event_type: str                     # e.g., "mechanism_selected", "graph_construction_started"
    
    # Timestamp
    timestamp_utc: float = field(default_factory=time.time)
    
    # Context
    context: Optional[str] = None       # Additional context
    
    # Data (can be any diagnostic data)
    data: Dict[str, Any] = field(default_factory=dict)  # Diagnostic data


@dataclass(frozen=True)
class CausalDiagnostics:
    """
    Diagnostics for a causal reasoning session.
    
    Provides insight into the reasoning process without modifying it.
    """
    
    # Identity
    diagnostics_id: str                 # Unique diagnostics identifier
    
    # Events captured
    events: Tuple[DiagnosticEvent, ...]  # All diagnostic events
    
    # Summary statistics
    event_count: int = 0                # Total number of events
    duration_seconds: float = 0.0       # Total reasoning duration
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if diagnostics capture a complete session."""
        event_types = {e.event_type for e in self.events}
        required_events = {"session_started", "session_completed"}
        return required_events.issubset(event_types)


def make_diagnostics(
    events: List[DiagnosticEvent],
) -> CausalDiagnostics:
    """Create new diagnostics."""
    events_tuple = tuple(events)
    
    # Calculate duration if start and end timestamps exist
    start_times = [e.timestamp_utc for e in events_tuple if "start" in e.event_type.lower()]
    end_times = [e.timestamp_utc for e in events_tuple if "complete" in e.event_type.lower() or "end" in e.event_type.lower()]
    
    duration = 0.0
    if start_times and end_times:
        duration = max(end_times) - min(start_times)
    
    return CausalDiagnostics(
        diagnostics_id=f"diagnostics:{uuid.uuid4().hex[:16]}",
        events=events_tuple,
        event_count=len(events_tuple),
        duration_seconds=duration,
    )


__all__ = [
    "DiagnosticEvent",
    "CausalDiagnostics",
]