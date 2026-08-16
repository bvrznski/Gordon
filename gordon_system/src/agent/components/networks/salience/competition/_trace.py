# Salience Network Competition Trace
# ====================================

"""
Canonical trace model for competition operations (Phase 4.8.6).

Trace preserves structural rationale for all competition decisions without
runtime stack traces or implementation details.

TRACE INVARIANTS:
    COMPETITION-TRACE-INV-001: Trace records only semantic rationale
    COMPETITION-TRACE-INV-002: No runtime dependencies in trace
    COMPETITION-TRACE-INV-003: Complete traceability for each decision
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class CompetitionTraceEntry:
    """
    Single trace entry for competition operation.
    
    Each entry records one atomic operation with its semantic rationale.
    """
    
    # Operation type (from TraceCode enum)
    code: str = field(default="")
    """Trace code identifying operation type."""
    
    # Operands involved
    operands: Tuple[str, ...] = field(default_factory=tuple)
    """Candidate identities affected by this operation."""
    
    # Result
    result: str = field(default="")
    """Semantic result of the operation."""
    
    # Rationale
    rationale: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic justification for the decision."""
    
    # Confidence and uncertainty
    confidence: float = 0.5
    """Confidence in the traced decision."""
    
    uncertainty_basis: str = field(default="")
    """Semantic basis for any uncertainty."""


@dataclass(frozen=True)
class CompetitionTrace:
    """
    Complete trace of competition operations.
    
    Trace preserves all structural rationale for competition decisions.
    """
    
    # Entries in chronological order
    entries: Tuple[CompetitionTraceEntry, ...] = field(default_factory=tuple)
    """All trace entries in execution order."""
    
    @property
    def entry_count(self) -> int:
        """Return number of trace entries."""
        return len(self.entries)
    
    def get_entries_by_code(self, code: str) -> Tuple[CompetitionTraceEntry, ...]:
        """
        Get all entries matching a specific trace code.
        
        Args:
            code: Trace code to filter by
            
        Returns:
            Tuple of matching trace entries
        """
        return tuple(e for e in self.entries if e.code == code)