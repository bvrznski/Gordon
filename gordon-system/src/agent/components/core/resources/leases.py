# Core Lease Model
# ================
"""
Immutable lease artifacts with expiration and fencing.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import uuid
import time

# Lease ID type (self-contained for now)
class LeaseId(str):
    """Unique identifier for a lease."""
    
    @classmethod
    def generate(cls) -> "LeaseId":
        return cls(value=f"lease_{uuid.uuid4().hex[:16]}")
    
    @property
    def value(self) -> str:
        return self


@dataclass(frozen=True)
class FencingToken:
    """
    Token for preventing stale owners from using resources.
    
    A lease is only valid if the fencing token matches the current allocation's
    fencing token. This prevents split-brain scenarios where an old owner
    tries to use a resource after ownership has been transferred.
    """
    value: str
    generation: int  # Increments on each ownership change
    
    @classmethod
    def initial(cls) -> "FencingToken":
        """Create an initial fencing token."""
        return cls(value=str(uuid.uuid4()), generation=1)
    
    def next(self) -> "FencingToken":
        """Get the next fencing token (increment generation)."""
        return FencingToken(value=str(uuid.uuid4()), generation=self.generation + 1)


class LeaseStatus(Enum):
    """
    Status of a lease.
    
    Transitions:
        CREATED → ACTIVE → (RENEWING) → RENEWED → ACTIVE
                   ↓
                EXPIRING → EXPIRED
                   ↓
                REVOKING → REVOKED
        
        ACTIVE → RELEASING → RELEASED
    """
    CREATED = "created"           # Lease created but not yet active
    ACTIVE = "active"             # Lease is valid and authorizing use
    RENEWING = "renewing"         # Renewal in progress
    RENEWED = "renewed"           # Successfully renewed
    EXPIRING = "expiring"         # Expiration in progress
    EXPIRED = "expired"           # Lease has expired
    REVOKING = "revoking"         # Revocation in progress
    REVOKED = "revoked"           # Lease was revoked
    RELEASING = "releasing"       # Release in progress
    RELEASED = "released"         # Lease released by owner


@dataclass(frozen=True)
class ResourceLease:
    """
    A time-bound lease on allocated resources.
    
    This is the canonical record of a lease - granting temporary usage rights
    with an expiration and fencing token for split-brain prevention.
    
    Every active use must have an active lease.
    Every lease has exactly one owner.
    Every lease has an expiration.
    """
    lease_id: str
    
    allocation_id: str          # Which allocation this lease is on
    resource_id: Optional[str]  # Specific resource if known
    
    runtime_id: str             # Which runtime owns this
    owner_id: str               # Who can use this resource
    
    generation: int             # For split-brain fencing
    
    created_at_utc: float       # When lease was created
    activated_at_utc: Optional[float] = None  # When lease became active
    expires_at_utc: float = 0.0       # When lease expires (MUST be set! - default for dataclass ordering)
    
    renewal_deadline_utc: Optional[float] = None  # When to start renewing
    maximum_lifetime_seconds: float = 86400.0     # Max total lifetime
    
    status: LeaseStatus = LeaseStatus.CREATED
    
    revocation_policy: str = "graceful"  # graceful or immediate
    
    # Fencing token (prevents stale owners)
    fencing_token: FencingToken = field(default_factory=FencingToken.initial)
    
    # Provenance
    source_transaction_id: str = ""
    
    @property
    def is_active(self) -> bool:
        """Check if lease is currently active."""
        return self.status == LeaseStatus.ACTIVE
    
    @property
    def is_expired(self) -> bool:
        """Check if lease has expired."""
        return time.time() > self.expires_at_utc
    
    @property
    def remaining_seconds(self) -> float:
        """Get remaining lifetime in seconds (can be negative)."""
        return self.expires_at_utc - time.time()
    
    def is_fencing_token_valid(self, token: FencingToken) -> bool:
        """
        Check if a fencing token is valid for this lease.
        
        Returns False if token doesn't match or lease has expired.
        """
        if self.is_expired:
            return False
        return token.value == self.fencing_token.value
    
    def can_use(self, owner_id: str, token: FencingToken) -> bool:
        """Check if the lease authorizes use."""
        return (
            self.is_active and
            self.owner_id == owner_id and
            self.is_fencing_token_valid(token)
        )


@dataclass(frozen=True)
class LeaseCreationResult:
    """
    Result of a lease creation request.
    """
    success: bool
    lease: Optional[ResourceLease]
    
    # Failure reason if not successful
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class LeaseRenewalResult:
    """
    Result of a lease renewal request.
    """
    success: bool
    renewed_lease: Optional[ResourceLease]
    
    # New expiration time
    new_expires_at_utc: Optional[float] = None
    
    # Failure reason if not successful
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class LeaseRevocationResult:
    """
    Result of a lease revocation request.
    """
    success: bool
    revoked_lease: Optional[ResourceLease]
    
    # Resources released as part of revocation
    resources_reclaimed: Tuple[str, ...] = field(default_factory=tuple)
    
    # Failure reason if not successful
    failure_reason: Optional[str] = None


# =============================================================================
# Lease Manager - Canonical Authority
# =============================================================================

class LeaseManager:
    """
    Canonical authority for lease operations.
    
    This is THE ONE source of truth for leases. No component may create or
    modify authoritative leases without going through this manager.
    
    Invariants enforced:
        - Every active lease has an owner
        - Every active lease has an expiration
        - Expired leases cannot authorize use
        - Fencing tokens prevent stale owners
        - Leases are bounded in time
    
    Usage:
        # Create lease for an allocation
        result = lease_manager.create_lease(
            allocation=allocation,
            owner_id="task_123",
            duration_seconds=3600.0
        )
        
        if result.success:
            lease = result.lease
            
            # Check before use
            if lease.can_use(owner_id, fencing_token):
                # Use the resource...
                
            # Renew before expiration
            renewal = lease_manager.renew_lease(lease)
    """
    
    def __init__(
        self,
        runtime_id: str,
        capacity_snapshot_fn=None  # Function that returns CapacitySnapshot
    ):
        self._runtime_id = runtime_id
        self._capacity_snapshot_fn = capacity_snapshot_fn or (lambda: None)
        
        self._lock = __import__("threading").RLock()
        
        # Lease storage
        self._leases_by_id: Dict[str, ResourceLease] = {}
        self._leases_by_allocation: Dict[str, List[ResourceLease]] = {}
        
        # Lease counter for IDs
        self._lease_counter = 0
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this manager serves."""
        return self._runtime_id
    
    @property
    def lease_count(self) -> int:
        """Get count of active leases."""
        with self._lock:
            return len(self._leases_by_id)
    
    def create_lease(
        self,
        allocation: "Allocation",  # Forward reference, used from allocations module
        owner_id: str,
        duration_seconds: float
    ) -> Tuple[bool, ResourceLease]:
        """
        Create a new lease for an allocation.
        
        Args:
            allocation: The allocated resource
            owner_id: Who will own this lease
            duration_seconds: How long the lease is valid
            
        Returns:
            Tuple of (success, lease)
        """
        with self._lock:
            # Validate runtime scope
            if allocation.runtime_id != self._runtime_id:
                return False, ResourceLease(
                    lease_id="invalid",
                    allocation_id=allocation.allocation_id,
                    runtime_id=self._runtime_id,
                    owner_id=owner_id,
                    generation=0,
                    created_at_utc=time.time(),
                    expires_at_utc=time.time() - 1,  # Already expired
                )
            
            # Generate lease ID
            self._lease_counter += 1
            lease_id = f"lease_{self._lease_counter:08d}"
            
            now = time.time()
            lease = ResourceLease(
                lease_id=lease_id,
                allocation_id=allocation.allocation_id,
                resource_id=allocation.resource_ids[0] if allocation.resource_ids else None,
                runtime_id=self._runtime_id,
                owner_id=owner_id,
                generation=allocation.generation_epoch if hasattr(allocation, 'generation_epoch') else 1,
                created_at_utc=now,
                activated_at_utc=None,  # Will be set when lease is used
                expires_at_utc=now + duration_seconds,
                renewal_deadline_utc=now + (duration_seconds * 0.7),  # Renew at 70%
                maximum_lifetime_seconds=duration_seconds,
            )
            
            self._leases_by_id[lease_id] = lease
            
            if allocation.allocation_id not in self._leases_by_allocation:
                self._leases_by_allocation[allocation.allocation_id] = []
            self._leases_by_allocation[allocation.allocation_id].append(lease)
            
            return True, lease
    
    def activate_lease(self, lease: ResourceLease) -> bool:
        """
        Mark a created lease as active.
        
        Returns True if activation was successful.
        """
        with self._lock:
            if lease.lease_id not in self._leases_by_id:
                return False
            
            current = self._leases_by_id[lease.lease_id]
            
            # Only CREATED leases can be activated
            if current.status != LeaseStatus.CREATED:
                return False
            
            # Update activation time
            updated = dataclass_replace(
                current,
                status=LeaseStatus.ACTIVE,
                activated_at_utc=time.time(),
            )
            
            self._leases_by_id[lease.lease_id] = updated
            return True
    
    def renew_lease(self, lease: ResourceLease) -> Tuple[bool, ResourceLease]:
        """
        Renew an active lease.
        
        Returns:
            Tuple of (success, renewed_lease)
        """
        with self._lock:
            if lease.lease_id not in self._leases_by_id:
                return False, lease
            
            current = self._leases_by_id[lease.lease_id]
            
            # Must be active to renew
            if current.status != LeaseStatus.ACTIVE:
                return False, current
            
            # Check renewal deadline
            now = time.time()
            if current.renewal_deadline_utc and now > current.renewal_deadline_utc:
                return False, current
            
            # Check maximum lifetime not exceeded
            elapsed = now - current.created_at_utc
            if elapsed + 3600.0 > current.maximum_lifetime_seconds:  # Allow one renewal
                return False, current
            
            # Create renewed lease with new expiration
            new_expires = now + (current.expires_at_utc - now)  # Extend by same duration
            
            updated = dataclass_replace(
                current,
                status=LeaseStatus.RENEWED,
                expires_at_utc=new_expires,
                renewal_deadline_utc=new_expires * 0.7,  # New renewal deadline
            )
            
            self._leases_by_id[lease.lease_id] = updated
            
            return True, updated
    
    def revoke_lease(
        self,
        lease: ResourceLease,
        reason: str = ""
    ) -> Tuple[bool, ResourceLease]:
        """
        Revoke a lease (preemption or failure recovery).
        
        Returns:
            Tuple of (success, lease_after_action)
        """
        with self._lock:
            if lease.lease_id not in self._leases_by_id:
                return False, lease
            
            current = self._leases_by_id[lease.lease_id]
            
            # Update status
            updated = dataclass_replace(
                current,
                status=LeaseStatus.REVOKED,
            )
            
            self._leases_by_id[lease.lease_id] = updated
            
            return True, updated
    
    def release_lease(self, lease: ResourceLease) -> bool:
        """
        Release a lease (normal path).
        
        Returns True if released.
        """
        with self._lock:
            if lease.lease_id not in self._leases_by_id:
                return False
            
            current = self._leases_by_id[lease.lease_id]
            
            # Update status
            updated = dataclass_replace(
                current,
                status=LeaseStatus.RELEASED,
            )
            
            self._leases_by_id[lease.lease_id] = updated
            
            # Clean up from allocation mapping
            if current.allocation_id in self._leases_by_allocation:
                self._leases_by_allocation[current.allocation_id] = [
                    l for l in self._leases_by_allocation[current.allocation_id]
                    if l.lease_id != lease.lease_id
                ]
            
            return True
    
    def get_active_leases_for_resource(self, resource_id: str) -> List[str]:
        """Get active lease IDs for a specific resource."""
        with self._lock:
            result = []
            for lease in self._leases_by_id.values():
                if (
                    lease.status == LeaseStatus.ACTIVE and
                    lease.resource_id == resource_id
                ):
                    result.append(lease.lease_id)
            return result
    
    def get_active_leases(self) -> List[ResourceLease]:
        """Get all active leases."""
        with self._lock:
            return [
                l for l in self._leases_by_id.values()
                if l.status == LeaseStatus.ACTIVE
            ]
    
    def get_lease(self, lease_id: str) -> Optional[ResourceLease]:
        """Get a lease by ID."""
        with self._lock:
            return self._leases_by_id.get(lease_id)


# =============================================================================
# Utility functions
# =============================================================================

def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "FencingToken",
    "LeaseStatus",
    "ResourceLease",
    "LeaseCreationResult",
    "LeaseRenewalResult",
    "LeaseRevocationResult",
    "LeaseManager",
]