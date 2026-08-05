# Core Fairness Assessment
# =========================
"""
Resource allocation fairness evaluation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import time


@dataclass(frozen=True)
class FairnessKey:
    """
    Key for grouping allocations in fairness assessment.
    
    Examples:
        - owner_id: "task_123"
        - tenant_id: "tenant_A"
        - service_name: "model_service"
        - component_type: "worker"
    """
    domain: str
    group_key: str  # e.g., owner_id, tenant_id
    
    @classmethod
    def for_owner(cls, domain: str, owner_id: str) -> "FairnessKey":
        """Create a fairness key for an owner."""
        return cls(domain=domain, group_key=owner_id)
    
    @classmethod
    def for_tenant(cls, domain: str, tenant_id: str) -> "FairnessKey":
        """Create a fairness key for a tenant."""
        return cls(domain=domain, group_key=tenant_id)


@dataclass(frozen=True)
class FairnessPolicy:
    """
    Configuration for fairness evaluation.
    
    Defines weights and constraints for fair allocation.
    """
    domain: str
    weight: float = 1.0                    # Relative priority weight
    
    reserved_share: float = 0.0            # Minimum guaranteed (fraction of total)
    burst_allowance: float = 1.5           # Can exceed quota by this much
    starvation_threshold_seconds: float = 300.0  # Alert if waiting > 5min
    
    max_concurrent_per_key: int = 10       # Per-key limit


@dataclass(frozen=True)
class FairnessAssessment:
    """
    Assessment of whether an allocation is fair.
    
    Evaluates current usage vs. policy constraints.
    """
    key: FairnessKey
    current_usage: float                  # Currently allocated
    requested: float                      # Requested now
    quota_limit: Optional[float]          # Hard limit (if any)
    
    is_within_quota: bool = True
    would_cause_starvation: bool = False
    
    fairness_score: float = 1.0           # 0.0 to 1.0


@dataclass(frozen=True)
class FairnessResult:
    """
    Final fairness evaluation result.
    """
    permitted: bool                       # Can proceed with allocation
    assessment: FairnessAssessment
    reason: str = ""                      # Explanation if not permitted


class FairnessAssessor:
    """
    Assessor of resource allocation fairness.
    
    Evaluates whether granting a request would violate fairness constraints.
    """
    
    def __init__(self):
        self._lock = __import__("threading").RLock()
        
        # Current usage by domain and key
        self._usage_by_domain: Dict[str, Dict[str, float]] = {}
        
        # Policy configuration
        self._policies: Dict[FairnessKey, FairnessPolicy] = {}
    
    def configure_policy(self, policy: FairnessPolicy) -> None:
        """Configure fairness policy for a key."""
        with self._lock:
            self._policies[FairnessKey(policy.domain, "global")] = policy
    
    def assess(
        self,
        owner_id: str,
        domain: str,
        current_ownership: Dict[str, float],
        quota_limit: Optional[float] = None
    ) -> FairnessResult:
        """
        Assess whether an allocation is fair.
        
        Args:
            owner_id: Who is requesting resources
            domain: Resource domain
            current_ownership: Current usage by all owners in this domain
            quota_limit: Hard limit (if any)
            
        Returns:
            Assessment of fairness
        """
        with self._lock:
            requested = current_ownership.get(owner_id, 0.0) + 1.0
            
            # Check if would exceed quota
            if quota_limit and requested > quota_limit:
                return FairnessResult(
                    permitted=False,
                    assessment=FairnessAssessment(
                        key=FairnessKey.for_owner(domain, owner_id),
                        current_usage=current_ownership.get(owner_id, 0.0),
                        requested=requested,
                        quota_limit=quota_limit,
                        is_within_quota=False,
                    ),
                    reason=f"Would exceed quota of {quota_limit}",
                )
            
            return FairnessResult(
                permitted=True,
                assessment=FairnessAssessment(
                    key=FairnessKey.for_owner(domain, owner_id),
                    current_usage=current_ownership.get(owner_id, 0.0),
                    requested=requested,
                    quota_limit=quota_limit,
                    is_within_quota=True,
                ),
                reason="Within quota and fair",
            )


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "FairnessKey",
    "FairnessPolicy",
    "FairnessAssessment",
    "FairnessResult",
    "FairnessAssessor",
]