# Core Allocation Model
# ======================
"""
Immutable allocation artifacts with ownership binding.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import uuid
import time

# Import allocation ID type (defined here for self-containment)
class AllocationId(str):
    """Unique identifier for an allocation."""
    
    @classmethod
    def generate(cls) -> "AllocationId":
        return cls(value=f"alloc_{uuid.uuid4().hex[:16]}")
    
    @property
    def value(self) -> str:
        return self


@dataclass(frozen=True)
class AllocationRequest:
    """
    Request for resource allocation.
    
    This is the INPUT - everything needed to evaluate an allocation request.
    """
    runtime_id: str
    owner_id: str
    
    # Task context
    task_id: Optional[str] = None  # When known
    component_id: Optional[str] = None  # When known
    
    # Domain and quantity - must come before fields with defaults for dataclass ordering
    domain: str = ""             # e.g., "cpu_cores", "gpu_vram_mb" (empty string default)
    quantity: float = 0.0        # Amount requested (default needed for dataclass ordering)
    minimum_quantity: Optional[float] = None  # Minimum acceptable
    
    # Timing
    deadline_utc: Optional[float] = None
    
    # Resource requirements
    required_attributes: Tuple[str, ...] = field(default_factory=tuple)  # e.g., "cuda", "high_memory"
    
    # Placement hints
    affinity_resources: Tuple[str, ...] = field(default_factory=tuple)
    anti_affinity_resources: Tuple[str, ...] = field(default_factory=tuple)
    
    # Priority and policy
    priority: int = 0
    fallback_policy: str = "queue"  # queue, fail, or fallback_domain
    
    # Preemption policy
    preemption_allowed: bool = False
    preemptible: bool = True      # Can this work be preempted?
    
    # Quota context
    quota_context: Optional[str] = None
    
    # Correlation
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


@dataclass(frozen=True)
class AllocationCandidate:
    """
    Candidate resource for allocation.
    
    Used during allocation to track potential resources and their scores.
    """
    resource_id: str
    domain: str
    available_capacity: float
    
    # Scoring
    affinity_score: float = 0.0      # Higher is better (proximity, topology)
    anti_affinity_penalty: float = 0.0  # Penalty for anti-affinity violations
    
    @property
    def effective_score(self) -> float:
        """Get overall score (affinity - penalty)."""
        return self.affinity_score - self.anti_affinity_penalty


@dataclass(frozen=True)
class AllocationScore:
    """
    Final allocation score.
    
    Combines multiple factors into a single score for ranking candidates.
    """
    capacity_score: float       # Based on available vs requested
    affinity_score: float       # Topology and placement preferences
    fairness_score: float       # Fairness of allocation
    priority_score: float       # Based on request priority
    
    @property
    def total(self) -> float:
        """Get weighted total score."""
        return (
            0.4 * self.capacity_score +
            0.2 * self.affinity_score +
            0.2 * self.fairness_score +
            0.2 * self.priority_score
        )


class AllocationDecisionType(Enum):
    """
    Typed allocation decision types.
    
    Each type has specific semantics for what should happen next.
    """
    ALLOCATE = "allocate"                  # Full allocation granted
    ALLOCATE_PARTIAL = "allocate_partial"  # Partial quantity granted
    DEFER = "defer"                        # Defer to later (queue)
    QUEUE = "queue"                        # Add to queue for later consideration
    REJECT_CAPACITY = "reject_capacity"
    REJECT_QUOTA = "reject_quota"
    REJECT_POLICY = "reject_policy"
    REJECT_CONTENTION = "reject_contention"
    REQUIRE_PREEMPTION = "require_preemption"
    REQUIRE_FALLBACK = "require_fallback"


@dataclass(frozen=True)
class AllocationDecision:
    """
    Decision on an allocation request.
    
    This is the OUTPUT - an immutable record of what was decided.
    """
    decision_type: AllocationDecisionType
    
    # For granted allocations
    allocation_id: Optional[str] = None
    resources_selected: Tuple[str, ...] = field(default_factory=tuple)
    quantities_allocated: Dict[str, float] = field(default_factory=dict)
    
    # For partial/deferred
    available_capacity: Optional[float] = None
    reason: Optional[str] = None
    
    # Decision context
    evaluated_at_utc: float = field(default_factory=time.time)
    
    algorithm_id: str = "baseline"
    fairness_result: Optional["FairnessResult"] = None  # Reference, not import
    quota_result: Optional["QuotaDecision"] = None       # Reference
    
    @classmethod
    def create_allocate(cls, allocation_id: str) -> "AllocationDecision":
        """Create an allocate decision."""
        return cls(
            decision_type=AllocationDecisionType.ALLOCATE,
            allocation_id=allocation_id,
        )
    
    @classmethod
    def create_partial(
        cls,
        allocation_id: str,
        quantities: Dict[str, float]
    ) -> "AllocationDecision":
        """Create a partial allocate decision."""
        return cls(
            decision_type=AllocationDecisionType.ALLOCATE_PARTIAL,
            allocation_id=allocation_id,
            quantities_allocated=quantities,
        )
    
    @classmethod
    def create_defer(cls, reason: str = "") -> "AllocationDecision":
        """Create a defer decision."""
        return cls(
            decision_type=AllocationDecisionType.DEFER,
            reason=f"Deferred: {reason}" if reason else "Deferred",
        )
    
    @classmethod
    def create_queue(cls, reason: str = "") -> "AllocationDecision":
        """Create a queue decision."""
        return cls(
            decision_type=AllocationDecisionType.QUEUE,
            reason=f"Queued: {reason}" if reason else "Queued",
        )
    
    @classmethod
    def create_reject_capacity(cls, reason: str) -> "AllocationDecision":
        """Create a capacity rejection."""
        return cls(
            decision_type=AllocationDecisionType.REJECT_CAPACITY,
            reason=f"No capacity: {reason}",
        )
    
    @classmethod
    def create_reject_quota(cls, reason: str) -> "AllocationDecision":
        """Create a quota rejection."""
        return cls(
            decision_type=AllocationDecisionType.REJECT_QUOTA,
            reason=f"Quota exceeded: {reason}",
        )
    
    @classmethod
    def create_reject_policy(cls, reason: str) -> "AllocationDecision":
        """Create a policy rejection."""
        return cls(
            decision_type=AllocationDecisionType.REJECT_POLICY,
            reason=f"Policy violation: {reason}",
        )


@dataclass(frozen=True)
class AllocationFailure:
    """
    Record of an allocation failure.
    
    Used for diagnostics and retry decisions.
    """
    failure_id: str
    failure_type: str           # capacity, quota, policy, contention, etc.
    reason: str
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class AllocationReceipt:
    """
    Receipt for a granted allocation.
    
    Used to prove that an allocation was authorized at a specific time.
    """
    receipt_id: str
    allocation_id: str
    issued_at_utc: float
    expires_at_utc: float
    
    # Capacity snapshot at issuance
    total_capacity: float
    free_capacity: float
    headroom: float


# =============================================================================
# Allocation State and Record
# =============================================================================

class AllocationState(Enum):
    """States in the allocation lifecycle."""
    REQUESTED = "requested"
    VALIDATED = "validated"
    QUEUED = "queued"
    RESERVED = "reserved"
    ALLOCATED = "allocated"
    LEASED = "leased"
    BOUND = "bound"
    ACTIVE = "active"
    IN_USE = "in_use"
    RELEASING = "releasing"
    RELEASED = "released"
    RECONCILED = "reconciled"
    
    # Failure states
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass(frozen=True)
class Allocation:
    """
    An allocated resource.
    
    This is the canonical record of a granted allocation - binding ownership
    to resources with capacity accounting.
    """
    allocation_id: str
    
    runtime_id: str
    owner_id: str
    
    resource_domain: str        # e.g., "cpu_cores", "gpu_vram_mb"
    
    quantity_allocated: float
    requested_quantity: float
    min_quantity: float         # Minimum acceptable (for partial)
    
    created_at: float
    state: AllocationState = AllocationState.ALLOCATED
    
    # Bound resources (if known)
    resource_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    # Lease info (if leased)
    lease_id: Optional[str] = None
    lease_expires_at: Optional[float] = None
    
    # Preemption info
    preemptible: bool = True
    
    # Quota context
    quota_context: Optional[str] = None


@dataclass(frozen=True)
class AllocationResult:
    """
    Result of an allocation request.
    
    Includes the decision plus any additional information.
    """
    decision: AllocationDecision
    allocation: Optional[Allocation] = None  # If granted
    
    reservation_used: Optional[str] = None   # If a reservation was used
    
    @property
    def is_granted(self) -> bool:
        """Check if allocation was granted."""
        return self.decision.decision_type in (
            AllocationDecisionType.ALLOCATE,
            AllocationDecisionType.ALLOCATE_PARTIAL,
        )


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "AllocationRequest",
    "AllocationCandidate",
    "AllocationScore",
    "AllocationDecisionType",
    "AllocationDecision",
    "AllocationFailure",
    "AllocationReceipt",
    "AllocationState",
    "Allocation",
    "AllocationResult",
    "AllocationId",
]
