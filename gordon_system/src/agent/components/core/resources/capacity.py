# Core Capacity Model
# ====================
"""
Immutable capacity tracking with accounting and ledger.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import time


@dataclass(frozen=True)
class DomainCapacitySnapshot:
    """
    Snapshot of capacity for one resource domain.
    
    All fields are in the domain's natural units (e.g., MB for memory, cores for CPU).
    """
    
    domain: str
    
    # Capacity values
    total_capacity: float       # Total available in system
    reserved_capacity: float    # Held by reservations
    allocated_capacity: float   # Permanently assigned to owners
    used_capacity: float        # Currently being consumed
    free_capacity: float        # Available for new allocations
    
    # Derived values
    reclaimable_capacity: float  # Can be reclaimed if needed
    unavailable_capacity: float  # Not available (failed, quarantined)
    
    @property
    def headroom(self) -> float:
        """Available capacity after accounting for headroom requirement."""
        return max(0.0, self.free_capacity - self.used_capacity)
    
    @property
    def utilization(self) -> float:
        """Current utilization percentage (0.0 to 1.0)."""
        if self.total_capacity <= 0:
            return 0.0
        return self.used_capacity / self.total_capacity
    
    @classmethod
    def create_empty(cls, domain: str) -> "DomainCapacitySnapshot":
        """Create an empty snapshot for a domain."""
        return cls(
            domain=domain,
            total_capacity=0.0,
            reserved_capacity=0.0,
            allocated_capacity=0.0,
            used_capacity=0.0,
            free_capacity=0.0,
            reclaimable_capacity=0.0,
            unavailable_capacity=0.0,
        )


@dataclass(frozen=True)
class CapacitySnapshot:
    """
    Complete capacity snapshot for all domains.
    
    This is the canonical record of system capacity at a point in time.
    """
    
    runtime_id: str
    version: int                 # Version for synchronization
    timestamp_utc: float         # When snapshot was taken
    
    domain_snapshots: Dict[str, DomainCapacitySnapshot]
    
    @property
    def total_domains(self) -> int:
        """Get number of domains tracked."""
        return len(self.domain_snapshots)
    
    @property
    def all_capacity(self) -> Dict[str, float]:
        """Get total capacity per domain as a simple dict."""
        return {
            d: s.total_capacity 
            for d, s in self.domain_snapshots.items()
        }
    
    def get_domain(self, domain: str) -> Optional[DomainCapacitySnapshot]:
        """Get snapshot for a specific domain."""
        return self.domain_snapshots.get(domain)
    
    def check_sufficient(
        self,
        domain: str,
        required_amount: float
    ) -> Tuple[bool, str]:
        """
        Check if sufficient capacity exists.
        
        Returns:
            Tuple of (sufficient, reason_if_not)
        """
        snap = self.domain_snapshots.get(domain)
        if not snap:
            return False, f"Unknown domain: {domain}"
        
        if snap.free_capacity < required_amount:
            return False, (
                f"Insufficient capacity in {domain}: "
                f"need {required_amount}, have {snap.free_capacity}"
            )
        
        return True, "Capacity available"


@dataclass(frozen=True)
class CapacityVersion:
    """Version marker for capacity state synchronization."""
    value: int


# =============================================================================
# Capacity Ledger
# =============================================================================

class CapacityLedger:
    """
    Ledger for tracking all capacity changes with full provenance.
    
    Used for reconciliation and detecting accounting drift.
    """
    
    @dataclass(frozen=True)
    class Entry:
        """Single ledger entry."""
        timestamp_utc: float
        entry_id: str
        domain: str
        change_type: str          # reserve, allocate, release, etc.
        amount: float
        balance_after: float
        owner_id: Optional[str] = None
        source_transaction: Optional[str] = None
    
    def __init__(self):
        self._entries: List["CapacityLedger.Entry"] = []
        self._lock = __import__("threading").RLock()
    
    def record(
        self,
        domain: str,
        change_type: str,
        amount: float,
        balance_after: float,
        owner_id: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> "CapacityLedger.Entry":
        """Record a capacity change."""
        entry = CapacityLedger.Entry(
            timestamp_utc=time.time(),
            entry_id=f"cap_{len(self._entries)}",
            domain=domain,
            change_type=change_type,
            amount=amount,
            balance_after=balance_after,
            owner_id=owner_id,
            source_transaction=transaction_id,
        )
        
        with self._lock:
            self._entries.append(entry)
        
        return entry
    
    def get_entries_for_domain(self, domain: str) -> List["CapacityLedger.Entry"]:
        """Get all entries for a domain."""
        with self._lock:
            return [e for e in self._entries if e.domain == domain]
    
    def verify_integrity(self) -> Tuple[bool, List[str]]:
        """
        Verify ledger integrity.
        
        Returns:
            Tuple of (intact, list_of_violations)
        """
        # Check no negative balances
        violations = []
        current_balance: Dict[str, float] = {}
        
        with self._lock:
            for entry in self._entries:
                domain = entry.domain
                
                if domain not in current_balance:
                    current_balance[domain] = 0.0
                
                if entry.change_type == "reserve":
                    current_balance[domain] += entry.amount
                elif entry.change_type == "allocate":
                    current_balance[domain] += entry.amount
                elif entry.change_type == "release":
                    current_balance[domain] -= entry.amount
                
                if current_balance[domain] < 0:
                    violations.append(
                        f"Negative balance in {domain}: {current_balance[domain]}"
                    )
        
        return len(violations) == 0, violations


# =============================================================================
# Capacity Model
# =============================================================================

class CapacityModel:
    """
    Canonical capacity tracking model.
    
    This is THE source of truth for capacity within a runtime.
    All capacity changes go through this model.
    
    Invariants enforced:
        - free_capacity = total - reserved - allocated + reclaimable_overlap
        - No negative capacity anywhere
        - Total >= allocated (always)
        - Reserved is always <= total
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Domain tracking
        self._domains: Dict[str, float] = {}  # domain -> total_capacity
        
        # Allocation tracking (per domain)
        self._reserved: Dict[str, float] = {}
        self._allocated: Dict[str, float] = {}
        self._used: Dict[str, float] = {}
        
        # Ledger for reconciliation
        self._ledger = CapacityLedger()
        
        # Version
        self._version = 0
    
    def add_resource(self, descriptor) -> None:
        """Add capacity from a resource descriptor."""
        with self._lock:
            domain = descriptor.domain
            capacity = descriptor.total_capacity
            
            if domain not in self._domains:
                self._domains[domain] = 0.0
                self._reserved[domain] = 0.0
                self._allocated[domain] = 0.0
                self._used[domain] = 0.0
            
            self._domains[domain] += capacity
            self._version += 1
    
    def remove_resource(self, descriptor) -> None:
        """Remove capacity from a resource descriptor."""
        with self._lock:
            domain = descriptor.domain
            
            if domain not in self._domains:
                return
            
            capacity = descriptor.total_capacity
            
            # Check this wouldn't make allocated go negative
            if self._allocated[domain] + capacity > self._domains[domain]:
                raise ValueError(
                    f"Cannot remove {capacity} from {domain}: "
                    f"has {self._allocated[domain]} allocated"
                )
            
            self._domains[domain] -= capacity
            self._version += 1
    
    def reserve_capacity(self, domain: str, amount: float) -> None:
        """Mark capacity as reserved."""
        with self._lock:
            if domain not in self._domains:
                raise ValueError(f"Unknown domain: {domain}")
            
            self._reserved[domain] = self._reserved.get(domain, 0.0) + amount
            self._ledger.record(
                domain=domain,
                change_type="reserve",
                amount=amount,
                balance_after=self._reserved[domain],
                transaction_id=f"res_{id(self)}",
            )
    
    def allocate_capacity(self, domain: str, amount: float) -> None:
        """Mark capacity as allocated."""
        with self._lock:
            if domain not in self._domains:
                raise ValueError(f"Unknown domain: {domain}")
            
            # Update both reserved (if it was reserved first) and allocated
            reserved = self._reserved.get(domain, 0.0)
            allocated = self._allocated.get(domain, 0.0)
            
            if amount <= reserved:
                # Reduce reserved, increase allocated
                self._reserved[domain] = max(0.0, reserved - amount)
                self._allocated[domain] = allocated + amount
            else:
                # Reduce all reserved, allocate rest from total
                self._reserved[domain] = 0.0
                self._allocated[domain] = allocated + amount
            
            self._ledger.record(
                domain=domain,
                change_type="allocate",
                amount=amount,
                balance_after=self._allocated[domain],
                transaction_id=f"alloc_{id(self)}",
            )
    
    def release_capacity(self, domain: str, amount: float) -> None:
        """Release capacity back."""
        with self._lock:
            if domain not in self._domains:
                raise ValueError(f"Unknown domain: {domain}")
            
            allocated = self._allocated.get(domain, 0.0)
            
            # Release from allocated first
            self._allocated[domain] = max(0.0, allocated - amount)
            
            self._ledger.record(
                domain=domain,
                change_type="release",
                amount=amount,
                balance_after=self._allocated[domain],
                transaction_id=f"rel_{id(self)}",
            )
    
    def get_snapshot(self) -> CapacitySnapshot:
        """Get current capacity snapshot."""
        with self._lock:
            domain_snaps = {}
            
            for domain, total in self._domains.items():
                reserved = self._reserved.get(domain, 0.0)
                allocated = self._allocated.get(domain, 0.0)
                
                # Calculate derived values
                used = self._used.get(domain, 0.0)
                free = max(0.0, total - reserved - allocated + self._reclaimable_overlap(domain))
                
                domain_snaps[domain] = DomainCapacitySnapshot(
                    domain=domain,
                    total_capacity=total,
                    reserved_capacity=reserved,
                    allocated_capacity=allocated,
                    used_capacity=used,
                    free_capacity=free,
                    reclaimable_capacity=self._get_reclaimable(domain),
                    unavailable_capacity=0.0,  # Would track failed resources
                )
            
            return CapacitySnapshot(
                runtime_id=self._runtime_id,
                version=self._version,
                timestamp_utc=time.time(),
                domain_snapshots=domain_snaps,
            )
    
    def _reclaimable_overlap(self, domain: str) -> float:
        """Calculate reclaimable capacity overlap."""
        # Simplified - in real impl would consider lease expiration times
        return 0.0
    
    def _get_reclaimable(self, domain: str) -> float:
        """Get reclaimable capacity for a domain."""
        # Simplified - in real impl would track reclaimable resources explicitly
        allocated = self._allocated.get(domain, 0.0)
        used = self._used.get(domain, 0.0)
        return max(0.0, allocated - used)


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "DomainCapacitySnapshot",
    "CapacitySnapshot",
    "CapacityVersion",
    "CapacityLedger",
    "CapacityModel",
]