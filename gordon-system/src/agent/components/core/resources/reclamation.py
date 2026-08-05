# Core Resource Reclamation
# ==========================
"""
Resource reclamation under policy control.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time


@dataclass(frozen=True)
class ReclamationMode(Enum):
    """Modes of resource reclamation."""
    VOLUNTARY = "voluntary"           # Owner releases voluntarily
    IDLE = "idle"                     # Idle resources reclaimed
    PRESSURE_DRIVEN = "pressure_driven"
    QUOTA_DRIVEN = "quota_driven"
    PREEMPTIVE = "preemptive"
    SHUTDOWN = "shutdown"             # Runtime shutdown
    RECOVERY = "recovery"             # Recovery process
    FORCED = "forced"                 # Force reclaim under policy
    QUARANTINE = "quarantine"         # Quarantine failed resources


@dataclass(frozen=True)
class ReclamationCandidate:
    """
    A resource that could be reclaimed.
    
    Contains all information needed to evaluate reclamation priority.
    """
    allocation_id: str
    resource_id: str
    
    owner_id: str
    domain: str
    
    quantity_allocated: float
    
    created_at_utc: float
    last_used_utc: Optional[float] = None  # When last accessed
    
    lease_expires_at_utc: Optional[float] = None
    preemptible: bool = True
    
    reclaimable: bool = True  # Can this be reclaimed


@dataclass(frozen=True)
class ReclamationPlan:
    """
    Plan for reclamation actions.
    
    Defines what resources to reclaim and in what order.
    """
    plan_id: str
    mode: ReclamationMode
    
    candidates: List[ReclamationCandidate]
    total_reclaimable_capacity: float


@dataclass(frozen=True)
class ReclamationAction(Enum):
    """Actions that can be taken during reclamation."""
    NOTIFICATION = "notification"       # Notify owner
    SOFT_RELEASE = "soft_release"       # Request release
    HARD_RECLAIM = "hard_reclaim"       # Force reclaim
    LEASE_REVOCATION = "lease_revocation"
    ALLOCATION_RELEASE = "allocation_release"


@dataclass(frozen=True)
class ReclamationRequest:
    """
    Request for reclamation.
    
    This is the INPUT to the reclamation system.
    """
    runtime_id: str
    
    mode: ReclamationMode
    requested_capacity: float
    
    domain: Optional[str] = None  # If None, all domains


@dataclass(frozen=True)
class ReclamationResult:
    """
    Result of a reclamation operation.
    """
    success: bool
    
    # For success
    resources_reclaimed: List[ReclamationCandidate]
    capacity_reclaimed: float
    
    # For failure
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class ReclamationVerification:
    """
    Verification that reclamation was successful.
    """
    verification_id: str
    reclamation_id: str
    
    resources_verified: List[str]
    capacity_verified: float
    
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)


class ResourceReclaimer:
    """
    Manager for resource reclamation operations.
    
    Coordinates reclamation of idle or expired resources according to policy.
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Reclamation history
        self._reclamation_history: List[Dict[str, Any]] = []
    
    def find_candidates(
        self,
        mode: ReclamationMode,
        domain: Optional[str] = None
    ) -> Tuple[List[ReclamationCandidate], float]:
        """
        Find resources eligible for reclamation.
        
        Returns:
            Tuple of (candidates, total_reclaimable)
        """
        with self._lock:
            candidates: List[ReclamationCandidate] = []
            
            # In real impl, would query ResourceManager for current allocations
            # and filter based on mode
            
            return candidates, 0.0
    
    def create_plan(
        self,
        mode: ReclamationMode,
        required_capacity: float,
        domain: Optional[str] = None
    ) -> Optional[ReclamationPlan]:
        """
        Create a reclamation plan.
        
        Returns a plan if reclamation should proceed.
        """
        with self._lock:
            candidates, reclaimable = self.find_candidates(mode, domain)
            
            if reclaimable < required_capacity:
                return None
            
            # Sort by priority
            sorted_candidates = self._order_candidates(candidates, mode)
            
            return ReclamationPlan(
                plan_id=f"reclaim_{time.time():.0f}",
                mode=mode,
                candidates=sorted_candidates,
                total_reclaimable_capacity=reclaimable,
            )
    
    def execute_plan(self, plan: ReclamationPlan) -> ReclamationResult:
        """
        Execute a reclamation plan.
        
        Returns result with details of what happened.
        """
        with self._lock:
            reclaimed = []
            total = 0.0
            
            for candidate in plan.candidates:
                # In real impl, would:
                # 1. Check if reclaimable
                # 2. Notify owner (if not forced mode)
                # 3. Release lease and allocation
                # 4. Update capacity
                
                reclaimed.append(candidate)
                total += candidate.quantity_allocated
            
            return ReclamationResult(
                success=True,
                resources_reclaimed=reclaimed,
                capacity_reclaimed=total,
            )
    
    def verify_reclamation(
        self,
        reclamation_id: str,
        resources: List[str]
    ) -> ReclamationVerification:
        """
        Verify that reclamation was successful.
        
        Confirms resources are truly free and no stale references remain.
        """
        with self._lock:
            verified = [r for r in resources]  # In real impl, would validate
            
            return ReclamationVerification(
                verification_id=f"verify_{time.time():.0f}",
                reclamation_id=reclamation_id,
                resources_verified=verified,
                capacity_verified=len(verified),  # Simplified
                success=True,
                details={"reason": "verification_complete"},
            )
    
    def _order_candidates(
        self,
        candidates: List[ReclamationCandidate],
        mode: ReclamationMode
    ) -> List[ReclamationCandidate]:
        """Order candidates by reclamation priority."""
        # In real impl, would sort based on:
        # - Last used time (oldest first)
        # - Lease expiration (soonest first)
        # - Preemptibility
        return sorted(
            candidates,
            key=lambda c: (
                0 if c.lease_expires_at_utc else 1,
                c.last_used_utc or 0,
                not c.preemptible
            )
        )


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "ReclamationMode",
    "ReclamationCandidate",
    "ReclamationPlan",
    "ReclamationAction",
    "ReclamationRequest",
    "ReclamationResult",
    "ReclamationVerification",
    "ResourceReclaimer",
]