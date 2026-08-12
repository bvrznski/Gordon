# Core Preemption System
# =======================
"""
Resource preemption under policy control.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time


@dataclass(frozen=True)
class PreemptionEligibility(Enum):
    """Whether a resource can be preempted."""
    ELIGIBLE = "eligible"           # Can be preempted
    NOT_ELIGIBLE = "not_eligible"   # Cannot be preempted (critical work)
    MAYBE_ELIGIBLE = "maybe_eligible"  # Depends on policy


@dataclass(frozen=True)
class PreemptionCandidate:
    """
    A resource that could be preempted.
    
    Contains all information needed to evaluate whether preemption is appropriate.
    """
    resource_id: str
    current_owner_id: str
    
    lease_expires_at_utc: Optional[float] = None  # When current lease expires
    priority: int = 0                             # Lower priority = better candidate
    preemptible: bool = True                      # Can this work be preempted?
    
    # Work characteristics
    is_critical: bool = False                     # Would failure cause major impact?
    checkpointable: bool = True                   # Can state be saved for restart?
    rollback_capable: bool = True                 # Can we safely roll back
    
    # Timing
    elapsed_time_seconds: float = 0.0             # How long already running
    estimated_remaining_seconds: float = 3600.0   # Estimated remaining time


@dataclass(frozen=True)
class PreemptionPlan:
    """
    Plan for preemption actions.
    
    Defines what resources to reclaim and how.
    """
    plan_id: str
    
    candidates: List[PreemptionCandidate]
    total_reclaimable_capacity: float
    required_capacity: float
    
    step_order: Tuple[str, ...] = field(default_factory=tuple)  # Resource IDs in order


@dataclass(frozen=True)
class PreemptionRequest:
    """
    Request for preemption.
    
    This is the INPUT to the preemption system.
    """
    runtime_id: str
    requesting_owner_id: str
    
    domain: str
    requested_capacity: float
    
    priority: int = 0                     # Higher = more urgent
    deadline_utc: Optional[float] = None
    
    can_preempt_self: bool = False        # Can preempt own work


@dataclass(frozen=True)
class PreemptionDecisionType(Enum):
    """Types of preemption decisions."""
    NO_PREEMPTION_NEEDED = "no_preemption_needed"  # Enough capacity
    PREEMPTION_RECOMMENDED = "preemption_recommended"
    PREEMPTION_REQUIRED = "preemption_required"   # Cannot proceed otherwise


@dataclass(frozen=True)
class PreemptionResult:
    """
    Result of a preemption operation.
    """
    success: bool
    
    # For success
    preemptions_performed: int = 0        # How many resources were preempted
    capacity_reclaimed: float = 0.0       # Total capacity reclaimed
    
    # For failure
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class PreemptionFailure(Enum):
    """Types of preemption failures."""
    NO_ELIGIBLE_CANDIDATES = "no_eligible_candidates"
    NOT_ENOUGH_CAPACITY_TO_RECLAIM = "not_enough_capacity_to_reclaim"
    POLICY_VIOLATION = "policy_violation"  # Cannot preempt critical work
    RECOVERY_FAILED = "recovery_failed"     # Preempted but couldn't restart


class Preemptor:
    """
    Manager for resource preemption operations.
    
    Evaluates candidates and executes preemption when policy permits.
    """
    
    def __init__(
        self,
        runtime_id: str,
        lease_manager  # Forward reference
    ):
        self._runtime_id = runtime_id
        self._lease_manager = lease_manager
        
        self._lock = __import__("threading").RLock()
        
        # Track preempted work for recovery
        self._preemption_history: List[Dict[str, Any]] = []
    
    def find_candidates(
        self,
        owner_id: str,
        domain: str,
        requested_amount: float
    ) -> Tuple[bool, List[PreemptionCandidate]]:
        """
        Find resources that could be preempted.
        
        Returns:
            Tuple of (can_preempt, list_of_candidates)
        """
        with self._lock:
            # Get current allocations in this domain
            # This is a simplified version - real impl would query ResourceManager
            
            candidates: List[PreemptionCandidate] = []
            
            # Find low-priority preemptible work in same or other owners
            for candidate_owner, usage in self._get_ownership_by_owner(domain).items():
                if candidate_owner == owner_id:
                    continue  # Don't preempt own critical work
                
                # Check if any allocations are preemptible
                candidates.append(PreemptionCandidate(
                    resource_id=f"resource_{candidate_owner}",
                    current_owner_id=candidate_owner,
                    priority=-10,  # Low priority
                    preemptible=True,
                    is_critical=False,
                    checkpointable=True,
                ))
            
            can_preempt = len(candidates) > 0
            
            return can_preempt, candidates
    
    def evaluate_plan(
        self,
        domain: str,
        required_capacity: float
    ) -> Optional[PreemptionPlan]:
        """
        Evaluate if preemption is viable.
        
        Returns a plan if preemption should proceed.
        """
        with self._lock:
            can_preempt, candidates = self.find_candidates(
                owner_id="system",
                domain=domain,
                requested_amount=required_capacity
            )
            
            if not can_preempt or not candidates:
                return None
            
            # Sort by priority (lowest first)
            sorted_candidates = sorted(candidates, key=lambda c: c.priority)
            
            # Check total reclaimable capacity
            total_reclaimable = sum(
                self._get_candidate_capacity(c) for c in sorted_candidates
            )
            
            if total_reclaimable < required_capacity:
                return None
            
            # Create plan
            reclaim_order = tuple(c.resource_id for c in sorted_candidates)
            
            return PreemptionPlan(
                plan_id=f"preempt_{time.time():.0f}",
                candidates=sorted_candidates,
                total_reclaimable_capacity=total_reclaimable,
                required_capacity=required_capacity,
                step_order=reclaim_order,
            )
    
    def execute_preemption(self, plan: PreemptionPlan) -> PreemptionResult:
        """
        Execute a preemption plan.
        
        Returns result with details of what happened.
        """
        with self._lock:
            successes = 0
            reclaimed = 0.0
            
            for candidate in plan.candidates:
                # In real impl, would:
                # 1. Notify owner
                # 2. Revoke lease
                # 3. Release allocation
                # 4. Update capacity
                
                successes += 1
                reclaimed += self._get_candidate_capacity(candidate)
            
            return PreemptionResult(
                success=True,
                preemptions_performed=successes,
                capacity_reclaimed=reclaimed,
            )
    
    def _get_ownership_by_owner(self, domain: str) -> Dict[str, float]:
        """Get current ownership by owner for a domain."""
        # This would query the ResourceManager
        return {}
    
    def _get_candidate_capacity(self, candidate: PreemptionCandidate) -> float:
        """Get reclaimable capacity from a candidate."""
        return 1.0  # Simplified - real impl would get actual allocation size


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "PreemptionEligibility",
    "PreemptionCandidate",
    "PreemptionPlan",
    "PreemptionRequest",
    "PreemptionDecisionType",
    "PreemptionResult",
    "PreemptionFailure",
    "Preemptor",
]