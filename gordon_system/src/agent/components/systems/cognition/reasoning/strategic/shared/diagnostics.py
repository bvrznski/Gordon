# Strategic Diagnostics - Phase 7.18
# ==================================

"""
Canonical Strategic Diagnostics for Phase 7.18.

Diagnostics provide observability into strategic reasoning operations.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategicDiagnostics:
    """
    Diagnostic information for a strategic reasoning session.
    
    Diagnostics track:
        - Performance metrics (timing, resource usage)
        - Reasoning steps (what was computed at each step)
        - Decision points (where decisions were made)
        - Observability data (for debugging and audit)
    """
    
    # Identity
    diagnostics_id: str                     # Unique diagnostics identifier
    
    # Session being diagnosed
    session_identity: str                   # Which session?
    
    # Performance metrics
    performance_metrics: Dict[str, float] = field(default_factory=dict)  # metric -> value
    
    # Reasoning steps logged
    reasoning_steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Decision points tracked
    decision_points: List[Dict[str, Any]] = field(default_factory=list)
    
    # Warnings or issues detected
    warnings: List[str] = field(default_factory=list)
    
    # Timing
    captured_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class DiagnosticEvent:
    """
    A single diagnostic event during reasoning.
    """
    
    # Event type
    event_type: str                         # e.g., "step_start", "decision_made"
    
    # Context
    context_id: str                         # Session/strategy ID
    
    # Timestamp
    timestamp_utc: float = field(default_factory=time.time)
    
    # Event data
    event_data: Dict[str, Any]              # Structured event information


@dataclass(frozen=True)
class DiagnosticTrace:
    """
    Complete diagnostic trace for a strategic session.
    """
    
    # Identity
    trace_id: str
    
    # Session identity
    session_identity: str
    
    # Events in order
    events: List[DiagnosticEvent]
    
    # Summary metrics
    total_steps: int = 0
    total_time_seconds: float = 0.0
    
    # Timing
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None


__all__ = [
    "StrategicDiagnostics",
    "DiagnosticEvent",
    "DiagnosticTrace",
]