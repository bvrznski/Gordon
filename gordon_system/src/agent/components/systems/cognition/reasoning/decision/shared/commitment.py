# Decision Commitment - Phase 7.19
# ===============================

"""
Canonical Decision Commitment Contract.

Commitment defines the selected option with rationale and confidence.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DecisionCommitment:
    """
    A decision commitment to a specific option.
    
    Commitment includes:
        - Selected option
        - Commitment rationale
        - Confidence level
        - Revision conditions
    """
    
    # Identity
    commitment_id: str                      # Unique identifier
    
    # Committed option
    committed_option: str                   # Option ID being committed
    
    # Commitment strength (0-1)
    commitment_strength: float = 0.5        # How strongly committed?
    
    # Revision conditions
    revision_conditions: Tuple[str, ...] = ()  # When to reconsider?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_firm_commitment(self) -> bool:
        """Check if commitment is firm (high strength)."""
        return self.commitment_strength >= 0.8
    
    @property
    def is_tentative_commitment(self) -> bool:
        """Check if commitment is tentative."""
        return 0.5 <= self.commitment_strength < 0.8
    
    @classmethod
    def create(
        cls,
        committed_option: str,
        commitment_strength: float = 0.5,
        revision_conditions: Optional[List[str]] = None,
    ) -> DecisionCommitment:
        """Create a new commitment."""
        return cls(
            commitment_id=f"decision_commitment:{uuid.uuid4().hex[:16]}",
            committed_option=committed_option,
            commitment_strength=max(0.0, min(1.0, commitment_strength)),
            revision_conditions=tuple(revision_conditions or []),
        )
    
    def strengthen(self, new_strength: float) -> DecisionCommitment:
        """Return a copy with increased commitment strength."""
        return dataclass_replace(
            self,
            commitment_strength=max(self.commitment_strength, new_strength),
        )
    
    def weaken(self, new_strength: float) -> DecisionCommitment:
        """Return a copy with decreased commitment strength."""
        return dataclass_replace(
            self,
            commitment_strength=min(self.commitment_strength, new_strength),
        )


@dataclass(frozen=True)
class CommitmentFormation:
    """
    Formation of a decision commitment.
    
    Commitment formation evaluates:
        - Decision readiness
        - Minimum confidence threshold
        - Policy compliance
        - Resource feasibility
    """
    
    # Identity
    formation_id: str                       # Unique identifier
    
    # Selected option
    selected_option: str                    # Option that was committed
    
    # Formation policy (what thresholds were used?)
    commitment_policy: str = "default"      # e.g., "conservative", "balanced", "aggressive"
    
    # Commitment strength achieved
    commitment_strength_achieved: float = 0.0
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        selected_option: str,
        commitment_policy: str = "default",
        commitment_strength_achieved: float = 0.0,
    ) -> CommitmentFormation:
        """Create a new commitment formation."""
        return cls(
            formation_id=f"commitment_formation:{uuid.uuid4().hex[:16]}",
            selected_option=selected_option,
            commitment_policy=commitment_policy,
            commitment_strength_achieved=commitment_strength_achieved,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DecisionCommitment",
    "CommitmentFormation",
]