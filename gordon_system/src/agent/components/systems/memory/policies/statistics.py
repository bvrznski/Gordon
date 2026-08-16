# Memory Policy Statistics - Phase 5.1.5 Canonical Statistics Module
# ===================================================================
"""
Memory Policy Statistics: Metrics about policy evaluation behavior.

Statistics are observational metrics, NOT decision authority.
They track what policies do but never influence decisions directly.

Key Metrics:
    evaluations     : Total number of evaluations performed
    approvals       : Number of ALLOW decisions
    denials         : Number of DENY decisions
    deferrals       : Number of DEFER decisions
    escalations     : Number of ESCALATE decisions

Statistics Laws:
    STATISTIC-LAW-001: Statistics track but never influence evaluation
    STATISTIC-LAW-002: Statistics are deterministic and reproducible
    STATISTIC-LAW-003: Statistics preserve history for analysis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time


# =============================================================================
# POLICY STATISTICS - Metrics about policy evaluation behavior
# =============================================================================


@dataclass(frozen=True)
class PolicyStatistics:
    """
    Immutable statistics record for a policy or set of policies.
    
    Fields:
        policy_id:           ID of the evaluated policy(s)
        
        # Evaluation counts
        total_evaluations:   Total number of evaluations performed
        approvals:           Number of ALLOW decisions
        denials:             Number of DENY decisions
        deferrals:           Number of DEFER decisions
        escalations:         Number of ESCALATE decisions
        ignores:             Number of IGNORE decisions
        retries:             Number of RETRY decisions
        
        # Timing statistics
        total_evaluation_time_ms: Total time spent evaluating (ms)
        min_evaluation_time_ms:   Minimum evaluation time (ms)
        max_evaluation_time_ms:   Maximum evaluation time (ms)
        
        # Confidence metrics
        avg_confidence:      Average confidence in decisions (0.0-1.0)
        avg_uncertainty:     Average uncertainty in decisions (0.0-1.0)
        
        # Timeline
        first_evaluation_utc: When was the first evaluation?
        last_evaluation_utc:  When was the last evaluation?
    """
    
    policy_id: str                              # ID of evaluated policy(s)
    
    # Evaluation counts
    total_evaluations: int = 0
    approvals: int = 0
    denials: int = 0
    deferrals: int = 0
    escalations: int = 0
    ignores: int = 0
    retries: int = 0
    
    # Timing
    total_evaluation_time_ms: float = 0.0
    min_evaluation_time_ms: Optional[float] = None
    max_evaluation_time_ms: Optional[float] = None
    
    # Confidence metrics
    avg_confidence: float = 1.0
    avg_uncertainty: float = 0.0
    
    # Timeline
    first_evaluation_utc: float = field(default_factory=time.time)
    last_evaluation_utc: float = field(default_factory=time.time)
    
    def record_evaluation(
        self,
        duration_ms: float,
        confidence: float,
        uncertainty: float,
        decision_kind: str,
    ) -> "PolicyStatistics":
        """
        Record a new evaluation and return updated statistics.
        
        Args:
            duration_ms: How long did the evaluation take?
            confidence: Confidence in this decision
            uncertainty: Uncertainty about this decision
            decision_kind: What kind of decision was made?
            
        Returns:
            New PolicyStatistics with updated metrics
        """
        total = self.total_evaluations + 1
        
        # Update confidence average (running average)
        new_avg_confidence = (
            (self.avg_confidence * self.total_evaluations + confidence) / total
        )
        new_avg_uncertainty = (
            (self.avg_uncertainty * self.total_evaluations + uncertainty) / total
        )
        
        # Update timing
        new_min = (
            min(self.min_evaluation_time_ms or float("inf"), duration_ms)
            if self.min_evaluation_time_ms is not None
            else duration_ms
        )
        new_max = max(self.max_evaluation_time_ms or 0, duration_ms)
        
        # Count decision kind
        approvals = self.approvals
        denials = self.denials
        deferrals = self.deferrals
        escalations = self.escalations
        ignores = self.ignores
        retries = self.retries
        
        if decision_kind == "allow":
            approvals += 1
        elif decision_kind == "deny":
            denials += 1
        elif decision_kind == "defer":
            deferrals += 1
        elif decision_kind == "escalate":
            escalations += 1
        elif decision_kind == "ignore":
            ignores += 1
        elif decision_kind == "retry":
            retries += 1
        
        return PolicyStatistics(
            policy_id=self.policy_id,
            total_evaluations=total,
            approvals=approvals,
            denials=denials,
            deferrals=deferrals,
            escalations=escalations,
            ignores=ignores,
            retries=retries,
            total_evaluation_time_ms=self.total_evaluation_time_ms + duration_ms,
            min_evaluation_time_ms=new_min,
            max_evaluation_time_ms=new_max,
            avg_confidence=new_avg_confidence,
            avg_uncertainty=new_avg_uncertainty,
            first_evaluation_utc=self.first_evaluation_utc,
            last_evaluation_utc=time.time(),
        )
    
    def get_approval_rate(self) -> float:
        """Get the approval rate (0.0-1.0)."""
        if self.total_evaluations == 0:
            return 0.0
        return self.approvals / self.total_evaluations
    
    def get_denial_rate(self) -> float:
        """Get the denial rate (0.0-1.0)."""
        if self.total_evaluations == 0:
            return 0.0
        return self.denials / self.total_evaluations
    
    def get_deferral_rate(self) -> float:
        """Get the deferral rate (0.0-1.0)."""
        if self.total_evaluations == 0:
            return 0.0
        return self.deferrals / self.total_evaluations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary representation."""
        return {
            "policy_id": self.policy_id,
            "total_evaluations": self.total_evaluations,
            "approvals": self.approvals,
            "denials": self.denials,
            "deferrals": self.deferrals,
            "escalations": self.escalations,
            "ignores": self.ignores,
            "retries": self.retries,
            "total_evaluation_time_ms": self.total_evaluation_time_ms,
            "min_evaluation_time_ms": self.min_evaluation_time_ms,
            "max_evaluation_time_ms": self.max_evaluation_time_ms,
            "avg_confidence": self.avg_confidence,
            "avg_uncertainty": self.avg_uncertainty,
            "first_evaluation_utc": self.first_evaluation_utc,
            "last_evaluation_utc": self.last_evaluation_utc,
        }


# =============================================================================
# POLICY STATISTICS AGGREGATOR - Aggregate statistics from multiple evaluations
# =============================================================================


class PolicyStatisticsAggregator:
    """
    Aggregate policy statistics across multiple evaluations and policies.
    
    Maintains running aggregates for reporting and analysis.
    """
    
    def __init__(self):
        """Initialize the aggregator."""
        self._policies: Dict[str, PolicyStatistics] = {}
        self._start_time_utc = time.time()
        
    def record_policy_evaluation(
        self,
        policy_id: str,
        duration_ms: float,
        confidence: float,
        uncertainty: float,
        decision_kind: str,
    ) -> None:
        """
        Record an evaluation from a specific policy.
        
        Args:
            policy_id: Which policy evaluated?
            duration_ms: How long did the evaluation take?
            confidence: Confidence in this decision
            uncertainty: Uncertainty about this decision
            decision_kind: What kind of decision was made?
        """
        if policy_id not in self._policies:
            # Initialize with first evaluation
            self._policies[policy_id] = PolicyStatistics(
                policy_id=policy_id,
                total_evaluations=0,
                approvals=0,
                denials=0,
                deferrals=0,
                escalations=0,
                ignores=0,
                retries=0,
                total_evaluation_time_ms=0.0,
                min_evaluation_time_ms=None,
                max_evaluation_time_ms=None,
                avg_confidence=1.0,
                avg_uncertainty=0.0,
                first_evaluation_utc=time.time(),
                last_evaluation_utc=time.time(),
            )
        
        # Update statistics
        self._policies[policy_id] = self._policies[policy_id].record_evaluation(
            duration_ms=duration_ms,
            confidence=confidence,
            uncertainty=uncertainty,
            decision_kind=decision_kind,
        )
    
    def get_policy_statistics(self, policy_id: str) -> Optional[PolicyStatistics]:
        """Get statistics for a specific policy."""
        return self._policies.get(policy_id)
    
    def get_all_policies_statistics(self) -> Dict[str, PolicyStatistics]:
        """Get statistics for all policies."""
        return dict(self._policies)
    
    def get_total_evaluations(self) -> int:
        """Get total evaluations across all policies."""
        return sum(s.total_evaluations for s in self._policies.values())
    
    def get_overall_approval_rate(self) -> float:
        """Get overall approval rate across all policies."""
        total = self.get_total_evaluations()
        if total == 0:
            return 0.0
        approvals = sum(s.approvals for s in self._policies.values())
        return approvals / total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregator state to dictionary representation."""
        return {
            "start_time_utc": self._start_time_utc,
            "current_time_utc": time.time(),
            "total_policies": len(self._policies),
            "total_evaluations": self.get_total_evaluations(),
            "overall_approval_rate": self.get_overall_approval_rate(),
            "policy_statistics": {pid: ps.to_dict() for pid, ps in self._policies.items()},
        }


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Statistics record
    "PolicyStatistics",
    
    # Aggregator
    "PolicyStatisticsAggregator",
]