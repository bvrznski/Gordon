# Salience Network Temporal Trace Model
# =====================================

"""
Canonical temporal trace model (Phase 4.8.7).

Trace records the structural rationale for temporal evolution operations.

TRACE INVARIANTS:
    TRACE-INV-001: All fields are immutable
    TRACE-INV-002: Contains only structural rationale (no reasoning chain)
    TRACE-INV-003: State is immutable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class TraceCode:
    """
    Codes for trace entries.
    
    TRACE CODES:
        - TEMPORAL_UPDATE: General temporal update occurred
        - ACCUMULATION: Accumulation operation recorded
        - DECAY: Decay operation recorded
        - SATURATION: Saturation threshold reached
        - HABITUATION: Habituation operation recorded
        - SENSITIZATION: Sensitization operation recorded  
        - FATIGUE: Fatigue accumulation recorded
        - RECOVERY: Recovery progress recorded
        - CONTEXT_SHIFT: Context adaptation occurred
        - PERSISTENCE_CHANGE: Persistence classification changed
        - STABILITY_CHANGE: Stability status changed
    """
    
    code: str = field(default="unknown")
    """Trace code identifier."""
    
    candidate_id: str = field(default="")
    """Candidate identity where event occurred."""
    
    @property
    def is_accumulation(self) -> bool:
        """Check if trace is accumulation-related."""
        return self.code == "accumulation"
    
    @property
    def is_decay(self) -> bool:
        """Check if trace is decay-related."""
        return self.code == "decay"


@dataclass(frozen=True)
class TemporalTrace:
    """
    Structural trace of temporal evolution.
    
    A trace contains:
        - Request identity (for matching requests to results)
        - Semantic delta applied
        - All operations performed
        - Validation findings
    
    TRACE INVARIANTS:
        TRACE-INV-001: Trace is deeply frozen dataclass
        TRACE-INV-002: Contains only structural rationale
        TRACE-INV-003: No reasoning chain in trace
    """
    
    # Request matching
    request_identity: str = field(default="")
    """Identity of the source update request."""
    
    # Semantic delta applied
    semantic_delta_applied: int = field(default=0)
    """Total semantic delta units processed."""
    
    # Trace entries (operations performed)
    trace_entries: Tuple[dict, ...] = field(default_factory=tuple)
    """
    List of trace entry dictionaries.
    
    Each entry contains:
        timestamp_delta: Delta at which operation occurred
        code: TraceCode.code value
        candidate_id: Candidate identity affected
        details: Operation-specific details
    """
    
    # Validation findings
    validation_status: str = field(default="unknown")
    """Semantic validation status."""
    
    validation_findings: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of validation findings."""
    
    @property
    def entry_count(self) -> int:
        """Return number of trace entries."""
        return len(self.trace_entries)
    
    @property
    def has_trace_entries(self) -> bool:
        """Check if any trace entries exist."""
        return self.entry_count > 0
    
    def get_entries_by_code(self, code: str) -> tuple[dict, ...]:
        """
        Retrieve trace entries by code.
        
        Args:
            code: Trace code to filter for
            
        Returns:
            Tuple of matching entries (possibly empty)
        """
        return tuple(e for e in self.trace_entries if e.get("code") == code)
    
    def get_candidates_with_accumulation(self) -> tuple[str, ...]:
        """Get list of candidates with accumulation trace entries."""
        entries = self.get_entries_by_code("accumulation")
        return tuple(e.get("candidate_id", "") for e in entries)
    
    def get_candidates_with_decay(self) -> tuple[str, ...]:
        """Get list of candidates with decay trace entries."""
        entries = self.get_entries_by_code("decay")
        return tuple(e.get("candidate_id", "") for e in entries)