# Gordon Executive Decision Commitment - Phase 4.4.10A
# =======================================================

"""
Decision Commitment System.

This module defines commitment tracking for Executive Decisions.
A commitment is the authoritative acceptance of a decision recommendation.


ARCHITECTURAL LAWS
==================

E-030: Commitments never execute behavior.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DecisionCommitment:
    """
    Record of an executive commitment for a Decision Recommendation.
    
    Runtime-neutral: Yes
    Executable: No
    
    Key properties:
        - decision_id: The decision being committed
        - authority_id: Who authorized the commitment
        - timestamp_utc: When the commitment was made
        
    Example:
        >>> commitment = DecisionCommitment(
        ...     decision_id="decision_abc123",
        ... )
    """
    
    decision_id: str = field(default="")
    """The decision being committed."""
    
    authority_id: str = field(default="")
    """ID of the authority that authorized this commitment."""
    
    timestamp_utc: float = 0.0
    """Timestamp when this commitment was made."""
    
    @property
    def is_commitment(self) -> bool:
        """Return True for all commitment records."""
        return True
    
    @classmethod
    def initial(cls, decision_id: str) -> "DecisionCommitment":
        """Create an initial commitment record."""
        return cls(decision_id=decision_id)