# Gordon Executive Decision Justification - Phase 4.4.10A
# =========================================================

"""
Decision Justification System.

This module defines justification tracking for Executive Decisions.
Justifications explain why the Executive Network accepted a commitment.


ARCHITECTURAL LAWS
==================

E-022: Justification shall describe semantic rationale, never implementation details.
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class DecisionJustification:
    """
    Record of why an Executive Decision was accepted.
    
    Runtime-neutral: Yes
    Executable: No
    
    Key properties:
        - decision_id: The decision being justified
        - rationale: The semantic reason for the commitment
        - supporting_goals: Goals this supports
        - accepted_risks: Risks that were acknowledged
        
    Example:
        >>> justification = DecisionJustification(
        ...     decision_id="decision_abc123",
        ... )
    """
    
    decision_id: str = field(default="")
    """The decision being justified."""
    
    rationale: str = field(default="")
    """The semantic reason for this commitment."""
    
    supporting_goals: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of goals this supports."""
    
    accepted_risks: Tuple[str, ...] = field(default_factory=tuple)
    """Risks that were acknowledged during acceptance."""
    
    @property
    def is_justification(self) -> bool:
        """Return True for all justification records."""
        return True
    
    @classmethod
    def initial(cls, decision_id: str, rationale: str) -> "DecisionJustification":
        """Create an initial justification record."""
        return cls(decision_id=decision_id, rationale=rationale)