# Adaptation Diagnostics - Phase 7.25
# ===================================

"""
Canonical Adaptation Diagnostics contract.

Diagnostics provide visibility into adaptation operations.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class AdaptationDiagnostic:
    """
    A diagnostic observation about adaptation operations.
    """
    
    # Identity
    diagnostic_identity: str              # Unique diagnostic identifier
    
    # Category
    diagnostic_category: str              # e.g., "behavior", "configuration"
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class AdaptationTrace:
    """
    Trace of an adaptation session.
    
    Every Adaptation Session produces a trace containing:
        - Adaptation candidates
        - Behavior changes
        - Configuration refinements
        - Context adjustments
        - Validation results
        - Diagnostics
    
    Trace remains inspectable.
    """
    
    # Identity
    trace_identity: str                   # Unique trace identifier
    
    # History
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Adaptation graph (relationships between adaptations)
    adaptation_graph: Dict[str, Any] = field(default_factory=dict)
    
    # Diagnostics
    diagnostics: Tuple[AdaptationDiagnostic, ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_complete(self) -> bool:
        """Check if trace has a complete lifecycle."""
        return any(h.get("state") == "completed" for h in self.adaptation_history)
    
    @classmethod
    def create(
        cls,
        adaptation_candidates: Optional[List[str]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> AdaptationTrace:
        """Create a new adaptation trace."""
        history = []
        if adaptation_candidates:
            for candidate_id in adaptation_candidates:
                history.append({
                    "candidate_id": candidate_id,
                    "state": "created",
                    "timestamp_utc": time.time(),
                })
        
        return cls(
            trace_identity=f"trace:{uuid.uuid4().hex[:16]}",
            adaptation_history=history,
            provenance=provenance or {},
        )
    
    def record_state_change(self, candidate_id: str, new_state: str) -> AdaptationTrace:
        """Record a state change for a candidate."""
        new_history = [
            *self.adaptation_history,
            {
                "candidate_id": candidate_id,
                "state": new_state,
                "timestamp_utc": time.time(),
            },
        ]
        return dataclass_replace(
            self,
            adaptation_history=new_history,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AdaptationTrace",
    "AdaptationDiagnostic",
]