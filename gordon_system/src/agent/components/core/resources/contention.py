# Core Contention Resolution
# ===========================
"""
Resource contention tracking and resolution.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import uuid
import time


@dataclass(frozen=True)
class ContentionKind(Enum):
    """Types of resource contention."""
    INSUFFICIENT_CAPACITY = "insufficient_capacity"
    EXCLUSIVE_CLAIM_CONFLICT = "exclusive_claim_conflict"
    SHARED_CAPACITY_SATURATION = "shared_capacity_saturation"
    QUOTA_CONFLICT = "quota_conflict"
    AFFINITY_CONFLICT = "affinity_conflict"
    ANTI_AFFINITY_CONFLICT = "anti_affinity_conflict"
    DEADLINE_CONFLICT = "deadline_conflict"
    PRIORITY_CONFLICT = "priority_conflict"
    LEASE_CONFLICT = "lease_conflict"
    OWNERSHIP_CONFLICT = "ownership_conflict"
    DEVICE_TOPOLOGY_CONFLICT = "device_topology_conflict"


@dataclass(frozen=True)
class ContentionState:
    """
    Current contention state for a resource domain.
    
    Tracks all pending requests and their relationships.
    """
    domain: str
    queued_count: int                  # Number of waiting requests
    active_contention: List[str]       # Request IDs in contention
    resolved_count: int = 0            # Resolved (granted) count


@dataclass(frozen=True)
class ContentionDecisionType(Enum):
    """Types of contention resolution decisions."""
    GRANT = "grant"                    # Grant the request
    PARTIAL_GRANT = "partial_grant"    # Grant partial quantity
    QUEUE = "queue"                    # Add to queue for later
    DEFER = "defer"                    # Defer decision temporarily
    REJECT = "reject"                  # Reject permanently
    PREEMPT = "preempt"                # Preempt existing work
    RECLAIM = "reclaim"                # Reclaim reclaimed capacity
    FALLBACK = "fallback"              # Use fallback domain
    REQUIRE_OPERATOR = "require_operator"  # Need manual intervention


@dataclass(frozen=True)
class ContentionDecision:
    """
    Decision for a contention resolution.
    
    This is the OUTPUT - an immutable record of how contention was resolved.
    """
    decision_type: ContentionDecisionType
    
    # For granted decisions
    granted_quantity: Optional[float] = None
    selected_resources: Tuple[str, ...] = field(default_factory=tuple)
    
    # Decision context
    evaluated_at_utc: float = field(default_factory=time.time)
    algorithm_id: str = "baseline"
    
    reason: Optional[str] = None


@dataclass(frozen=True)
class ContentionQueueEntry:
    """
    Entry in the contention queue.
    
    Tracks a pending contention request with its metadata.
    """
    entry_id: str
    domain: str
    owner_id: str
    requested_quantity: float
    priority: int
    created_at_utc: float = field(default_factory=time.time)
    
    # Position in queue (for ordering)
    queue_position: int = 0


@dataclass(frozen=True)
class ContentionSnapshot:
    """
    Snapshot of contention state for observability.
    """
    runtime_id: str
    timestamp_utc: float
    
    queued_count: int                  # Total queued requests
    active_contentions: Dict[str, int]  # domain -> count
    resolved_count: int = 0


class ContentionResolver:
    """
    Resolver for resource contention.
    
    When multiple requests compete for the same resources, this component
    determines who wins based on priority, fairness, deadlines, and policy.
    """
    
    def __init__(self, runtime_id: str = "default"):
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Contention queue (priority-sorted)
        self._queue: List[ContentionQueueEntry] = []
        
        # Active contentions per domain
        self._active_contentions: Dict[str, List[str]] = {}
        
        # Statistics
        self._resolved_count = 0
    
    def add_to_queue(
        self,
        owner_id: str,
        domain: str,
        requested_quantity: float,
        priority: int = 0
    ) -> ContentionQueueEntry:
        """
        Add a request to the contention queue.
        
        Returns the queue entry (includes position info).
        """
        with self._lock:
            entry = ContentionQueueEntry(
                entry_id=f"cont_{uuid.uuid4().hex[:12]}",
                domain=domain,
                owner_id=owner_id,
                requested_quantity=requested_quantity,
                priority=priority,
                queue_position=len(self._queue),
            )
            
            self._queue.append(entry)
            
            # Sort by priority (descending) then creation time
            self._queue.sort(
                key=lambda e: (-e.priority, e.created_at_utc)
            )
            
            # Update positions
            for i, e in enumerate(self._queue):
                if e.entry_id == entry.entry_id:
                    self._update_queue_positions()
                    break
            
            return entry
    
    def resolve_contention(
        self,
        domain: str,
        available_capacity: float,
        candidate_requests: List[Tuple[ContentionQueueEntry, float]]  # (entry, requested)
    ) -> ContentionDecision:
        """
        Resolve contention for resources in a domain.
        
        Args:
            domain: Resource domain
            available_capacity: How much is currently available
            candidate_requests: List of (entry, quantity_requested) pairs
            
        Returns:
            Decision on how to resolve
        """
        with self._lock:
            if not candidate_requests:
                return ContentionDecision(
                    decision_type=ContentionDecisionType.DEFER,
                    reason="No candidates",
                )
            
            # Sort by priority
            sorted_candidates = sorted(
                candidate_requests,
                key=lambda x: (-x[0].priority, x[0].created_at_utc)
            )
            
            total_requested = sum(req for _, req in sorted_candidates)
            
            if total_requested <= available_capacity:
                # All can be granted
                self._resolved_count += len(sorted_candidates)
                
                return ContentionDecision(
                    decision_type=ContentionDecisionType.GRANT,
                    granted_quantity=available_capacity,
                    reason="All requests fit within capacity",
                )
            
            # Need to select some candidates - pick highest priority first
            remaining = available_capacity
            granted_entries: List[ContentionQueueEntry] = []
            
            for entry, requested in sorted_candidates:
                if remaining >= requested:
                    granted_entries.append(entry)
                    remaining -= requested
            
            self._resolved_count += len(granted_entries)
            
            if not granted_entries:
                return ContentionDecision(
                    decision_type=ContentionDecisionType.REJECT,
                    reason="No candidates fit within available capacity",
                )
            
            return ContentionDecision(
                decision_type=ContentionDecisionType.PARTIAL_GRANT,
                granted_quantity=available_capacity - remaining,
                reason=f"Granted {len(granted_entries)} of {len(sorted_candidates)} candidates",
            )
    
    def get_queue_snapshot(self) -> ContentionSnapshot:
        """Get current contention state snapshot."""
        with self._lock:
            domain_counts: Dict[str, int] = {}
            for entry in self._queue:
                domain_counts[entry.domain] = domain_counts.get(entry.domain, 0) + 1
            
            return ContentionSnapshot(
                runtime_id=self._runtime_id,
                timestamp_utc=time.time(),
                queued_count=len(self._queue),
                active_contentions=domain_counts,
                resolved_count=self._resolved_count,
            )
    
    def _update_queue_positions(self) -> None:
        """Update queue positions after sorting."""
        for i, entry in enumerate(self._queue):
            entry.queue_position = i


# =============================================================================
# Public API Exports
# =============================================================================

class ResourceContention(str):
    """Identifier for a contention."""
    pass


class ContentionQueue(list):
    """A queue for handling contentions."""
    pass


__all__ = [
    "ContentionKind",
    "ContentionState",
    "ContentionDecisionType",
    "ContentionDecision",
    "ContentionQueueEntry",
    "ContentionSnapshot",
    "ContentionResolver",
    "ResourceContention",
    "ContentionQueue",
]
