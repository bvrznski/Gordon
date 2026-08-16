# Salience Network Competition State
# ==================================
#
# Canonical implementation of multiple candidate relationships (Phase 4.8.4).
#

"""
Competition state for multiple salient Candidates.

COMPETITION PRESERVES EXTERNAL AUTHORITY:
    - Winner selection is NOT done in State
    - Attention allocation is NOT done in State  
    - Only semantic relationships are represented
    
COMPETITION CATEGORIES:
    - UNRESOLVED: Multiple candidates competing, no winner determined
    - RESOLVED: One candidate dominates, others suppressed or subordinate
    - CONFLICTED: Mutually exclusive candidates with unresolved conflict
    - SUPPRESSED: Winner dominates, losers suppressed semantically
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class SalienceCandidateReference:
    """
    Canonical reference to a salient candidate in competition.
    
    Each reference preserves:
        - State identity for tracking
        - Subject reference for semantic identification
        - Level classification for comparison
        - Relationship descriptor
    
    COMPETITION INVARIANTS:
        - SALIENCE-COMPETITION-REF-INV-001: Unique state identities within set
        - SALIENCE-COMPETITION-REF-INV-002: No embedded implementation objects
    """
    
    state_identity: str = field(default="")
    """State identity of the candidate."""
    
    subject_id: str = field(default="")
    """Subject identity being evaluated."""
    
    level: str = field(default="unknown")
    """Salience level classification."""
    
    relationship: str = field(default="competing")
    """
    Semantic relationship to dominant:
        - competing: Normal competitor
        - suppressed: Suppressed by dominant
        - subordinate: Subordinate to dominant
        - dominant: The winning candidate
    """


@dataclass(frozen=True)
class SalienceCompetitionState:
    """
    Canonical composition of multiple candidate relationships.
    
    COMPETITION COMPOSITION:
        - candidates: Set of competing Candidates
        - dominant_candidate: State identity of dominant (if resolved)
        - status: Resolution status
    
    COMPETITION LAWS:
        - SALIENCE-COMPETITION-LAW-001: No winner selection in State
        - SALIENCE-COMPETITION-LAW-002: No attention allocation in State
        - SALIENCE-COMPETITION-LAW-003: Dominant must belong to candidates set
    
    COMPETITION STATUS:
        - UNRESOLVED: Multiple candidates, no determination made
        - RESOLVED: One winner identified
        - CONFLICTED: Mutually exclusive candidates with unresolved conflict
        - SUPPRESSED: Winner dominates semantically
    """
    
    candidates: Tuple[SalienceCandidateReference, ...] = field(default_factory=tuple)
    """Set of competing Candidates."""
    
    dominant_candidate: str | None = field(default=None)
    """State identity of dominant Candidate where applicable."""
    
    status: str = field(default="unresolved")
    """Resolution status of the competition."""
    
    basis: Tuple[str, ...] = field(default_factory=tuple)
    """
    Semantic basis for competition state:
        - Evidence supporting each candidate
        - Constraints limiting selection
        - External directives affecting outcome
    """