# Salience Network Competition Request
# =====================================

"""
Canonical competition request model (Phase 4.8.6).

A CompetitionRequest contains multiple validated Candidate States for
comparison and ranking.

COMPETITION INVARIANTS:
    COMPETITION-REQUEST-INV-001: Contains only validated Candidates
    COMPETITION-REQUEST-INV-002: All Candidates are immutable
    COMPETITION-REQUEST-INV-003: Request is deeply frozen dataclass
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class CompetitionRequest:
    """
    Immutable competition request.
    
    Contains the candidates to be compared and ranked by the competition layer.
    All Candidates must have been validated through Phase 4.8.5 evaluation.
    
    COMPETITION REQUEST INVARIANTS:
        COMPETITION-REQUEST-INV-001: At least one Candidate required
        COMPETITION-REQUEST-INV-002: Unique identities within candidates
        COMPETITION-REQUEST-INV-003: Immutable Candidates only
    """
    
    # Identity for this request (external supply)
    identity: str = field(default="")
    """Unique identifier for the competition request."""
    
    # Candidate states to compare
    candidate_states: Tuple[dict, ...] = field(default_factory=tuple)
    """
    Tuple of validated Candidate State dictionaries.
    
    Each dictionary contains:
        state_identity: Unique candidate identifier
        overall_level: Canonical salience level
        assessment: Assessment descriptor dictionary
        confidence: Confidence in assessment (0.0-1.0)
        uncertainty: Semantic uncertainty description
        evidence_ids: Evidence supporting this candidate
    """
    
    # Policy reference for competition
    competition_policy: str = field(default="")
    """Reference to external competition policy configuration."""
    
    # Optional prior competition state for stability estimation
    prior_competition_state: str | None = field(default=None)
    """Identity of previous competition result (for stability estimation)."""
    
    # Provenance tracking
    provenance_source: str = field(default="")
    """Source that generated this request."""
    
    @property
    def candidate_count(self) -> int:
        """Return number of candidates in request."""
        return len(self.candidate_states)
    
    @property
    def has_multiple_candidates(self) -> bool:
        """Check if there are multiple candidates for competition."""
        return self.candidate_count > 1
    
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