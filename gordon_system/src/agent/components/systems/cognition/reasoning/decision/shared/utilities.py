# Decision Utility Management - Phase 7.41
# =========================================

"""
Canonical Utility Management Contract.

Utility management evaluates:
    - expected utility
    - expected value
    - cost
    - benefit
    - reward
    - penalty

Utilities remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class UtilityModel:
    """A utility model for evaluating alternatives."""
    
    # Identity
    model_id: str                             # Unique identifier
    
    # Model specification
    model_type: str = "additive"              # additive, multiplicative, weighted
    weights: Dict[str, float] = field(default_factory=dict)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class UtilityDistribution:
    """Probability distribution over utilities."""
    
    # Identity
    distribution_id: str                      # Unique identifier
    
    # Distribution data
    utility_values: Tuple[float, ...] = ()
    probabilities: Tuple[float, ...] = ()     # Same length as utility_values
    
    @property
    def expected_value(self) -> float:
        """Calculate expected value."""
        if not self.utility_values or not self.probabilities:
            return 0.0
        return sum(u * p for u, p in zip(self.utility_values, self.probabilities))
    
    @property
    def variance(self) -> float:
        """Calculate variance."""
        expected = self.expected_value
        if not self.utility_values or not self.probabilities:
            return 0.0
        return sum(p * (u - expected) ** 2 for u, p in zip(self.utility_values, self.probabilities))


@dataclass(frozen=True)
class UtilityManagement:
    """
    Management of utility estimation for a decision.
    
    Evaluates:
        - expected utility
        - expected value
        - cost
        - benefit
        - reward
        - penalty
    
    Utilities remain explicit; never hide uncertainty.
    """
    
    # Identity
    management_id: str                        # Unique identifier
    
    # Decision context
    decision_set_id: str                      # Related decision set
    evaluated_option: str = "unknown"         # Option being evaluated
    
    # Utility components
    expected_utility: float = 0.0             # Expected utility value
    expected_cost: float = 0.0                # Expected cost
    expected_benefit: float = 0.0             # Expected benefit
    
    # Distribution (for uncertainty quantification)
    utility_distribution: Optional[UtilityDistribution] = None
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def net_utility(self) -> float:
        """Calculate net utility (benefit - cost)."""
        return self.expected_benefit - self.expected_cost
    
    def with_distribution(self, distribution: UtilityDistribution) -> UtilityManagement:
        """Attach a utility distribution and return new instance."""
        return dataclass_replace(
            self,
            utility_distribution=distribution,
        )
    
    @classmethod
    def create(
        cls,
        decision_set_id: str,
        evaluated_option: str = "unknown",
        expected_utility: float = 0.0,
        expected_cost: float = 0.0,
        expected_benefit: float = 0.0,
    ) -> UtilityManagement:
        """Create a new utility management instance."""
        return cls(
            management_id=f"utility_management:{uuid.uuid4().hex[:16]}",
            decision_set_id=decision_set_id,
            evaluated_option=evaluated_option,
            expected_utility=expected_utility,
            expected_cost=expected_cost,
            expected_benefit=expected_benefit,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "UtilityModel",
    "UtilityDistribution",
    "UtilityManagement",
]