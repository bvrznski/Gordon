# Strategic Trade-offs - Phase 7.18
# =================================

"""
Canonical Trade-off Analysis for Phase 7.18.

Trade-off analysis evaluates expected value, resource utilization,
time, risk, uncertainty, opportunity cost, and related metrics.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategicTradeoff:
    """
    Result of trade-off analysis between competing objectives or strategies.
    
    Trade-off analysis evaluates:
        - Expected value of each option
        - Resource utilization requirements
        - Time constraints and schedules
        - Risk profiles
        - Uncertainty levels
        - Opportunity costs
    """
    
    # Identity
    tradeoff_id: str                        # Unique tradeoff identifier
    
    # Input
    objective_set_id: str                   # Which objectives are involved?
    
    # Competing options
    competing_options: List[str]            # IDs of competing strategies/objectives
    
    # Evaluation metrics (quantitative)
    evaluation_metrics: Dict[str, float]    # metric_name -> value
    
    # Selected compromise
    selected_compromise: Optional[str] = None  # Which option was chosen?
    
    # Rationale for the trade-off
    tradeoff_rationale: str = ""            # Why was this trade-off made?
    
    # Rejected alternatives (for traceability)
    rejected_alternatives: List[str] = field(default_factory=list)
    
    # Timing
    analyzed_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class TradeoffAnalysis:
    """
    Comprehensive trade-off analysis for a strategic decision.
    """
    
    # Identity
    analysis_id: str
    
    # Input
    objective_set_id: str
    strategy_identity: Optional[str] = None
    
    # All trade-offs identified
    tradeoffs: List[StrategicTradeoff]
    
    # Overall assessment
    overall_tradeoff_quality: str = "good"  # good, acceptable, poor
    
    # Consistency with strategic goals
    consistency_with_objectives: float = 1.0  # 0.0 to 1.0
    
    # Provenance
    analyzed_at_utc: float = field(default_factory=time.time)
    
    @property
    def has_conflicts(self) -> bool:
        """Check if any trade-offs resulted in conflicts."""
        return len([t for t in self.tradeoffs if not t.selected_compromise]) > 0


@dataclass(frozen=True)
class TradeoffMetrics:
    """
    Metrics used in trade-off evaluation.
    """
    
    # Expected value
    expected_value: float = 0.0
    
    # Resource utilization (normalized 0-1, higher = more resources needed)
    resource_utilization: float = 0.0
    
    # Time to completion (in days)
    time_to_completion: float = 0.0
    
    # Risk level (normalized 0-1, higher = more risk)
    risk_level: float = 0.0
    
    # Uncertainty level (normalized 0-1, higher = more uncertainty)
    uncertainty_level: float = 0.0
    
    # Opportunity cost (normalized 0-1)
    opportunity_cost: float = 0.0


__all__ = [
    "StrategicTradeoff",
    "TradeoffAnalysis",
    "TradeoffMetrics",
]