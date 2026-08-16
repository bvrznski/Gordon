# Salience Network Dynamic Update Request
# ========================================

"""
Canonical dynamic update request model (Phase 4.8.7).

A DynamicUpdateRequest represents a request for temporal evolution of Candidate
salience states without runtime scheduling or wall-clock access.

DYNAMICS REQUEST INVARIANTS:
    DYN-REQ-INV-001: Request is immutable (frozen dataclass)
    DYN-REQ-INV-002: Semantic delta is supplied externally (not computed internally)
    DYN-REQ-INV-003: No runtime scheduling or timers used
    DYN-REQ-INV-004: Policy is referenced, not executed
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class DynamicDeltaKind:
    """
    Semantic kind of temporal progression.
    
    DELTA Kinds:
        - CYCLE: One reasoning cycle
        - STEPS: Multiple reasoning cycles
        - EXTERNAL_DURATION: External semantic duration reference
        - SIMULATION_TICK: Simulation tick increment
        - EPISODE_TRANSITION: Episode transition marker
    """
    
    kind: str = field(default="unknown")
    """Delta kind identifier."""
    
    count: int = field(default=1)
    """Semantic time units passed."""
    
    @property
    def is_cycle(self) -> bool:
        """Check if delta represents a single reasoning cycle."""
        return self.kind == "cycle" and self.count == 1
    
    @property
    def is_steps(self) -> bool:
        """Check if delta represents multiple cycles/steps."""
        return self.kind == "steps"
    
    @property
    def is_semantic_duration(self) -> bool:
        """Check if delta represents external semantic duration."""
        return self.kind == "external_duration"


@dataclass(frozen=True)
class DynamicUpdateRequest:
    """
    Immutable request for temporal evolution of Candidate salience.
    
    A request contains:
        - Identity (for traceability)
        - Current Candidate States to evolve
        - Semantic delta (time progression)
        - Dynamic Policy reference
        - Previous adaptive state reference
        - Provenance tracking
    
    DYNAMICS REQUEST INVARIANTS:
        DYN-REQ-INV-001: Request is deeply frozen dataclass
        DYN-REQ-INV-002: Semantic delta supplied externally (not computed)
        DYN-REQ-INV-003: No runtime scheduling occurs
        DYN-REQ-INV-004: All Candidates must be validated
    """
    
    # Identity for this request (external supply)
    identity: str = field(default="")
    """Unique identifier for the update request."""
    
    # Candidate states to evolve
    candidate_states: Tuple[dict, ...] = field(default_factory=tuple)
    """
    Tuple of Candidate State dictionaries to evolve.
    
    Each dictionary contains:
        state_identity: Unique candidate identifier
        overall_level: Current salience level
        assessment: Assessment descriptor dictionary
        confidence: Confidence in assessment (0.0-1.0)
        evidence_ids: Evidence supporting this candidate
    """
    
    # Semantic temporal delta
    semantic_delta: DynamicDeltaKind = field(default_factory=DynamicDeltaKind)
    """Semantic time progression (NOT datetime.now!)."""
    
    # Policy reference for dynamics
    dynamic_policy: str = field(default="")
    """Reference to external dynamic policy configuration."""
    
    # Previous adaptive state (for continuity)
    previous_adaptive_state: Tuple[dict, ...] = field(default_factory=tuple)
    """
    Tuple of previous adaptive states.
    
    Each dictionary contains:
        candidate_id: Matching state_identity
        accumulation_level: Current accumulation level
        decay_state: Current decay descriptor
        habituation_level: Current habituation level
        sensitization_level: Current sensitization level
        fatigue_level: Current fatigue level
        recovery_state: Current recovery descriptor
        persistence_kind: Current persistence classification
        stability_status: Current stability status
    """
    
    # Provenance tracking
    provenance_source: str = field(default="")
    """Source that generated this request."""
    
    @property
    def candidate_count(self) -> int:
        """Return number of candidates in request."""
        return len(self.candidate_states)
    
    @property
    def has_candidates(self) -> bool:
        """Check if there are any candidates to evolve."""
        return self.candidate_count > 0
    
    def get_candidate_by_identity(self, identity: str) -> dict | None:
        """
        Retrieve candidate by state identity.
        
        Args:
            identity: State identity to search for
            
        Returns:
            Candidate dictionary or None if not found
        """
        for candidate in self.candidate_states:
            if candidate.get("state_identity") == identity:
                return candidate
        return None
    
    def get_previous_adaptive_by_candidate_id(self, candidate_id: str) -> dict | None:
        """
        Retrieve previous adaptive state by candidate ID.
        
        Args:
            candidate_id: Candidate identity to search for
            
        Returns:
            Adaptive state dictionary or None if not found
        """
        for prev_state in self.previous_adaptive_state:
            if prev_state.get("candidate_id") == candidate_id:
                return prev_state
        return None