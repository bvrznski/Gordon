# Gordon Executive Decision Recommendation - Phase 4.4.10A
# ==========================================================

"""
Decision Recommendation System.

This module defines recommendation tracking for Executive Decisions.
Recommendations are evaluated proposals presented for executive commitment.


ARCHITECTURAL LAWS
==================

E-029: Recommendations never possess authority.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DecisionRecommendation:
    """
    Record of a decision recommendation submitted for executive approval.
    
    Runtime-neutral: Yes
    Executable: No
    
    Key properties:
        - decision_id: The decision being recommended
        - recommender_id: Who made the recommendation
        - timestamp_utc: When the recommendation was made
        
    Example:
        >>> recommendation = DecisionRecommendation(
        ...     decision_id="decision_abc123",
        ... )
    """
    
    decision_id: str = field(default="")
    """The decision being recommended."""
    
    recommender_id: str = field(default="")
    """ID of the entity that made this recommendation."""
    
    timestamp_utc: float = 0.0
    """Timestamp when this recommendation was made."""
    
    @property
    def is_recommendation(self) -> bool:
        """Return True for all recommendation records."""
        return True
    
    @classmethod
    def initial(cls, decision_id: str) -> "DecisionRecommendation":
        """Create an initial recommendation record."""
        return cls(decision_id=decision_id)