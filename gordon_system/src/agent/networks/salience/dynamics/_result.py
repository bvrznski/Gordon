# Salience Network Dynamic Update Result
# =======================================

"""
Canonical dynamic update result model (Phase 4.8.7).

A DynamicUpdateResult represents the immutable outcome of temporal evolution
applied to Candidate salience states.

DYNAMICS RESULT INVARIANTS:
    DYN-RES-INV-001: Result is immutable (frozen dataclass)
    DYN-RES-INV-002: Contains updated Candidates
    DYN-RES-INV-003: Contains adaptive findings and trace
    DYN-RES-INV-004: No in-place mutation occurs
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class DynamicFindingKind:
    """
    Kinds of dynamic findings recorded during evolution.
    
    FINDING KINDS:
        - ACCUMULATED: Accumulation increased salience
        - DECAYED: Decay reduced salience  
        - HABITUATED: Habituation reduced response
        - SENSITIZED: Sensitization increased response
        - FATIGUED: Fatigue reduced contribution
        - RECOVERED: Recovery restored responsiveness
        - CONTEXT_SHIFT: Context adaptation occurred
        - RESET: State was reset to baseline
        - SATURATED: Accumulation reached saturation
    """
    
    kind: str = field(default="unknown")
    """Finding kind identifier."""
    
    candidate_id: str = field(default="")
    """Candidate identity where finding occurred."""
    
    @property
    def is_accumulated(self) -> bool:
        """Check if finding represents accumulation."""
        return self.kind == "accumulated"
    
    @property
    def is_decayed(self) -> bool:
        """Check if finding represents decay."""
        return self.kind == "decayed"


@dataclass(frozen=True)
class DynamicStatus:
    """
    Status of a dynamic update operation.
    
    STATUS KINDS:
        - SUCCESS: Update completed successfully
        - PARTIAL: Some candidates updated, others unchanged
        - FAILED: Update failed for all candidates
        - INVALID_REQUEST: Request validation failed
        - NO_CHANGE: No evolution needed (delta = 0)
    """
    
    kind: str = field(default="unknown")
    """Status kind identifier."""
    
    message: str = field(default="")
    """Human-readable status message."""
    
    @property
    def is_success(self) -> bool:
        """Check if update was successful."""
        return self.kind == "success"
    
    @property
    def is_partial(self) -> bool:
        """Check if update was partial."""
        return self.kind == "partial"


@dataclass(frozen=True)
class DynamicUpdateResult:
    """
    Immutable result of temporal evolution.
    
    A result contains:
        - Updated Candidate States (with evolved adaptive descriptors)
        - Adaptive findings (what changed and why)
        - Validation status
        - Temporal trace (structural rationale for changes)
    
    DYNAMICS RESULT INVARIANTS:
        DYN-RES-INV-001: Result is deeply frozen dataclass
        DYN-RES-INV-002: Contains updated Candidates
        DYN-RES-INV-003: Contains findings and trace
        DYN-RES-INV-004: No in-place mutation occurs
    """
    
    # Identity matching the request
    identity: str = field(default="")
    """Identity matching the source request (for traceability)."""
    
    # Updated candidate states
    updated_candidates: Tuple[dict, ...] = field(default_factory=tuple)
    """
    Tuple of updated Candidate State dictionaries.
    
    Each dictionary contains original fields plus:
        adaptive_state: Dictionary with current adaptive descriptors
        updated_at_delta: Delta when this update occurred
    """
    
    # Adaptive findings (what changed and why)
    findings: Tuple[DynamicFindingKind, ...] = field(default_factory=tuple)
    """Findings describing what dynamic operations occurred."""
    
    # Validation status
    validation_status: str = field(default="unknown")
    """
    Semantic validation status:
        - valid: All Candidates validated successfully
        - valid_with_warnings: Valid but with minor issues
        - invalid: Some Candidates failed validation
    """
    
    validation_findings: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of validation findings."""
    
    # Temporal trace (structural rationale)
    temporal_trace: str | None = field(default=None)
    """Trace reference or identifier for this update."""
    
    # Status summary
    status: DynamicStatus = field(default_factory=DynamicStatus)
    """Overall update operation status."""
    
    @property
    def candidate_count(self) -> int:
        """Return number of updated candidates."""
        return len(self.updated_candidates)
    
    @property
    def has_findings(self) -> bool:
        """Check if any dynamic findings were recorded."""
        return len(self.findings) > 0
    
    @property
    def is_success(self) -> bool:
        """Check if update completed successfully."""
        return self.status.is_success
    
    def get_candidate_by_identity(self, identity: str) -> dict | None:
        """
        Retrieve updated candidate by state identity.
        
        Args:
            identity: State identity to search for
            
        Returns:
            Updated candidate dictionary or None if not found
        """
        for candidate in self.updated_candidates:
            if candidate.get("state_identity") == identity:
                return candidate
        return None
    
    def get_findings_by_kind(self, kind: str) -> tuple[DynamicFindingKind, ...]:
        """
        Retrieve findings of a specific kind.
        
        Args:
            kind: Finding kind to filter for
            
        Returns:
            Tuple of matching findings (possibly empty)
        """
        return tuple(f for f in self.findings if f.kind == kind)