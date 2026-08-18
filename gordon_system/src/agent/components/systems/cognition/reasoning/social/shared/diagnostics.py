# Social Diagnostics - Phase 7.32
# ===============================

"""
Canonical Social Diagnostics.

Diagnostics provide detailed information about:
- Session execution status
- Stage-specific issues  
- Performance metrics
- Error details
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class SocialDiagnostics:
    """
    Social diagnostics result.
    
    Contains detailed diagnostic information about social reasoning execution:
        - Session status (CREATED, INITIALIZING, OBSERVING, etc.)
        - Stage-specific metrics
        - Error details if any stage failed
        - Performance timing for each stage
        
    Diagnostics remain independently inspectable.
    """
    
    # Identity
    diagnostics_id: str                       # Unique identifier
    
    # Session status
    session_status: str = "CREATED"           # Current lifecycle state
    lifecycle_state_history: Tuple[str, ...] = ()  # State transitions
    
    # Stage metrics (timing, results count)
    stage_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Errors (if any)
    errors: Tuple[Dict[str, Any], ...] = ()
    
    # Performance
    total_duration_seconds: float = 0.0
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: Optional[float] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if diagnostics show a completed session."""
        return self.session_status in ("COMPLETED", "ARCHIVED")
    
    @property
    def has_errors(self) -> bool:
        """Check if any errors were recorded."""
        return len(self.errors) > 0
    
    @classmethod
    def create(cls, session_id: str) -> SocialDiagnostics:
        """Create a new diagnostics record."""
        return cls(
            diagnostics_id=f"diag:{uuid.uuid4().hex[:16]}",
            session_status="CREATED",
            start_time_utc=time.time(),
        )
    
    def with_stage_metric(self, stage_name: str, metrics: Dict[str, Any]) -> SocialDiagnostics:
        """Return a copy with stage metrics added."""
        new_metrics = {**self.stage_metrics}
        new_metrics[stage_name] = metrics
        return dataclass_replace(
            self,
            stage_metrics=new_metrics,
        )
    
    def with_error(self, error: Dict[str, Any]) -> SocialDiagnostics:
        """Return a copy with an additional error."""
        return dataclass_replace(
            self,
            errors=self.errors + (error,),
        )


@dataclass(frozen=True)
class DiagnosticLogEntry:
    """
    A single diagnostics log entry.
    
    Includes:
        - Timestamp
        - Log level (debug, info, warning, error)
        - Message
        - Context data
    """
    
    timestamp_utc: float                      # When was this logged?
    level: str                                # debug, info, warning, error
    message: str                              # What happened?
    context: Dict[str, Any] = field(default_factory=dict)  # Additional data
    
    def to_dict(self) -> Dict[str, Any]:
        """Create a dictionary representation."""
        return {
            "timestamp": self.timestamp_utc,
            "level": self.level,
            "message": self.message,
            "context": self.context,
        }


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SocialDiagnostics",
    "DiagnosticLogEntry",
]