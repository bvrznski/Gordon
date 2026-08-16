# Reward Network - Result Model
# =============================

"""
Reward evaluation result model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class RewardEvaluationResult:
    """
    Result of a reward evaluation.
    
    OUTPUT CONTRACT (Phase 4.10.1 - Part 2):
        • landscape: Complete RewardLandscape with all estimates
        • state: RewardState summary
        • findings: Evaluation findings
        • limitations: Known limitations
        • trace: Evaluation trace for provenance
        • status: Success/failure indicator
        
    The result is immutable and contains only semantic information.
    It does not modify any system state or make executive decisions.
    """
    
    # Core output
    landscape_id: str
    """Unique identifier for the landscape."""
    
    reward_estimates: Tuple[dict, ...] = field(default_factory=tuple)
    """All computed RewardEstimates (as dictionaries)."""
    
    timescale_rewards: dict = field(default_factory=dict)
    """Multi-timescale reward values."""
    
    hierarchical_rewards: dict = field(default_factory=dict)
    """Hierarchical reward values."""
    
    total_magnitude: float = 0.0
    """Sum of all estimate magnitudes."""
    
    # State summary
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    
    # Metadata
    status: str = "success"
    """Evaluation status (success/failure)."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from evaluation."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this result."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Evaluation trace for provenance."""
    
    @property
    def is_success(self) -> bool:
        """Check if evaluation succeeded."""
        return self.status == "success"
    
    @property
    def estimate_count(self) -> int:
        """Get count of reward estimates."""
        return len(self.reward_estimates)