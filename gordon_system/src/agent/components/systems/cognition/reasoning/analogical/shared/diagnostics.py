# Analogy Diagnostics - Phase 7.4
# ==============================

"""
Canonical Analogy Diagnostics Contract.

Diagnostics provide detailed operational information about analogy sessions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class AnalogyTrace:
    """
    Complete trace of an analogy session.
    
    Trace includes:
        - Retrieved cases
        - Mappings considered (including rejected)
        - Transferred knowledge
        - Validation results
        - All diagnostic information
    
    Trace remains inspectable for debugging and verification.
    """
    
    # Identity
    trace_id: str                             # Unique identifier
    
    # Mapping steps (in order)
    mapping_steps: Tuple[Dict[str, Any], ...] = ()
    
    # Transferred artifacts
    transferred_artifacts: Tuple[str, ...] = ()
    
    # Diagnostics
    diagnostics: Tuple[Dict[str, Any], ...] = ()
    
    # Metadata
    generated_at_utc: float = field(default_factory=time.time)
    
    @property
    def step_count(self) -> int:
        """Number of mapping steps recorded."""
        return len(self.mapping_steps)
    
    @classmethod
    def create(cls) -> AnalogyTrace:
        """Create a new trace."""
        return cls(
            trace_id=f"analogy_trace:{uuid.uuid4().hex[:16]}",
        )
    
    def add_mapping_step(self, step: Dict[str, Any]) -> AnalogyTrace:
        """Add a mapping step to the trace."""
        return dataclass_replace(
            self,
            mapping_steps=self.mapping_steps + (step,),
        )
    
    def add_diagnostic(self, diagnostic: Dict[str, Any]) -> AnalogyTrace:
        """Add a diagnostic entry."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + (diagnostic,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AnalogyTrace",
]