# Reward Network - Benefit Estimator
# ====================================

"""
Benefit estimator for reward evaluation.

Benefits contribute positively to reward estimates. Each benefit is explicitly
represented with its contributing evidence and source-specific estimation.

BENEFIT LAWS:
    BENEFIT-LAW-001: Benefit remains explicitly represented.
    BENEFIT-LAW-002: Benefit remains distinct from Reward.
    BENEFIT-LAW-003: Benefit remains distinct from Goal Progress.
    BENEFIT-LAW-004: Benefit preserves contributing evidence.
    BENEFIT-LAW-005: Benefit estimates preserve provenance.
    BENEFIT-LAW-006: Benefit estimates remain immutable.
    BENEFIT-LAW-007: Benefit estimation remains deterministic.
    BENEFIT-LAW-008: Benefit estimation shall never infer executive policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class GoalBenefitEstimate:
    """
    Benefit estimate from goal progress.
    
    Estimates how much a goal achievement contributes to reward.
    """
    
    goal_id: str
    """ID of the goal that was advanced."""
    
    progress_amount: float
    """Amount of goal progress (0.0 to 1.0)."""
    
    estimated_benefit: float
    """Estimated benefit value from this progress."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None
    """Provenance reference for this estimation method."""


@dataclass(frozen=True)
class KnowledgeBenefitEstimate:
    """
    Benefit estimate from knowledge acquisition.
    
    Estimates benefit from learning new information or understanding.
    """
    
    knowledge_topic: str
    """Topic area of newly acquired knowledge."""
    
    knowledge_depth: float
    """Depth of understanding achieved (0.0 to 1.0)."""
    
    estimated_benefit: float
    """Estimated benefit value from this knowledge."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None
    """Provenance reference for this estimation method."""


@dataclass(frozen=True)
class EfficiencyBenefitEstimate:
    """
    Benefit estimate from resource efficiency.
    
    Estimates benefit from reduced resource expenditure.
    """
    
    resource_type: str  # ResourceKind.*
    """Type of resource (time, compute, energy, etc.)."""
    
    saved_amount: float
    """Amount of resource saved."""
    
    estimated_benefit: float
    """Estimated benefit value from efficiency gain."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None
    """Provenance reference for this estimation method."""


@dataclass(frozen=True)
class ResourceBenefitEstimate:
    """
    Benefit estimate from resource acquisition.
    
    Estimates benefit from gaining new resources (material, informational).
    """
    
    resource_type: str  # ResourceKind.*
    """Type of resource acquired."""
    
    resource_amount: float
    """Amount of resource acquired."""
    
    estimated_benefit: float
    """Estimated benefit value from resource gain."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None
    """Provenance reference for this estimation method."""


@dataclass(frozen=True)
class StabilityBenefitEstimate:
    """
    Benefit estimate from system stability.
    
    Estimates benefit from maintaining or improving system stability.
    """
    
    stability_change: str  # StabilityChangeKind.*
    """Type of stability change."""
    
    estimated_benefit: float
    """Estimated benefit value from stability improvement."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None
    """Provenance reference for this estimation method."""


@dataclass(frozen=True)
class LearningOpportunityEstimate:
    """
    Benefit estimate from learning opportunities.
    
    Estimates benefit from exposure to new learning opportunities.
    """
    
    opportunity_type: str  # OpportunityKind.*
    """Type of learning opportunity."""
    
    estimated_benefit: float
    """Estimated benefit value from the opportunity."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this estimate."""
    
    provenance: Optional[str] = None
    """Provenance reference for this estimation method."""


# =============================================================================
# AGGREGATED BENEFIT ESTIMATE
# =============================================================================

@dataclass(frozen=True)
class BenefitEstimate:
    """
    Complete benefit assessment for a reward evaluation.
    
    Aggregates all benefit sources into a single estimate while preserving
    the decomposition of individual contributions.
    
    PROPERTIES:
        • total_benefit: Sum of all benefit estimates
        • goal_benefits: Benefits from goal progress
        • knowledge_benefits: Benefits from learning
        • efficiency_benefits: Benefits from resource efficiency  
        • resource_benefits: Benefits from resource acquisition
        • stability_benefits: Benefits from system stability
        • opportunity_benefits: Benefits from learning opportunities
        
    NOT RESPONSIBLE FOR:
        • Making executive decisions based on benefits
        • Modifying outcomes or beliefs
        • Updating reward policies
    """
    
    # Aggregated total
    total_benefit: float
    """Sum of all benefit estimates."""
    
    # Decomposed contributions (always preserved)
    goal_benefits: Tuple[GoalBenefitEstimate, ...] = field(default_factory=tuple)
    """Benefits from goal progress."""
    
    knowledge_benefits: Tuple[KnowledgeBenefitEstimate, ...] = field(default_factory=tuple)
    """Benefits from learning and knowledge acquisition."""
    
    efficiency_benefits: Tuple[EfficiencyBenefitEstimate, ...] = field(default_factory=tuple)
    """Benefits from resource efficiency gains."""
    
    resource_benefits: Tuple[ResourceBenefitEstimate, ...] = field(default_factory=tuple)
    """Benefits from acquiring new resources."""
    
    stability_benefits: Tuple[StabilityBenefitEstimate, ...] = field(default_factory=tuple)
    """Benefits from system stability improvements."""
    
    opportunity_benefits: Tuple[LearningOpportunityEstimate, ...] = field(default_factory=tuple)
    """Benefits from learning opportunities."""
    
    # Metadata
    provenance: Optional[str] = None
    """Provenance reference for this aggregation method."""
    
    @property
    def has_contributions(self) -> bool:
        """Check if any benefit contributions were estimated."""
        return (
            len(self.goal_benefits) > 0 or
            len(self.knowledge_benefits) > 0 or
            len(self.efficiency_benefits) > 0 or
            len(self.resource_benefits) > 0 or
            len(self.stability_benefits) > 0 or
            len(self.opportunity_benefits) > 0
        )