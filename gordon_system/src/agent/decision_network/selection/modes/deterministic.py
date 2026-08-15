# Gordon Cognitive Architecture - Phase 4.5.7
# ===========================================
#
"""
Deterministic selection mode.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class DeterministicSelectionMethod:
    """
    A deterministic method for selecting a candidate from a frontier.
    
    DETERMINISTIC METHODS:
        • SOLE_FRONTIER_MEMBER: Select sole member if exactly one eligible candidate
        • LEXICOGRAPHIC_IDENTITY: Use canonical identity ordering (semantically neutral only)
        • PARETO_LEXICOGRAPHIC: Pareto with lexicographic tie-breaker
        • EXPLICIT_AUTHORITY_CHOICE: Apply authority's explicit choice
        • EXPLICIT_USER_CHOICE: Apply user's explicit choice
        • EXECUTIVE_DIRECTED: Apply executive network directive
        • REPLAYED_PRIOR_SELECTION: Replay prior selection from record
    
    IMPORTANT:
        • Deterministic methods must produce the same result for identical inputs
        • Deterministic ordering never infers substantive preference without evidence
        • Lexicographic ordering only used when all other criteria are equal
    """
    
    kind: str = "SOLE_FRONTIER_MEMBER"
    """Canonical deterministic method."""
    
    parameters: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Additional configuration for the method."""