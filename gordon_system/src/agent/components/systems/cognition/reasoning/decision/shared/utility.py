# Decision Utility Estimation - Phase 7.19
# ========================================

"""
Canonical Decision Utility Estimation Contract.

Utility estimation evaluates expected benefit, cost, risk, and uncertainty.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class UtilityComponents:
    """
    Detailed utility components for a decision option.
    
    Components include:
        - Expected benefit
        - Expected cost
        - Risk
        - Uncertainty
        - Resource demand
        - Time estimate
        - Reversibility
    """
    
    # Identity
    utility_id: str                         # Unique identifier
    
    # Evaluated option
    evaluated_option: str                   # Option ID being estimated
    
    # Utility components
    expected_benefit: float = 0.0           # Expected positive outcomes
    expected_cost: float = 0.0              # Expected negative outcomes
    
    # Risk metrics
    risk_score: float = 0.0                 # Risk level (0-1)
    uncertainty: float = 0.0                # Uncertainty level (0-1)
    
    # Resource metrics
    resource_demand: str = "low"            # low, medium, high
    time_estimate_seconds: float = 0.0      # Estimated duration
    
    # Strategic factors
    reversibility: str = "reversible"       # irreversible, conditional, reversible
    opportunity_cost: float = 0.0           # Value of next best alternative
    
    @property
    def net_utility(self) -> float:
        """Calculate net utility (benefit - cost)."""
        return self.expected_benefit - self.expected_cost
    
    @classmethod
    def create(
        cls,
        evaluated_option: str,
        expected_benefit: float = 0.0,
        expected_cost: float = 0.0,
        risk_score: float = 0.0,
        uncertainty: float = 0.0,
    ) -> UtilityComponents:
        """Create new utility components."""
        return cls(
            utility_id=f"utility_components:{uuid.uuid4().hex[:16]}",
            evaluated_option=evaluated_option,
            expected_benefit=expected_benefit,
            expected_cost=expected_cost,
            risk_score=risk_score,
            uncertainty=uncertainty,
        )


@dataclass(frozen=True)
class UtilityEstimation:
    """
    Complete utility estimation for a decision.
    
    Utility estimates remain explicit; they never hide uncertainty.
    """
    
    # Identity
    estimation_id: str                      # Unique identifier
    
    # Evaluated option
    evaluated_option: str                   # Option ID being estimated
    
    # Utility components
    utility_components: Tuple[UtilityComponents, ...]
    
    # Aggregate score (weighted combination of components)
    aggregate_score: float = 0.0            # Overall utility score
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def component_count(self) -> int:
        """Count of utility components."""
        return len(self.utility_components)
    
    def get_component_by_name(self, name: str) -> Optional[UtilityComponents]:
        """Get a specific utility component by name."""
        for component in self.utility_components:
            if component.utility_id.endswith(name):
                return component
        return None
    
    @classmethod
    def create(
        cls,
        evaluated_option: str,
        components: List[UtilityComponents],
        aggregate_score: float = 0.0,
    ) -> UtilityEstimation:
        """Create a new utility estimation."""
        return cls(
            estimation_id=f"utility_estimation:{uuid.uuid4().hex[:16]}",
            evaluated_option=evaluated_option,
            utility_components=tuple(components),
            aggregate_score=aggregate_score,
        )


__all__ = [
    "UtilityComponents",
    "UtilityEstimation",
]