# Decision Commitment Management - Phase 7.41
# ============================================

"""
Canonical Commitment Management Contract.

Commitment management evaluates:
    - decision quality
    - decision confidence
    - reversibility
    - commitment cost
    - expected consequences
    - commitment stability

Commits remain explicit; never modify historical decisions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class CommitmentAnalysis:
    """Analysis of a single commitment."""
    
    # Identity
    commitment_id: str                        # Unique identifier
    
    # Decision details
    selected_decision: str                    # Alternative being committed to
    rejected_decisions: Tuple[str, ...] = ()  # Alternatives not chosen
    
    # Commitment properties
    confidence: float = 0.0                   # Confidence in the decision
    reversibility: bool = False               # Can it be reversed?
    
    # Expected outcomes
    expected_utility: float = 0.0             # Expected utility value
    expected_cost: float = 0.0                # Expected cost
    
    # Provenance
    analyzed_at_utc: float = field(default_factory=time.time)
    analyst_id: str = "default"


@dataclass(frozen=True)
class CommitmentManagement:
    """
    Management of commitment decisions.
    
    Evaluates:
        - decision quality
        - decision confidence
        - reversibility
        - commitment cost
        - expected consequences
        - commitment stability
    
    Commitments remain explicit; never overwrite historical decisions.
    """
    
    # Identity
    management_id: str                        # Unique identifier
    
    # Decision context
    decision_set_id: str                      # Related decision set
    evaluation_scope: str = "unknown"         # What is being committed?
    
    # Commitment analyses
    commitments: Tuple[CommitmentAnalysis, ...] = ()
    
    # Overall assessment
    overall_confidence: float = 0.0           # Aggregate confidence
    commitment_strength: float = 0.0          # How strongly to commit
    
    # Reversibility tracking
    reversible_commitments: Tuple[str, ...] = ()   # IDs of reversible commitments
    irreversible_commitments: Tuple[str, ...] = () # IDs of irreversible commitments
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def commitment_count(self) -> int:
        """Count of commitments."""
        return len(self.commitments)
    
    def get_commitment(self, decision_id: str) -> Optional[CommitmentAnalysis]:
        """Get commitment for a specific decision."""
        for commit in self.commitments:
            if commit.selected_decision == decision_id:
                return commit
        return None
    
    def with_commitment(self, analysis: CommitmentAnalysis) -> CommitmentManagement:
        """Add a commitment analysis and return new instance."""
        new_commitments = list(self.commitments)
        new_commitments.append(analysis)
        
        # Update reversibility tracking
        reversible_ids = [
            c.selected_decision 
            for c in new_commitments if c.reversibility
        ]
        irreversible_ids = [
            c.selected_decision 
            for c in new_commitments if not c.reversibility
        ]
        
        # Recalculate overall confidence
        avg_confidence = sum(c.confidence for c in new_commitments) / len(new_commitments)
        
        return dataclass_replace(
            self,
            commitments=tuple(new_commitments),
            overall_confidence=avg_confidence,
            reversible_commitments=tuple(reversible_ids),
            irreversible_commitments=tuple(irreversible_ids),
        )
    
    @classmethod
    def create(
        cls,
        decision_set_id: str,
        evaluation_scope: str = "unknown",
    ) -> CommitmentManagement:
        """Create a new commitment management instance."""
        return cls(
            management_id=f"commitment_management:{uuid.uuid4().hex[:16]}",
            decision_set_id=decision_set_id,
            evaluation_scope=evaluation_scope,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CommitmentAnalysis",
    "CommitmentManagement",
]