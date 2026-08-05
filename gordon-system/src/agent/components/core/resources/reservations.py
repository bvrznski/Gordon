# Core Reservation Model
# =======================
"""
Immutable reservation artifacts with bounded lifetimes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import uuid
import time


@dataclass(frozen=True)
class ReservationRequest:
    """
    Request for a resource reservation.
    
    This is the INPUT - everything needed to evaluate whether a reservation
    should be granted.
    """
    runtime_id: str
    owner_id: str
    domain: str                  # e.g., "cpu", "gpu_vram_mb"
    requested_quantity: float
    minimum_quantity: Optional[float] = None   # Minimum acceptable (for partial)
    preferred_quantity: Optional[float] = None  # Preferred quantity
    
    deadline_utc: Optional[float] = None       # Deadline by which needed
    priority: Optional[int] = None              # Higher = more urgent
    
    # Affinity/anti-affinity
    affinity_resources: Tuple[str, ...] = field(default_factory=tuple)
    anti_affinity_resources: Tuple[str, ...] = field(default_factory=tuple)
    
    # Fallback policy
    fallback_policy: str = "queue"  # queue, fail, or fallback_domain
    
    @property
    def effective_minimum(self) -> float:
        """Get minimum quantity (default to requested if not specified)."""
        return self.minimum_quantity or self.requested_quantity
    
    @property
    def effective_preferred(self) -> float:
        """Get preferred quantity."""
        return self.preferred_quantity or self.requested_quantity


@dataclass(frozen=True)
class ReservationRequirement:
    """
    Requirements for a reservation decision.
    
    Used by allocators to determine if they can satisfy a request.
    """
    domain: str
    minimum_quantity: float
    deadline_utc: Optional[float] = None
    affinity_resources: Tuple[str, ...] = field(default_factory=tuple)
    anti_affinity_resources: Tuple[str, ...] = field(default_factory=tuple)


class ReservationDecisionType(Enum):
    """Types of reservation decisions."""
    GRANT = "grant"                # Request granted
    PARTIAL = "partial"            # Partial grant (some quantity)
    DEFER = "defer"                # Defer decision
    REJECT_CAPACITY = "reject_capacity"
    REJECT_DEADLINE = "reject_deadline"
    REJECT_POLICY = "reject_policy"


@dataclass(frozen=True)
class ReservationDecision:
    """
    Decision on a reservation request.
    
    This is the OUTPUT - an immutable record of what was decided.
    """
    decision_type: ReservationDecisionType
    reservation_id: Optional[str] = None
    
    # For partial grants
    granted_quantity: Optional[float] = None
    
    # Rejection reasons
    rejection_reason: Optional[str] = None
    
    # Decision context
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create_grant(cls, reservation_id: str) -> "ReservationDecision":
        """Create a grant decision."""
        return cls(
            decision_type=ReservationDecisionType.GRANT,
            reservation_id=reservation_id,
        )
    
    @classmethod
    def create_partial(cls, reservation_id: str, granted_quantity: float) -> "ReservationDecision":
        """Create a partial grant decision."""
        return cls(
            decision_type=ReservationDecisionType.PARTIAL,
            reservation_id=reservation_id,
            granted_quantity=granted_quantity,
        )
    
    @classmethod
    def create_defer(cls, reason: str = "") -> "ReservationDecision":
        """Create a defer decision."""
        return cls(
            decision_type=ReservationDecisionType.DEFER,
            rejection_reason=f"Deferred: {reason}" if reason else "Deferred",
        )
    
    @classmethod
    def create_reject_capacity(cls, reason: str) -> "ReservationDecision":
        """Create a capacity rejection."""
        return cls(
            decision_type=ReservationDecisionType.REJECT_CAPACITY,
            rejection_reason=f"No capacity: {reason}",
        )
    
    @classmethod
    def create_reject_deadline(cls, reason: str) -> "ReservationDecision":
        """Create a deadline rejection."""
        return cls(
            decision_type=ReservationDecisionType.REJECT_DEADLINE,
            rejection_reason=f"Cannot meet deadline: {reason}",
        )
    
    @classmethod
    def create_reject_policy(cls, reason: str) -> "ReservationDecision":
        """Create a policy rejection."""
        return cls(
            decision_type=ReservationDecisionType.REJECT_POLICY,
            rejection_reason=f"Policy violation: {reason}",
        )


class ReservationStatus(Enum):
    """Status of an active reservation."""
    PENDING = "pending"           # Requested, not yet granted
    ACTIVE = "active"             # Granted and holding capacity
    EXPIRED = "expired"           # Past expiration
    RELEASED = "released"         # Explicitly released
    CONSUMED = "consumed"         # Converted to allocation


@dataclass(frozen=True)
class Reservation:
    """
    A granted reservation.
    
    This is the canonical record of a reservation that's holding capacity.
    """
    reservation_id: str
    
    runtime_id: str
    owner_id: str
    domain: str
    
    requested_quantity: float
    minimum_quantity: float
    preferred_quantity: float
    
    created_at: float           # When reservation was created
    deadline_utc: Optional[float] = None  # Deadline for the reservation
    expiration_utc: float = 0.0       # When reservation expires (timeout) - default needed for dataclass ordering
    
    priority: int = 0            # For ordering in contention
    status: ReservationStatus = ReservationStatus.ACTIVE
    
    # Source
    source_transaction_id: str = ""
    generation_epoch: int = 1


@dataclass(frozen=True)
class ReservationRelease:
    """Record of a reservation release."""
    reservation_id: str
    released_at_utc: float
    owner_id: str
    reason: str


@dataclass(frozen=True)
class ReservationExpiration:
    """Record of a reservation expiration."""
    reservation_id: str
    expired_at_utc: float
    owner_id: str


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "ReservationRequest",
    "ReservationRequirement",
    "ReservationDecision",
    "ReservationDecisionType",
    "ReservationStatus",
    "Reservation",
    "ReservationRelease",
    "ReservationExpiration",
]