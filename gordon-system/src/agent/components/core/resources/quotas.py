# Core Quota Enforcement
# ======================
"""
Resource quota management and enforcement.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import time


@dataclass(frozen=True)
class QuotaScope(Enum):
    """Scopes at which quotas can be defined."""
    RUNTIME = "runtime"           # Per runtime-wide quota
    OWNER = "owner"               # Per owner (task, service)
    COMPONENT = "component"       # Per component/service
    SERVICE = "service"           # Per service
    TASK_CLASS = "task_class"     # Per task class (batch, interactive)


@dataclass(frozen=True)
class QuotaLimit:
    """
    A quota limit definition.
    
    Defines the maximum allowed usage for a scope and domain.
    """
    scope: QuotaScope
    scope_id: str              # e.g., "runtime_1", "owner_A"
    domain: str                # e.g., "cpu_cores", "gpu_vram_mb"
    
    limit_value: float         # Maximum allowed
    burst_limit: Optional[float] = None  # Can exceed by this (if supported)


@dataclass(frozen=True)
class QuotaUsage:
    """
    Current usage for a quota scope.
    """
    scope: QuotaScope
    scope_id: str
    domain: str
    
    used: float                # Currently allocated
    limit: float               # Limit value


@dataclass(frozen=True)
class QuotaDecisionType(Enum):
    """Types of quota decisions."""
    ALLOWED = "allowed"          # Request within quota
    EXCEEDS_QUOTA = "exceeds_quota"
    WOULD_EXCEED_QUOTA = "would_exceed_quota"


@dataclass(frozen=True)
class QuotaDecision:
    """
    Decision on quota compliance.
    """
    decision_type: QuotaDecisionType
    
    allowed: bool              # Can proceed
    quota_used: float          # Current usage
    requested: float           # Amount requested
    limit: float               # Limit value
    
    reason: Optional[str] = None


@dataclass(frozen=True)
class ResourceQuota:
    """
    A resource quota configuration.
    
    Defines limits for a scope and domain combination.
    """
    runtime_id: str
    scope: QuotaScope
    scope_id: str
    domain: str
    
    limit_value: float           # Maximum allowed
    burst_limit: Optional[float] = None  # Can exceed by this (if supported)
    window_seconds: float = 60.0  # Quota calculation window


@dataclass(frozen=True)
class QuotaViolation:
    """
    Record of a quota violation.
    """
    violation_id: str
    scope: QuotaScope
    scope_id: str
    domain: str
    limit: float
    attempted: float
    timestamp_utc: float = field(default_factory=time.time)


class QuotaEnforcer:
    """
    Enforcer for resource quotas.
    
    Ensures that allocations don't exceed configured quota limits.
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Current usage by scope and domain
        self._usage: Dict[Tuple[str, str], float] = {}  # (scope_id, domain) -> used
        
        # Quota limits
        self._limits: Dict[Tuple[QuotaScope, str, str], float] = {}  # (scope, id, domain) -> limit
    
    def set_quota_limit(
        self,
        scope: QuotaScope,
        scope_id: str,
        domain: str,
        limit: float
    ) -> None:
        """Set a quota limit for a scope."""
        with self._lock:
            self._limits[(scope, scope_id, domain)] = limit
    
    def check_quota(
        self,
        owner_id: str,
        domain: str,
        requested_amount: float
    ) -> QuotaDecision:
        """
        Check if an allocation request would exceed quotas.
        
        Args:
            owner_id: Who is requesting resources
            domain: Resource domain
            requested_amount: Amount being requested
            
        Returns:
            Decision on quota compliance
        """
        with self._lock:
            current_usage = self._usage.get((owner_id, domain), 0.0)
            
            # Check if within any configured limit
            limit_key = (QuotaScope.OWNER, owner_id, domain)
            limit = self._limits.get(limit_key)
            
            if limit is None:
                return QuotaDecision(
                    decision_type=QuotaDecisionType.ALLOWED,
                    allowed=True,
                    quota_used=current_usage,
                    requested=requested_amount,
                    limit=float('inf'),
                    reason="No quota limit configured",
                )
            
            new_total = current_usage + requested_amount
            
            if new_total > limit:
                return QuotaDecision(
                    decision_type=QuotaDecisionType.WOULD_EXCEED_QUOTA,
                    allowed=False,
                    quota_used=current_usage,
                    requested=requested_amount,
                    limit=limit,
                    reason=f"Would exceed quota of {limit}: {current_usage} + {requested_amount}",
                )
            
            return QuotaDecision(
                decision_type=QuotaDecisionType.ALLOWED,
                allowed=True,
                quota_used=new_total,
                requested=requested_amount,
                limit=limit,
                reason="Within quota",
            )
    
    def record_allocation(self, owner_id: str, domain: str, amount: float) -> None:
        """Record an allocation for quota tracking."""
        with self._lock:
            key = (owner_id, domain)
            current = self._usage.get(key, 0.0)
            self._usage[key] = current + amount
    
    def record_release(self, owner_id: str, domain: str, amount: float) -> None:
        """Record a release for quota tracking."""
        with self._lock:
            key = (owner_id, domain)
            current = self._usage.get(key, 0.0)
            self._usage[key] = max(0.0, current - amount)


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "QuotaScope",
    "QuotaLimit",
    "QuotaUsage",
    "QuotaDecisionType",
    "QuotaDecision",
    "ResourceQuota",
    "QuotaViolation",
    "QuotaEnforcer",
]
