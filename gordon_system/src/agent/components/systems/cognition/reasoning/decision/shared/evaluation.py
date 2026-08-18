# Decision Option Evaluation - Phase 7.19
# =======================================

"""
Canonical Decision Option Evaluation Contract.

Option Evaluation represents the complete evaluation of options.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class UtilityEstimate:
    """
    Utility estimation for a single option.
    
    Utility estimates remain explicit; they never hide uncertainty.
    """
    
    # Identity
    estimate_id: str                        # Unique identifier
    
    # Evaluated option
    evaluated_option: str                   # Option ID being estimated
    
    # Utility components
    expected_benefit: float = 0.0           # Expected positive outcomes
    expected_cost: float = 0.0              # Expected negative outcomes
    risk_score: float = 0.0                 # Risk level (0-1)
    uncertainty: float = 0.0                # Uncertainty level (0-1)
    
    # Resource metrics
    resource_demand: str = "low"            # low, medium, high
    time_estimate_seconds: float = 0.0      # Estimated duration
    
    # Opportunity cost
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
    ) -> UtilityEstimate:
        """Create a new utility estimate."""
        return cls(
            estimate_id=f"utility_estimate:{uuid.uuid4().hex[:16]}",
            evaluated_option=evaluated_option,
            expected_benefit=expected_benefit,
            expected_cost=expected_cost,
            risk_score=risk_score,
            uncertainty=uncertainty,
        )


@dataclass(frozen=True)
class OptionEvaluation:
    """
    Complete evaluation of a set of options.
    
    Canonical pipeline:
        Option Generation → Constraint Analysis → 
        Utility Evaluation → Confidence Calibration → 
        Commitment Selection → Validation → Publication
    """
    
    # Identity
    evaluation_id: str                      # Unique identifier
    
    # Evaluated options
    evaluated_options: Tuple[UtilityEstimate, ...]
    
    # Evaluation strategy
    evaluation_strategy: str = "default"    # Strategy used (e.g., "exhaustive", "bounded")
    
    # Diagnostics
    duration_seconds: float = 0.0           # Total evaluation time
    options_evaluated_count: int = 0        # Number of options evaluated
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def option_count(self) -> int:
        """Count of evaluated options."""
        return len(self.evaluated_options)
    
    def get_estimate_for_option(self, option_id: str) -> Optional[UtilityEstimate]:
        """Get utility estimate for a specific option."""
        for estimate in self.evaluated_options:
            if estimate.evaluated_option == option_id:
                return estimate
        return None
    
    @classmethod
    def create(
        cls,
        estimates: List[UtilityEstimate],
        evaluation_strategy: str = "default",
        options_evaluated_count: Optional[int] = None,
    ) -> OptionEvaluation:
        """Create a new option evaluation."""
        return cls(
            evaluation_id=f"option_evaluation:{uuid.uuid4().hex[:16]}",
            evaluated_options=tuple(estimates),
            evaluation_strategy=evaluation_strategy,
            options_evaluated_count=options_evaluated_count or len(estimates),
        )


__all__ = [
    "UtilityEstimate",
    "OptionEvaluation",
]