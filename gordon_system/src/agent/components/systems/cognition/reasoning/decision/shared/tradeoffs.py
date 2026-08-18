# Decision Tradeoff Management - Phase 7.41
# ==========================================

"""
Canonical Tradeoff Management Contract.

Tradeoff management evaluates:
    - risk versus reward
    - short-term versus long-term
    - efficiency versus robustness
    - certainty versus exploration
    - resource consumption
    - opportunity cost

Tradeoffs remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class TradeoffAnalysis:
    """Analysis of a single tradeoff."""
    
    # Identity
    tradeoff_id: str                          # Unique identifier
    
    # Competing objectives
    objective_a: str                          # First objective (e.g., "efficiency")
    objective_b: str                          # Second objective (e.g., "robustness")
    
    # Tradeoff evaluation
    selected_balance: float = 0.5             # 0-1 scale (closer to A=0, B=1)
    confidence: float = 0.0                   # Confidence in tradeoff analysis
    
    # Metrics
    benefit_a: float = 0.0                    # Benefit of favoring A
    benefit_b: float = 0.0                    # Benefit of favoring B
    cost_a: float = 0.0                       # Cost of favoring A
    cost_b: float = 0.0                       # Cost of favoring B
    
    # Provenance
    analyzed_at_utc: float = field(default_factory=time.time)
    analyst_id: str = "default"


@dataclass(frozen=True)
class TradeoffManagement:
    """
    Management of tradeoff analysis for a decision.
    
    Evaluates:
        - risk versus reward
        - short-term versus long-term
        - efficiency versus robustness
        - certainty versus exploration
        - resource consumption
        - opportunity cost
    
    Tradeoffs remain explicit; never ignore dominant competing criteria.
    """
    
    # Identity
    management_id: str                        # Unique identifier
    
    # Decision context
    decision_set_id: str                      # Related decision set
    analysis_scope: str = "unknown"           # What is being analyzed?
    
    # Tradeoff analyses
    tradeoffs: Tuple[TradeoffAnalysis, ...] = ()
    
    # Overall assessment
    overall_balance: float = 0.5              # Aggregate balance across all tradeoffs
    
    # Dominant criteria (prioritized list)
    dominant_criteria: Tuple[str, ...] = ()   # Criteria with highest weight
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def tradeoff_count(self) -> int:
        """Count of tradeoff analyses."""
        return len(self.tradeoffs)
    
    def get_tradeoff(self, objective_a: str) -> Optional[TradeoffAnalysis]:
        """Get tradeoff analysis for a specific pair."""
        for tradeoff in self.tradeoffs:
            if tradeoff.objective_a == objective_a:
                return tradeoff
        return None
    
    def with_tradeoff(self, analysis: TradeoffAnalysis) -> TradeoffManagement:
        """Add a tradeoff analysis and return new instance."""
        new_tradeoffs = list(self.tradeoffs)
        new_tradeoffs.append(analysis)
        
        # Recalculate overall balance
        if len(new_tradeoffs) > 0:
            avg_balance = sum(t.selected_balance for t in new_tradeoffs) / len(new_tradeoffs)
        else:
            avg_balance = self.overall_balance
        
        return dataclass_replace(
            self,
            tradeoffs=tuple(new_tradeoffs),
            overall_balance=avg_balance,
        )
    
    @classmethod
    def create(
        cls,
        decision_set_id: str,
        analysis_scope: str = "unknown",
    ) -> TradeoffManagement:
        """Create a new tradeoff management instance."""
        return cls(
            management_id=f"tradeoff_management:{uuid.uuid4().hex[:16]}",
            decision_set_id=decision_set_id,
            analysis_scope=analysis_scope,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TradeoffAnalysis",
    "TradeoffManagement",
]