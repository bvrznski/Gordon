# World-Model Reasoning Diagnostics - Phase 7.44
# =================================

"""
Canonical World Model Diagnostics.

Diagnostics provide detailed information about world model operations.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class DiagnosticEvent:
    """
    A diagnostic event during world model reasoning.
    """
    
    event_id: str
    timestamp_utc: float
    level: str  # "debug", "info", "warning", or "error"
    
    kind: str
    message: str
    
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorldDiagnostics:
    """
    World model diagnostic information.
    """
    
    diagnostics_id: str
    
    events: List[DiagnosticEvent] = field(default_factory=list)
    
    debug_count: int = 0
    info_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    
    total_duration_seconds: float = 0.0
    
    timestamp_utc: float = field(default_factory=time.time)
    provenance: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        provenance: Optional[str] = None,
    ) -> WorldDiagnostics:
        """Create a new world diagnostics log."""
        return cls(
            diagnostics_id=f"diagnostics:{uuid.uuid4().hex[:16]}",
            events=[],
            debug_count=0,
            info_count=0,
            warning_count=0,
            error_count=0,
            total_duration_seconds=0.0,
            provenance=provenance,
        )
    
    def add_event(self, event: DiagnosticEvent) -> WorldDiagnostics:
        """Add a diagnostic event."""
        new_events = self.events + [event]
        
        return dataclass_replace(
            self,
            events=new_events,
            debug_count=self.debug_count + (1 if event.level == "debug" else 0),
            info_count=self.info_count + (1 if event.level == "info" else 0),
            warning_count=self.warning_count + (1 if event.level == "warning" else 0),
            error_count=self.error_count + (1 if event.level == "error" else 0),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DiagnosticEvent",
    "WorldDiagnostics",
]