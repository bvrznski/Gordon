# Canonical Prediction Error Trace System
# =======================================
"""
Trace system for Prediction Error Network Phase 4.9.2.

This module provides:
    - PredictionErrorTrace: Immutable structural trace of error construction

PHASE BOUNDARY:
    This is pure semantic infrastructure with NO runtime dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# PREDICTION ERROR TRACE (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionErrorTrace:
    """
    Immutable structural trace of prediction error construction.
    
    Fields:
        events:             Ordered sequence of trace codes
        timestamps:         Timestamps for each event (semantic reference)
        metadata:           Additional context
        
    Rules:
        - Trace contains stable codes, not hidden reasoning text
        - No side effects in trace recording
    """
    events: tuple[str, ...] = field(default_factory=tuple)  # TraceCode codes
    timestamps: dict[str, str] | None = None  # event_id -> semantic_time_ref
    metadata: dict[str, Any] | None = None


# =============================================================================
# TRACE BUILDER (FOR CONSTRUCTION)
# =============================================================================

class TraceBuilder:
    """
    Builder for PredictionErrorTrace.
    
    Rules:
        - Immutable trace construction only
        - No runtime dependencies
    """
    
    def __init__(self) -> None:
        self._events: list[str] = []
        self._timestamps: dict[str, str] = {}
        self._metadata: dict[str, Any] = {}
    
    def add_event(self, code: str, timestamp_ref: str | None = None) -> None:
        """Add a trace event with optional semantic timestamp."""
        self._events.append(code)
        if timestamp_ref is not None:
            self._timestamps[code] = timestamp_ref
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata for the trace."""
        self._metadata[key] = value
    
    def build(self) -> PredictionErrorTrace:
        """Build the immutable trace."""
        timestamps = dict(self._timestamps) if self._timestamps else None
        metadata = dict(self._metadata) if self._metadata else None
        return PredictionErrorTrace(
            events=tuple(self._events),
            timestamps=timestamps,
            metadata=metadata
        )