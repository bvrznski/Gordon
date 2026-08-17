# Relational Diagnostics - Phase 7.11
# ====================================

"""
Canonical Relational Diagnostics.

Diagnostics record the reasoning process for inspection and traceability.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class DiagnosticsRecord:
    """
    Individual diagnostics record during relational reasoning.
    
    Each record captures a specific event or observation in the reasoning process.
    """
    
    # Identity
    record_id: str                        # Unique record identifier
    
    # Record type
    record_type: str                      # e.g., "entity_discovery", "relation_inferred"
    
    # Timestamp
    timestamp_utc: float                  # When did this occur?
    
    # Details
    details: Tuple[str, ...] = ()         # Detailed information
    
    # Severity (for filtering)
    severity: str = "info"                # info, warning, error
    
    @classmethod
    def create(
        cls,
        record_type: str,
        details: Optional[List[str]] = None,
        severity: str = "info",
    ) -> DiagnosticsRecord:
        """Create a new diagnostics record."""
        return cls(
            record_id=f"diag_record:{uuid.uuid4().hex[:16]}",
            record_type=record_type,
            timestamp_utc=time.time(),
            details=tuple(details or []),
            severity=severity,
        )


@dataclass(frozen=True)
class RelationalTrace:
    """
    Complete trace of a relational reasoning session.
    
    Trace contains all entities, relations, graphs, inference results,
    validation findings, and diagnostics for full inspectability.
    """
    
    # Identity
    trace_id: str                         # Unique trace identifier
    
    # Reasoning steps
    reasoning_steps: Tuple[str, ...] = ()  # Step descriptions
    
    # Structural graph reference (snapshot)
    structural_graph: Optional[str] = None   # Reference to final graph state
    
    # Diagnostics
    diagnostics: Tuple[DiagnosticsRecord, ...] = ()  # All diagnostic records
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from another trace
    
    @classmethod
    def create(
        cls,
    ) -> RelationalTrace:
        """Create a new relational trace."""
        return cls(
            trace_id=f"relational_trace:{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
        )
    
    def record_step(self, step: str) -> RelationalTrace:
        """Record a reasoning step."""
        return dataclass_replace(
            self,
            reasoning_steps=self.reasoning_steps + (step,),
        )
    
    def add_diagnostic(self, diagnostic: DiagnosticsRecord) -> RelationalTrace:
        """Add a diagnostics record."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + (diagnostic,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RelationalTrace",
    "DiagnosticsRecord",
]