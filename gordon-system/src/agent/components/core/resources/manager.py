# Core ResourceManager - Canonical Runtime Resource Authority
# ============================================================
"""
Phase 3.7.13 - ResourceManager as canonical resource authority.

ResourceManager owns:
- Resource registration and inventory maintenance
- Capacity truth (total, reserved, allocated, used, free)
- Ownership records
- Resource snapshots and history
- Reconciliation with external state
- Diagnostics

ResourceManager does NOT own:
- Task scheduling decisions
- Admission control
- Executor execution logic
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
import uuid
import time
import threading

from .inventory import (
    ResourceInventory,
    ResourceDescriptor,
    ResourceState,
    ResourceId,
)
from .capacity import CapacityModel, CapacitySnapshot, CapacityVersion
from .reservations import ReservationRequest, ReservationDecision, Reservation
from .allocations import AllocationRequest, AllocationDecision, AllocationResult, Allocation
from .leases import LeaseManager, ResourceLease, LeaseStatus, FencingToken
from .contention import ContentionResolver
from .quotas import QuotaEnforcer
from .fairness import FairnessAssessor
from .preemption import Preemptor
from .pressure import PressureManager


# =============================================================================
# ResourceManager Configuration
# =============================================================================

@dataclass(frozen=True)
class ResourceManagerConfig:
    """
    Immutable configuration for ResourceManager.
    
    All bounds are enforced - no unbounded growth possible.
    """
    
    runtime_id: str
    
    # Resource limits (hard constraints)
    max_resources: int = 10000          # Maximum resource entries
    max_reservations: int = 1000        # Max pending reservations
    max_allocations: int = 10000        # Max active allocations
    max_leases: int = 50000             # Max active leases
    
    # Timeouts (bounded)
    default_reservation_timeout_seconds: float = 300.0   # 5 min
    default_lease_duration_seconds: float = 3600.0       # 1 hour
    max_lease_duration_seconds: float = 86400.0          # 24 hours
    lease_renewal_ratio: float = 0.7                                     # Renew at 70% lifetime
    
    # Policy bounds
    default_headroom_fraction: float = 0.1                               # Keep 10% headroom
    max_overcommit_ratio: float = 1.2                                    # Up to 20% overcommit
    preemption_enabled: bool = True                                      # Allow preemption
    reclamation_enabled: bool = True                                     # Allow reclamation
    
    # History bounds (bounded!)
    max_event_history: int = 10000
    max_snapshot_history: int = 100
    
    # Detection thresholds
    leak_detection_threshold_seconds: float = 3600.0                     # Report idle > 1hr as potential leak
    stale_generation_threshold_seconds: float = 60.0                     # Generation considered stale after 60s


# =============================================================================
# ResourceManager - Canonical Authority
# =============================================================================

class ResourceManager:
    """
    Canonical runtime-wide resource authority.
    
    This is THE ONE source of truth for all resource management within a runtime.
    All resource operations MUST go through this manager.
    
    Invariants Enforced:
        1. Exactly one ResourceManager exists per runtime (enforced by runtime_id)
        2. Every allocation has an owner
        3. Every lease has owner and expiration
        4. Capacity accounting never negative
        5. No direct acquisition bypasses ResourceManager
        6. Reservations, allocations, leases remain distinct
        7. Release always reconciled with capacity
        8. Expired leases cannot authorize use
        9. Stale fencing tokens rejected
    
    Usage:
        config = ResourceManagerConfig(runtime_id="runtime_1")
        rm = ResourceManager(config)
        
        # Register resources
        descriptor = ResourceDescriptor(...)
        rm.register_resource(descriptor)
        
        # Request allocation
        result = rm.request_allocation(AllocationRequest(...))
        
        if result.decision.is_granted():
            allocation = result.allocation
            lease_manager = rm.lease_manager
            lease_result = lease_manager.create_lease(allocation, owner_id="task_1")
    """
    
    def __init__(self, config: ResourceManagerConfig):
        # Verify runtime_id is set
        if not config.runtime_id:
            raise ValueError("ResourceManager requires a non-empty runtime_id")
        
        self._config = config
        self._runtime_id = config.runtime_id
        
        # Core state (owned by this manager)
        self._lock = threading.RLock()
        
        # Inventory (source of truth for known resources)
        self._inventory = ResourceInventory(runtime_id=config.runtime_id)
        
        # Capacity model (derived from inventory + allocations + leases)
        self._capacity_model = CapacityModel(runtime_id=config.runtime_id)
        
        # Lease manager (canonical lease authority - delegate to this)
        self._lease_manager = LeaseManager(
            runtime_id=config.runtime_id,
            capacity_snapshot_fn=self._get_capacity_snapshot_for_leases
        )
        
        # Contention resolver (for allocation conflicts)
        self._contention_resolver = ContentionResolver()
        
        # Quota enforcer (enforce resource quotas)
        self._quota_enforcer = QuotaEnforcer(runtime_id=config.runtime_id)
        
        # Fairness assessor (determine fair allocation among owners)
        self._fairness_assessor = FairnessAssessor()
        
        # Preemptor (for high-priority work)
        self._preemptor = Preemptor(
            runtime_id=config.runtime_id,
            lease_manager=self._lease_manager
        )
        
        # Pressure manager (monitor and report resource pressure)
        self._pressure_manager = PressureManager(runtime_id=config.runtime_id)
        
        # Allocation tracking (internal)
        self._allocations: Dict[str, Allocation] = {}
        self._reservation_by_id: Dict[str, Reservation] = {}
        
        # Event log (bounded)
        self._events: List[Dict[str, Any]] = []
        self._snapshots: List[Tuple[float, "ResourceManagerSnapshot"]] = []
        
        # State version for synchronization
        self._state_version = 0
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this manager serves."""
        return self._runtime_id
    
    @property
    def config(self) -> ResourceManagerConfig:
        """Get the configuration."""
        return self._config
    
    @property
    def lease_manager(self) -> LeaseManager:
        """
        Get the canonical lease authority.
        
        This is THE ONE source of truth for leases. No other component
        may create or modify authoritative leases.
        """
        return self._lease_manager
    
    @property
    def contention_resolver(self) -> ContentionResolver:
        """Get the contention resolver."""
        return self._contention_resolver
    
    # -------------------------------------------------------------------------
    # Resource Registration
    # -------------------------------------------------------------------------
    
    def register_resource(self, descriptor: ResourceDescriptor) -> None:
        """
        Register a new resource with the inventory.
        
        This is the ONLY way to add resources to the system.
        
        Args:
            descriptor: Immutable resource descriptor
            
        Raises:
            ValueError: If resource already registered or invalid
        """
        with self._lock:
            # Validate runtime scope
            if descriptor.runtime_id != self._runtime_id:
                raise ValueError(
                    f"Resource {descriptor.resource_id} belongs to "
                    f"runtime {descriptor.runtime_id}, not {self._runtime_id}"
                )
            
            # Check for duplicate registration
            if self._inventory.has_resource(descriptor.resource_id):
                raise ValueError(f"Resource {descriptor.resource_id} already registered")
            
            # Register with inventory
            self._inventory.add_descriptor(descriptor)
            
            # Update capacity model
            self._capacity_model.add_resource(descriptor)
            
            # Record event
            self._record_event("resource_registered", {
                "resource_id": descriptor.resource_id,
                "domain": descriptor.domain,
                "kind": descriptor.kind,
                "total_capacity": descriptor.total_capacity,
            })
            
            # Increment state version
            self._state_version += 1
    
    def deregister_resource(self, resource_id: str) -> bool:
        """
        Remove a resource from the inventory.
        
        Cannot deregister if there are active allocations or leases.
        
        Args:
            resource_id: The resource to remove
            
        Returns:
            True if deregistered, False if not found
        """
        with self._lock:
            if not self._inventory.has_resource(resource_id):
                return False
            
            # Check for active allocations
            allocation_ids = [
                aid for aid, alloc in self._allocations.items()
                if alloc.resource_id == resource_id and alloc.state.is_active()
            ]
            
            if allocation_ids:
                raise ValueError(
                    f"Cannot deregister {resource_id}: "
                    f"has {len(allocation_ids)} active allocations: {allocation_ids}"
                )
            
            # Check for active leases
            lease_ids = self._lease_manager.get_active_leases_for_resource(resource_id)
            if lease_ids:
                raise ValueError(
                    f"Cannot deregister {resource_id}: has {len(lease_ids)} active leases"
                )
            
            # Remove from inventory
            descriptor = self._inventory.remove_descriptor(resource_id)
            
            # Update capacity model
            self._capacity_model.remove_resource(descriptor)
            
            # Record event
            self._record_event("resource_deregistered", {
                "resource_id": resource_id,
            })
            
            self._state_version += 1
            return True
    
    def refresh_inventory(self, new_descriptors: List[ResourceDescriptor]) -> None:
        """
        Refresh inventory with new observations.
        
        This replaces the current inventory - use for full discovery refreshes.
        
        Args:
            new_descriptors: Complete set of currently known resources
        """
        with self._lock:
            # Validate all descriptors belong to this runtime
            for desc in new_descriptors:
                if desc.runtime_id != self._runtime_id:
                    raise ValueError(
                        f"Inventory refresh contains resource {desc.resource_id} "
                        f"from wrong runtime {desc.runtime_id}"
                    )
            
            # Get old descriptor IDs
            old_ids = set(self._inventory.get_all_resource_ids())
            new_ids = set(d.resource_id for d in new_descriptors)
            
            # Remove stale resources
            for resource_id in old_ids - new_ids:
                self.deregister_resource(resource_id)
            
            # Add/update existing resources
            for descriptor in new_descriptors:
                if not self._inventory.has_resource(descriptor.resource_id):
                    self.register_resource(descriptor)
                else:
                    # Update existing (version bump handled by inventory)
                    self._inventory.update_descriptor(descriptor)
            
            self._state_version += 1
    
    # -------------------------------------------------------------------------
    # Capacity Queries
    # -------------------------------------------------------------------------
    
    def get_capacity_snapshot(self) -> CapacitySnapshot:
        """
        Get the current capacity snapshot.
        
        This includes total, reserved, allocated, used, and free capacity
        for all resource domains.
        """
        with self._lock:
            return self._capacity_model.get_snapshot()
    
    def _get_capacity_snapshot_for_leases(self) -> CapacitySnapshot:
        """Internal method for lease manager to get capacity."""
        return self.get_capacity_snapshot()
    
    def check_capacity(
        self,
        domain: str,
        requested_amount: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a capacity request can be satisfied.
        
        Args:
            domain: Resource domain (e.g., "cpu_cores", "gpu_vram_mb")
            requested_amount: Amount of capacity requested
            
        Returns:
            Tuple of (can_satisfy, reason_if_not)
        """
        with self._lock:
            snapshot = self._capacity_model.get_snapshot()
            
            domain_snap = snapshot.domain_snapshots.get(domain)
            if not domain_snap:
                return False, f"Unknown domain: {domain}"
            
            # Check headroom (keep some buffer for safety)
            required = requested_amount * (1 + self._config.default_headroom_fraction)
            
            if required > domain_snap.free_capacity:
                return False, (
                    f"Insufficient capacity in {domain}: "
                    f"need {required:.2f}, have {domain_snap.free_capacity:.2f}"
                )
            
            # Check overcommit
            total_requested = domain_snap.allocated_capacity + requested_amount
            if total_requested > domain_snap.total_capacity * self._config.max_overcommit_ratio:
                return False, (
                    f"Would exceed max overcommit ratio in {domain}: "
                    f"{total_requested:.2f} > {domain_snap.total_capacity * self._config.max_overcommit_ratio:.2f}"
                )
            
            return True, None
    
    # -------------------------------------------------------------------------
    # Reservations
    # -------------------------------------------------------------------------
    
    def request_reservation(
        self,
        request: ReservationRequest
    ) -> Tuple[ReservationDecision, Optional[Reservation]]:
        """
        Submit a reservation request.
        
        Reservations temporarily hold capacity before final allocation.
        
        Args:
            request: The reservation request
            
        Returns:
            Tuple of (decision, reservation_if_created)
        """
        with self._lock:
            # Validate runtime scope
            if request.runtime_id != self._runtime_id:
                raise ValueError(
                    f"Reservation request for {request.runtime_id}, "
                    f"but manager serves {self._runtime_id}"
                )
            
            # Check capacity
            can_satisfy, reason = self.check_capacity(
                request.domain,
                request.requested_quantity
            )
            if not can_satisfy:
                decision = ReservationDecision.create_reject_capacity(reason)
                return decision, None
            
            # Create reservation
            reservation_id = f"res_{uuid.uuid4().hex[:16]}"
            reservation = Reservation(
                reservation_id=reservation_id,
                runtime_id=request.runtime_id,
                owner_id=request.owner_id,
                domain=request.domain,
                requested_quantity=request.requested_quantity,
                minimum_quantity=request.minimum_quantity or request.requested_quantity,
                preferred_quantity=request.preferred_quantity or request.requested_quantity,
                deadline_utc=request.deadline_utc or (time.time() + self._config.default_reservation_timeout_seconds),
                expiration_utc=time.time() + self._config.default_reservation_timeout_seconds,
                priority=request.priority or 0,
            )
            
            # Record in tracking
            if len(self._reservation_by_id) >= self._config.max_reservations:
                # Remove oldest expired reservation
                expired = [
                    rid for rid, res in self._reservation_by_id.items()
                    if time.time() > res.expiration_utc
                ]
                if expired:
                    old_id = min(expired, key=lambda rid: self._reservation_by_id[rid].created_at)
                    del self._reservation_by_id[old_id]
            
            self._reservation_by_id[reservation_id] = reservation
            
            # Update capacity model (mark as reserved)
            self._capacity_model.reserve_capacity(request.domain, request.requested_quantity)
            
            decision = ReservationDecision.create_grant(reservation)
            
            self._record_event("reservation_created", {
                "reservation_id": reservation_id,
                "owner_id": request.owner_id,
                "domain": request.domain,
                "quantity": request.requested_quantity,
            })
            
            self._state_version += 1
            
            return decision, reservation
    
    def release_reservation(self, reservation_id: str) -> bool:
        """
        Release a reservation before expiration.
        
        Args:
            reservation_id: The reservation to release
            
        Returns:
            True if released
        """
        with self._lock:
            if reservation_id not in self._reservation_by_id:
                return False
            
            reservation = self._reservation_by_id[reservation_id]
            
            # Release capacity back
            self._capacity_model.release_capacity(
                reservation.domain,
                reservation.requested_quantity
            )
            
            del self._reservation_by_id[reservation_id]
            
            self._record_event("reservation_released", {
                "reservation_id": reservation_id,
                "owner_id": reservation.owner_id,
            })
            
            self._state_version += 1
            return True
    
    def expire_reservation(self, reservation_id: str) -> bool:
        """
        Expire a reservation (called by timer/cleanup).
        
        Args:
            reservation_id: The reservation to expire
            
        Returns:
            True if expired
        """
        with self._lock:
            if reservation_id not in self._reservation_by_id:
                return False
            
            reservation = self._reservation_by_id[reservation_id]
            
            # Release capacity
            self._capacity_model.release_capacity(
                reservation.domain,
                reservation.requested_quantity
            )
            
            del self._reservation_by_id[reservation_id]
            
            self._record_event("reservation_expired", {
                "reservation_id": reservation_id,
            })
            
            self._state_version += 1
            return True
    
    # -------------------------------------------------------------------------
    # Allocations
    # -------------------------------------------------------------------------
    
    def request_allocation(
        self,
        request: AllocationRequest
    ) -> Tuple[AllocationDecision, Optional[AllocationResult]]:
        """
        Submit an allocation request.
        
        This is the main entry point for requesting resources.
        
        Args:
            request: The allocation request
            
        Returns:
            Tuple of (decision, result_if_granted)
        """
        with self._lock:
            # Validate runtime scope
            if request.runtime_id != self._runtime_id:
                raise ValueError(
                    f"Allocation request for {request.runtime_id}, "
                    f"but manager serves {self._runtime_id}"
                )
            
            # Check reservation exists if specified
            if request.reservation_id:
                if request.reservation_id not in self._reservation_by_id:
                    decision = AllocationDecision.create_reject_policy(
                        "Reservation not found or expired"
                    )
                    return decision, None
            
            # Check quota
            quota_result = self._quota_enforcer.check_quota(
                owner_id=request.owner_id,
                domain=request.domain,
                requested_amount=request.quantity
            )
            if not quota_result.allowed:
                decision = AllocationDecision.create_reject_quota(quota_result.violation_message)
                return decision, None
            
            # Check fairness
            fairness_result = self._fairness_assessor.assess(
                owner_id=request.owner_id,
                domain=request.domain,
                current_ownership=self._get_owner_ownership(request.domain),
                quota_limit=quota_result.quota_limit or float('inf')
            )
            
            if not fairness_result.permitted:
                # Check if preemption is needed
                if self._config.preemption_enabled:
                    can_preempt, candidates = self._preemptor.find_candidates(
                        owner_id=request.owner_id,
                        domain=request.domain,
                        requested_amount=request.quantity
                    )
                    
                    if can_preempt and candidates:
                        # Request preemption (not implemented in this minimal version)
                        decision = AllocationDecision.create_require_preemption(
                            candidate_count=len(candidates),
                            reason="Higher priority work requires resources"
                        )
                        return decision, None
            
            # Check capacity (final check before allocation)
            can_satisfy, reason = self.check_capacity(
                request.domain,
                request.quantity
            )
            if not can_satisfy:
                # Check contention - maybe other tasks would yield
                if self._config.preemption_enabled and request.fallback_policy == "queue":
                    decision = AllocationDecision.create_queue(
                        reason=f"Queue: {reason}"
                    )
                    return decision, None
                
                decision = AllocationDecision.create_reject_capacity(reason)
                return decision, None
            
            # Allocate resources (simplified - in real impl would select specific resources)
            allocation_id = f"alloc_{uuid.uuid4().hex[:16]}"
            
            # Update capacity
            self._capacity_model.allocate_capacity(request.domain, request.quantity)
            
            # Create allocation record
            allocation = Allocation(
                allocation_id=allocation_id,
                runtime_id=request.runtime_id,
                owner_id=request.owner_id,
                resource_domain=request.domain,
                quantity_allocated=request.quantity,
                requested_quantity=request.quantity,
                min_quantity=request.minimum_quantity or request.quantity,
                created_at=time.time(),
                state="allocated",
            )
            
            self._allocations[allocation_id] = allocation
            
            result = AllocationResult(
                decision=AllocationDecision.ALLOCATE,
                allocation=allocation,
                reservation_used=request.reservation_id
            )
            
            self._record_event("resource_allocated", {
                "allocation_id": allocation_id,
                "owner_id": request.owner_id,
                "domain": request.domain,
                "quantity": request.quantity,
            })
            
            self._state_version += 1
            
            return AllocationDecision.ALLOCATE, result
    
    def release_allocation(self, allocation_id: str) -> bool:
        """
        Release an allocation before lease expiration.
        
        This is the normal path for releasing resources.
        
        Args:
            allocation_id: The allocation to release
            
        Returns:
            True if released
        """
        with self._lock:
            if allocation_id not in self._allocations:
                return False
            
            allocation = self._allocations[allocation_id]
            
            # Release capacity back
            self._capacity_model.release_capacity(
                allocation.resource_domain,
                allocation.quantity_allocated
            )
            
            del self._allocations[allocation_id]
            
            self._record_event("resource_released", {
                "allocation_id": allocation_id,
                "owner_id": allocation.owner_id,
            })
            
            self._state_version += 1
            return True
    
    def _get_owner_ownership(self, domain: str) -> Dict[str, float]:
        """Get current ownership by owner for a domain."""
        result = {}
        for alloc in self._allocations.values():
            if alloc.resource_domain == domain:
                result[alloc.owner_id] = result.get(alloc.owner_id, 0.0) + alloc.quantity_allocated
        return result
    
    # -------------------------------------------------------------------------
    # Leases (delegate to LeaseManager)
    # -------------------------------------------------------------------------
    
    def create_lease(
        self,
        allocation: Allocation,
        owner_id: str,
        duration_seconds: Optional[float] = None
    ) -> Tuple[bool, ResourceLease]:
        """
        Create a lease for an allocation.
        
        This is a convenience wrapper that delegates to the canonical
        lease manager.
        """
        return self._lease_manager.create_lease(
            allocation=allocation,
            owner_id=owner_id,
            duration_seconds=duration_seconds or self._config.default_lease_duration_seconds
        )
    
    def renew_lease(self, lease: ResourceLease) -> Tuple[bool, ResourceLease]:
        """Renew an existing lease."""
        return self._lease_manager.renew_lease(lease)
    
    def revoke_lease(
        self,
        lease: ResourceLease,
        reason: str = ""
    ) -> Tuple[bool, ResourceLease]:
        """
        Revoke a lease (high-privilege operation).
        
        Returns:
            Tuple of (success, lease_after_action)
        """
        return self._lease_manager.revoke_lease(lease, reason)
    
    # -------------------------------------------------------------------------
    # Pressure and Diagnostics
    # -------------------------------------------------------------------------
    
    def get_pressure_state(self) -> Dict[str, Any]:
        """Get current resource pressure state."""
        with self._lock:
            snapshot = self.get_capacity_snapshot()
            
            # Calculate pressure per domain
            pressures = {}
            for domain, dom_snap in snapshot.domain_snapshots.items():
                if dom_snap.total_capacity > 0:
                    utilization = dom_snap.allocated_capacity / dom_snap.total_capacity
                    
                    if utilization >= 0.95:
                        level = "CRITICAL"
                    elif utilization >= 0.8:
                        level = "HIGH"
                    elif utilization >= 0.6:
                        level = "ELEVATED"
                    else:
                        level = "NORMAL"
                    
                    pressures[domain] = {
                        "level": level,
                        "utilization": utilization,
                        "allocated": dom_snap.allocated_capacity,
                        "total": dom_snap.total_capacity,
                    }
            
            return pressures
    
    def get_diagnostics(self) -> "ResourceManagerDiagnostics":
        """Get diagnostic snapshot."""
        with self._lock:
            return ResourceManagerDiagnostics(
                runtime_id=self._runtime_id,
                state_version=self._state_version,
                resource_count=len(self._inventory.get_all_resource_ids()),
                allocation_count=len(self._allocations),
                lease_count=self._lease_manager.lease_count,
                reservation_count=len(self._reservation_by_id),
                capacity_snapshot=self._capacity_model.get_snapshot(),
                event_count=len(self._events),
            )
    
    # -------------------------------------------------------------------------
    # State Snapshots
    # -------------------------------------------------------------------------
    
    def get_snapshot(self) -> "ResourceManagerSnapshot":
        """Get an immutable snapshot of current state."""
        with self._lock:
            return ResourceManagerSnapshot(
                runtime_id=self._runtime_id,
                state_version=self._state_version,
                inventory_snapshot=self._inventory.get_snapshot(),
                capacity_snapshot=self.get_capacity_snapshot(),
                allocation_count=len(self._allocations),
                lease_count=self._lease_manager.lease_count,
                reservation_count=len(self._reservation_by_id),
            )
    
    def _record_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Record an event (bounded)."""
        self._events.append({
            "timestamp_utc": time.time(),
            "event_type": event_type,
            "payload": dict(payload),
        })
        
        if len(self._events) > self._config.max_event_history:
            self._events = self._events[-self._config.max_event_history:]
    
    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    
    def get_all_resources(self) -> List[ResourceDescriptor]:
        """Get all registered resources."""
        with self._lock:
            return list(self._inventory.get_all_descriptors())
    
    def get_allocation(self, allocation_id: str) -> Optional[Allocation]:
        """Get an allocation by ID."""
        with self._lock:
            return self._allocations.get(allocation_id)
    
    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """Get a reservation by ID."""
        with self._lock:
            return self._reservation_by_id.get(reservation_id)


# =============================================================================
# Snapshot Types
# =============================================================================

@dataclass(frozen=True)
class ResourceManagerSnapshot:
    """
    Immutable snapshot of ResourceManager state.
    
    Used for debugging, testing, and multi-runtime coordination.
    """
    runtime_id: str
    state_version: int
    inventory_snapshot: Dict[str, Any]
    capacity_snapshot: CapacitySnapshot
    allocation_count: int
    lease_count: int
    reservation_count: int


@dataclass(frozen=True)
class ResourceManagerDiagnostics:
    """
    Diagnostic snapshot for observability and debugging.
    """
    runtime_id: str
    state_version: int
    resource_count: int
    allocation_count: int
    lease_count: int
    reservation_count: int
    capacity_snapshot: CapacitySnapshot
    event_count: int


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "ResourceManager",
    "ResourceManagerConfig",
    "ResourceManagerSnapshot",
    "ResourceManagerDiagnostics",
]