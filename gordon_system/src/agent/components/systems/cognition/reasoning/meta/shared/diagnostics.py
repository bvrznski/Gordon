# Meta Reasoning Diagnostics - Phase 7.13
# ========================================

"""
Canonical Meta Reasoning Diagnostics definition.

Diagnostics provide diagnostic information for meta-reasoning execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class DiagnosticEvent:
    """
    A diagnostic event during meta-reasoning execution.
    
    Diagnostics provide visibility into internal operations.
    """
    
    # Identity
    event_id: str                           # Unique event identifier
    
    # Event details
    kind: str                               # Event type (e.g., "orchestration_start")
    message: str = ""                       # Human-readable description
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    # Timing
    occurred_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class MetaReasoningDiagnostics:
    """
    Diagnostics for meta-reasoning execution.
    
    A diagnostics result contains:
        - Identity and provenance
        - Diagnostic events collected
        - Diagnostic summary
    
    Diagnostics remain inspectable but don't modify execution.
    """
    
    # Identity
    diagnostics_id: str                     # Unique diagnostics identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Events
    diagnostic_events: List[DiagnosticEvent] = field(default_factory=list)
    
    # Summary
    event_count_by_kind: Dict[str, int] = field(default_factory=dict)  # Kind -> count
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate diagnostics collection time."""
        if self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        return 0.0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
    ) -> MetaReasoningDiagnostics:
        """Create new diagnostics collection."""
        return cls(
            diagnostics_id=f"diagnostics:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
        )
    
    def record_event(self, kind: str, message: str = "") -> MetaReasoningDiagnostics:
        """Record a diagnostic event."""
        new_events = self.diagnostic_events + [DiagnosticEvent(
            event_id=f"diag_event:{uuid.uuid4().hex[:16]}",
            kind=kind,
            message=message,
            occurred_at_utc=time.time(),
        )]
        
        # Update counts
        new_counts = dict(self.event_count_by_kind)
        new_counts[kind] = new_counts.get(kind, 0) + 1
        
        return dataclass_replace(
            self,
            diagnostic_events=new_events,
            event_count_by_kind=new_counts,
        )
    
    def to_completed(self) -> MetaReasoningDiagnostics:
        """Mark diagnostics as completed."""
        return dataclass_replace(
            self,
            completed_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MetaReasoningDiagnostics",
    "DiagnosticEvent",
]