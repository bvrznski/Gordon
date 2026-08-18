# Strategic Opportunity Contract - Phase 7.37 Part 2
# ==================================================

"""
Opportunity Management for Strategic Reasoning.

This module implements the canonical opportunity contracts specified in Phase 7.37 Part 2:

- OpportunityManagement: Evaluates future opportunities, strategic timing, expected value
- OpportunityIdentity: Unique identifier for opportunity tracking
- OpportunityModel: Formal representation of an opportunity
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class OpportunityType(Enum):
    """Types of strategic opportunities."""
    
    MARKET_EXPANSION = "market_expansion"
    TECHNOLOGY_ADVANCEMENT = "technology_advancement"
    PARTNERSHIP = "partnership"
    ACQUISITION = "acquisition"
    PRODUCT_DEVELOPMENT = "product_development"
    REGIONAL_EXPANSION = "regional_expansion"
    REGULATORY_CHANGE = "regulatory_change"


@dataclass(frozen=True)
class OpportunityIdentity:
    """
    Unique identifier for an opportunity assessment.
    
    LAW: OPPORTUNITY-LAW-001 - Every Opportunity Assessment shall possess one explicit identity.
    """
    
    opportunity_id: str          # UUID4 string
    semantic_identity: str       # Stable semantic reference across runs
    version: int                 # Version number for evolution tracking


@dataclass(frozen=True)
class OpportunityAssessment:
    """
    Individual assessment of an opportunity factor.
    
    LAW: OPPORTUNITY-LAW-002 - Opportunity assumptions shall remain explicit.
    """
    
    assessment_id: str
    factor_name: str             # e.g., "market_size", "competitor_response"
    score: float                 # 0.0 to 1.0
    confidence: float            # 0.0 to 1.0 (uncertainty estimate)
    evidence: Tuple[str, ...]    # Supporting evidence references


@dataclass(frozen=True)
class OpportunityConstraint:
    """Constraints that bound opportunity realization."""
    
    constraint_id: str
    type: str                    # e.g., "timeline", "resource", "legal"
    description: str
    hard: bool                   # Hard constraints cannot be violated


@dataclass(frozen=True)
class OpportunityRisk:
    """
    Risk associated with an opportunity.
    
    LAW: OPPORTUNITY-LAW-003 - Opportunity uncertainty shall remain explicit.
    """
    
    risk_id: str
    description: str
    probability: float           # 0.0 to 1.0
    impact: float                # 0.0 to 1.0 (negative impact magnitude)
    mitigation: Tuple[str, ...]  # Mitigation strategies


@dataclass(frozen=True)
class OpportunityAnalysis:
    """
    Analysis result for a single opportunity.
    
    LAW: OPPORTUNITY-LAW-004 - Opportunity provenance shall remain complete.
    """
    
    analysis_id: str
    opportunity_identity: OpportunityIdentity
    expected_value: float        # Expected value of pursuing this opportunity
    timing_score: float          # How well-timed is this opportunity?
    competition_score: float     # Competitive advantage assessment
    required_investment: float   # Resources needed to pursue
    quality_rating: str          # "excellent", "good", "fair", "poor"


@dataclass(frozen=True)
class OpportunityEvolution:
    """
    Records evolution of opportunity assessment over time.
    
    LAW: OPPORTUNITY-LAW-005 - Opportunity revisions shall preserve history.
    """
    
    evolution_id: str
    opportunity_identity: OpportunityIdentity
    timestamp_utc: float
    change_type: str             # "revision", "update", "refinement"
    previous_state_hash: str     # Hash of previous state for verification
    change_description: str


@dataclass(frozen=True)
class OpportunityModel:
    """
    Complete formal representation of an opportunity.
    
    LAW: OPPORTUNITY-LAW-007 - Opportunity Assessments shall remain independently inspectable.
    """
    
    identity: OpportunityIdentity
    title: str                   # Brief description of the opportunity
    description: str             # Detailed opportunity description
    expected_value: float        # Expected value from pursuing
    probability_of_success: float  # Probability of successful realization
    timing: Tuple[str, ...]      # Timing-related factors
    required_resources: Dict[str, float]  # Resource requirements by type
    competition_intensity: str   # "low", "medium", "high"
    risks: Tuple[OpportunityRisk, ...]
    constraints: Tuple[OpportunityConstraint, ...]
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def hash_state(self) -> str:
        """Compute state hash for evolution tracking."""
        import hashlib
        content = f"{self.identity.opportunity_id}:{self.identity.version}:{self.title}:{self.expected_value}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass(frozen=True)
class OpportunityManagement:
    """
    Opportunity management evaluation result.
    
    LAW: OPPORTUNITY-LAW-008 - Equivalent strategic environments shall produce equivalent opportunity assessments.
    """
    
    evaluation_id: str
    opportunity_identity: OpportunityIdentity
    analysis_results: Tuple[OpportunityAnalysis, ...]
    expected_value: float
    priority_rank: int
    recommended_action: str      # "pursue", "defer", "reject", "monitor"
    confidence_level: float      # Confidence in the assessment
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Analysis metadata


@dataclass(frozen=True)
class OpportunityPortfolio:
    """
    Portfolio of assessed opportunities.
    
    LAW: OPPORTUNITY-LAW-006 - Opportunity assessments shall never suppress significant strategic risks.
    """
    
    portfolio_id: str
    opportunity_identity: OpportunityIdentity
    assessed_opportunities: Tuple[OpportunityModel, ...]
    total_expected_value: float
    total_risk_exposure: float
    
    @property
    def risk_adjusted_return(self) -> float:
        """Calculate risk-adjusted return of the portfolio."""
        if self.total_risk_exposure == 0:
            return self.total_expected_value
        return self.total_expected_value / (1 + self.total_risk_exposure)