# Strategic Portfolio Contract - Phase 7.37 Part 2
# ================================================

"""
Portfolio Management for Strategic Reasoning.

This module implements the canonical portfolio contracts specified in Phase 7.37 Part 2:

- PortfolioManagement: Evaluates initiative balance, risk diversification, resource distribution
- PortfolioIdentity: Unique identifier for portfolio tracking
- StrategicProject: Individual project within a portfolio
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class PortfolioIdentity:
    """
    Unique identifier for a strategic portfolio.
    
    LAW: PORTFOLIO-LAW-001 - Every Strategic Portfolio shall possess one explicit identity.
    """
    
    portfolio_id: str             # UUID4 string
    semantic_identity: str        # Stable semantic reference across runs
    version: int                  # Version number for evolution tracking


@dataclass(frozen=True)
class StrategicProject:
    """
    Individual project/strategy within the portfolio.
    
    LAW: PORTFOLIO-LAW-002 - Portfolio composition shall remain explicit.
    """
    
    project_id: str
    name: str
    description: str
    expected_value: float
    resource_requirements: Dict[str, float]
    timeline_months: int
    risk_score: float             # 0.0 to 1.0


@dataclass(frozen=True)
class PortfolioConstraint:
    """Constraints that bound portfolio optimization."""
    
    constraint_id: str
    type: str                     # e.g., "max_risk", "min_diversity"
    description: str
    hard: bool                    # Hard constraints cannot be violated
    value: Any


@dataclass(frozen=True)
class PortfolioAnalysis:
    """
    Analysis result for a portfolio.
    
    LAW: PORTFOLIO-LAW-004 - Portfolio provenance shall remain complete.
    """
    
    analysis_id: str
    portfolio_identity: PortfolioIdentity
    total_expected_value: float
    overall_risk: float
    diversification_score: float  # 0.0 to 1.0 (higher = more diversified)
    resource_utilization: Dict[str, float]
    project_balance: str          # "balanced", "concentrated", "overcommitted"


@dataclass(frozen=True)
class PortfolioEvolution:
    """
    Records evolution of portfolio composition over time.
    
    LAW: PORTFOLIO-LAW-005 - Portfolio revisions shall preserve history.
    """
    
    evolution_id: str
    portfolio_identity: PortfolioIdentity
    timestamp_utc: float
    change_type: str              # "add_project", "remove_project", "reallocate"
    previous_state_hash: str      # Hash of previous state for verification
    change_description: str


@dataclass(frozen=True)
class PortfolioModel:
    """
    Complete formal representation of a portfolio.
    
    LAW: PORTFOLIO-LAW-007 - Strategic Portfolios shall remain independently inspectable.
    """
    
    identity: PortfolioIdentity
    projects: Tuple[StrategicProject, ...]
    constraints: Tuple[PortfolioConstraint, ...]
    created_at_utc: float = field(default_factory=time.time)
    
    def get_total_expected_value(self) -> float:
        """Sum of expected values for all projects."""
        return sum(p.expected_value for p in self.projects)
    
    def get_total_risk(self) -> float:
        """
        Calculate overall portfolio risk.
        
        LAW: PORTFOLIO-LAW-006 - Portfolio optimization shall never violate declared strategic constraints.
        """
        if not self.projects:
            return 0.0
        # Weighted average risk based on project scale
        total_value = sum(p.expected_value for p in self.projects)
        if total_value == 0:
            return max(p.risk_score for p in self.projects) if self.projects else 0.0
        
        weighted_sum = sum(p.risk_score * p.expected_value for p in self.projects)
        return weighted_sum / total_value
    
    def get_resource_requirements(self) -> Dict[str, float]:
        """Aggregate resource requirements across all projects."""
        result: Dict[str, float] = {}
        for project in self.projects:
            for resource, amount in project.resource_requirements.items():
                result[resource] = result.get(resource, 0.0) + amount
        return result
    
    @property
    def hash_state(self) -> str:
        """Compute state hash for evolution tracking."""
        import hashlib
        content = f"{self.identity.portfolio_id}:{self.identity.version}:{self.get_total_expected_value()}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass(frozen=True)
class PortfolioManagement:
    """
    Portfolio management evaluation result.
    
    LAW: PORTFOLIO-LAW-008 - Equivalent strategic inputs shall produce equivalent portfolio structures.
    """
    
    evaluation_id: str
    portfolio_identity: PortfolioIdentity
    analysis_results: Tuple[PortfolioAnalysis, ...]
    total_expected_value: float
    overall_risk: float
    diversification_score: float
    recommended_projects: Tuple[str, ...]  # Projects to add or prioritize
    deferred_projects: Tuple[str, ...]     # Projects to defer
    rejected_projects: Tuple[str, ...]     # Projects to reject
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Analysis metadata


@dataclass(frozen=True)
class PortfolioResourceAllocation:
    """
    Resource allocation for a portfolio.
    
    LAW: PORTFOLIO-LAW-003 - Portfolio dependencies shall remain explicit.
    """
    
    allocation_id: str
    portfolio_identity: PortfolioIdentity
    resource_allocations: Dict[str, float]  # resource_type -> allocated_amount
    total_budget: float
    
    @property
    def utilization_rate(self) -> float:
        """Calculate budget utilization rate."""
        if self.total_budget == 0:
            return 0.0
        return sum(self.resource_allocations.values()) / self.total_budget


@dataclass(frozen=True)
class PortfolioBalanceMetrics:
    """
    Detailed metrics for portfolio balance analysis.
    
    LAW: PORTFOLIO-LAW-002 - Portfolio composition shall remain explicit.
    """
    
    metrics_id: str
    portfolio_identity: PortfolioIdentity
    project_count: int
    value_distribution: Tuple[float, ...]  # Individual project values sorted
    risk_distribution: Tuple[float, ...]   # Individual project risks sorted
    resource_concentration: float          # How concentrated are resources?
    diversity_index: float                 # Entropy-based diversity measure
    
    @property
    def is_well_balanced(self) -> bool:
        """Check if portfolio appears well-balanced."""
        return (0.3 <= self.resource_concentration <= 0.7 and 
                0.5 <= self.diversity_index)