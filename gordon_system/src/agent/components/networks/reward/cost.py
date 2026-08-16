# Reward Network - Cost Estimator
# ================================

"""
Cost estimator for reward evaluation.

Costs contribute negatively to reward estimates. Each cost source is explicitly
represented with its contributing evidence and source-specific estimation.

COST LAWS:
    COST-LAW-001: Every Cost source remains explicit.
    COST-LAW-002: Cost remains decomposed.
    COST-LAW-003: Time Cost remains independent.
    COST-LAW-004: Compute Cost remains independent.
    COST-LAW-005: Energy Cost remains independent.
    COST-LAW-006: Opportunity Cost remains independent.
    COST-LAW-007: Risk Cost remains independent.
    COST-LAW-008: Attention Cost remains independent.
    COST-LAW-009: Costs preserve provenance.
    COST-LAW-010: Cost estimation remains deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class TimeCostEstimate:
    """Cost estimate from time expenditure."""
    
    time_amount: float
    """Amount of time spent (in canonical units)."""
    
    estimated_cost: float
    """Estimated cost value from time expenditure."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None


@dataclass(frozen=True)
class ComputeCostEstimate:
    """Cost estimate from compute resource expenditure."""
    
    compute_amount: float
    """Amount of compute used (in canonical units)."""
    
    estimated_cost: float
    """Estimated cost value from compute usage."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None


@dataclass(frozen=True)
class EnergyCostEstimate:
    """Cost estimate from energy expenditure."""
    
    energy_amount: float
    """Amount of energy used (in canonical units)."""
    
    estimated_cost: float
    """Estimated cost value from energy usage."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None


@dataclass(frozen=True)
class OpportunityCostEstimate:
    """Cost estimate from opportunity loss."""
    
    missed_opportunity: str
    """What was not done due to this action."""
    
    estimated_cost: float
    """Estimated cost value from the missed opportunity."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None


@dataclass(frozen=True)
class RiskCostEstimate:
    """Cost estimate from risk incurred."""
    
    risk_increase: float
    """Amount of risk increased (0.0 to 1.0)."""
    
    estimated_cost: float
    """Estimated cost value from risk increase."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None


@dataclass(frozen=True)
class AttentionCostEstimate:
    """Cost estimate from attention allocation."""
    
    attention_duration: float
    """Amount of attention allocated (in canonical units)."""
    
    estimated_cost: float
    """Estimated cost value from attention usage."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None


# =============================================================================
# AGGREGATED COST ESTIMATE
# =============================================================================

@dataclass(frozen=True)
class CostEstimate:
    """
    Complete cost assessment for a reward evaluation.
    
    Aggregates all cost sources into a single estimate while preserving
    the decomposition of individual contributions.
    
    PROPERTIES:
        • total_cost: Sum of all cost estimates
        • time_costs: Costs from time expenditure
        • compute_costs: Costs from compute usage
        • energy_costs: Costs from energy usage
        • opportunity_costs: Costs from missed opportunities
        • risk_costs: Costs from risk increase
        • attention_costs: Costs from attention allocation
        
    NOT RESPONSIBLE FOR:
        • Making executive decisions based on costs
        • Modifying outcomes or beliefs
        • Updating reward policies
    """
    
    # Aggregated total
    total_cost: float
    """Sum of all cost estimates."""
    
    # Decomposed contributions (always preserved)
    time_costs: Tuple[TimeCostEstimate, ...] = field(default_factory=tuple)
    """Costs from time expenditure."""
    
    compute_costs: Tuple[ComputeCostEstimate, ...] = field(default_factory=tuple)
    """Costs from compute resource usage."""
    
    energy_costs: Tuple[EnergyCostEstimate, ...] = field(default_factory=tuple)
    """Costs from energy resource usage."""
    
    opportunity_costs: Tuple[OpportunityCostEstimate, ...] = field(default_factory=tuple)
    """Costs from missed opportunities."""
    
    risk_costs: Tuple[RiskCostEstimate, ...] = field(default_factory=tuple)
    """Costs from risk increase."""
    
    attention_costs: Tuple[AttentionCostEstimate, ...] = field(default_factory=tuple)
    """Costs from attention allocation."""
    
    # Metadata
    provenance: Optional[str] = None
    """Provenance reference for this aggregation method."""
    
    @property
    def has_contributions(self) -> bool:
        """Check if any cost contributions were estimated."""
        return (
            len(self.time_costs) > 0 or
            len(self.compute_costs) > 0 or
            len(self.energy_costs) > 0 or
            len(self.opportunity_costs) > 0 or
            len(self.risk_costs) > 0 or
            len(self.attention_costs) > 0
        )