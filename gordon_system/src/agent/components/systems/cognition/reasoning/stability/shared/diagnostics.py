# Stability Diagnostics - Phase 7.26
# ===================================

"""
Canonical Stability Diagnostics.

Diagnostics provide trace, observability, and insight into stability operations.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StabilityDiagnostic:
    """A diagnostic observation about stability operations."""
    
    diagnostic_id: str
    diagnostic_type: str            # e.g., "homeostasis_check", "containment_applied"
    severity: float                 # 0.0 to 1.0
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StabilityTrace:
    """
    Complete trace of stability operations.
    
    Trace contains:
        - Stabilization history (what decisions were made and when)
        - Stability graph (relationships between subsystems and their states)
        - Diagnostics (observations about the process)
        - Provenance (where things came from)
    """
    
    trace_id: str
    stability_identity: str
    
    # Stabilization history (ordered list of events)
    stabilization_history: List[str] = field(default_factory=list)
    
    # Stability graph (subsystems and their relationships)
    stability_graph: Dict[str, Any] = field(default_factory=dict)
    
    # Diagnostics collected during the session
    diagnostics: List[StabilityDiagnostic] = field(default_factory=list)
    
    # Provenance
    provenance: str = "unknown"
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    def add_diagnostic(self, diagnostic: StabilityDiagnostic) -> StabilityTrace:
        """Return a new trace with the added diagnostic."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + [diagnostic],
        )
    
    def add_stabilization_event(self, event: str) -> StabilityTrace:
        """Return a new trace with the added stabilization event."""
        return dataclass_replace(
            self,
            stabilization_history=self.stabilization_history + [event],
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "StabilityTrace",
    "StabilityDiagnostic",
]