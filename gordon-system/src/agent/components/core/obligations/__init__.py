# Core Obligations System
# =======================
"""
Core runtime obligation tracking.

Provides:
- Obligation creation, assignment, and fulfillment
- Compliance verification
- Penalty management for violations

Phase 3.7: Runtime third-stage expansion - Obligations subsystem.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import time


# =============================================================================
# Obligation Status
# =============================================================================

class ObligationStatus(Enum):
    """
    Status of an obligation in its lifecycle.
    
    - CREATED: Obligation created but not yet assigned
    - ASSIGNED: Assigned to a responsible party
    - PENDING: Waiting for fulfillment
    - IN_PROGRESS: Being worked on
    - FULFILLED: Successfully fulfilled
    - EXPIRED: Time limit reached without fulfillment
    - VIOLATED: Violation recorded (failed to fulfill)
    """
    
    CREATED = "created"
    ASSIGNED = "assigned"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FULFILLED = "fulfilled"
    EXPIRED = "expired"
    VIOLATED = "violated"


# =============================================================================
# Obligation
# =============================================================================

@dataclass(frozen=True)
class Obligation:
    """
    A runtime obligation that must be fulfilled.
    
    Usage:
        obligation = Obligation(
            obligation_id=obligation_id,
            responsible_entity=entity_id,
            required_action="log_event",
            deadline=time.time() + 3600
        )
        
        # Track fulfillment
        if time.time() > obligation.deadline and not obligation.fulfilled:
            await record_violation(obligation)
    """
    
    obligation_id: str
    
    # What must be done
    required_action: str  # e.g., "log_event", "release_resource"
    description: str = ""
    
    # Who is responsible
    responsible_entity: Any  # Entity ID or similar
    assigned_at: float = field(default_factory=time.time)
    
    # Time constraints
    deadline: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    
    # Status tracking
    status: ObligationStatus = ObligationStatus.CREATED
    
    # Fulfillment evidence
    fulfilled_at: Optional[float] = None
    fulfillment_evidence: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_due(self) -> bool:
        """Check if obligation has passed its deadline."""
        if self.deadline is None:
            return False
        return time.time() > self.deadline
    
    @property
    def is_violated(self) -> bool:
        """Check if obligation was not fulfilled in time."""
        return self.status == ObligationStatus.VIOLATED or (
            self.is_due and 
            self.status in (ObligationStatus.CREATED, ASSIGNED, PENDING, IN_PROGRESS)
        )
    
    @property
    def remaining_seconds(self) -> Optional[float]:
        """Return seconds until deadline (negative if past)."""
        if self.deadline is None:
            return None
        return self.deadline - time.time()
    
    def fulfill(
        self,
        evidence: Dict[str, Any]
    ) -> "Obligation":
        """Return a fulfilled copy of this obligation."""
        return Obligation(
            obligation_id=self.obligation_id,
            required_action=self.required_action,
            description=self.description,
            responsible_entity=self.responsible_entity,
            assigned_at=self.assigned_at,
            deadline=self.deadline,
            created_at=self.created_at,
            status=ObligationStatus.FULFILLED,
            fulfilled_at=time.time(),
            fulfillment_evidence=dict(evidence)
        )
    
    def mark_violated(self) -> "Obligation":
        """Return a violated copy of this obligation."""
        return Obligation(
            obligation_id=self.obligation_id,
            required_action=self.required_action,
            description=self.description,
            responsible_entity=self.responsible_entity,
            assigned_at=self.assigned_at,
            deadline=self.deadline,
            created_at=self.created_at,
            status=ObligationStatus.VIOLATED,
            fulfilled_at=None,
            fulfillment_evidence=dict(self.fulfillment_evidence)
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "obligation_id": self.obligation_id,
            "required_action": self.required_action,
            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),
            "responsible_entity": str(self.responsible_entity) if hasattr(self.responsible_entity, '__str__') else self.responsible_entity,
            "deadline": self.deadline,
            "remaining_seconds": self.remaining_seconds,
            "is_violated": self.is_violated
        }


# =============================================================================
# Obligation Tracker
# =============================================================================

class ObligationTracker:
    """
    Tracks obligations for a runtime entity.
    
    Provides:
        - Obligation lifecycle management
        - Violation detection and recording
        - Fulfillment tracking
    
    Usage:
        tracker = ObligationTracker(entity_id)
        
        # Create obligation
        obligation = tracker.create_obligation(
            required_action="release_resource",
            deadline=time.time() + 300
        )
        
        # Track status
        if tracker.has_violations():
            await handle_violations(tracker.get_violations())
    """
    
    def __init__(self, entity_id: str) -> None:
        self.entity_id = entity_id
        self._obligations: Dict[str, Obligation] = {}
        self._lock = __import__("threading").Lock()
    
    def create_obligation(
        self,
        required_action: str,
        description: Optional[str] = None,
        deadline: Optional[float] = None,
        responsible_entity: Optional[Any] = None
    ) -> Obligation:
        """
        Create a new obligation.
        
        Args:
            required_action: What action must be taken
            description: Human-readable description
            deadline: When it must be completed (optional)
            responsible_entity: Who is responsible
            
        Returns:
            The created Obligation
        """
        import uuid
        
        with self._lock:
            obligation = Obligation(
                obligation_id=f"oblig_{uuid.uuid4().hex[:8]}",
                required_action=required_action,
                description=description or f"Obligation for {self.entity_id}",
                responsible_entity=responsible_entity or self.entity_id,
                deadline=deadline
            )
            
            self._obligations[obligation.obligation_id] = obligation
            return obligation
    
    def fulfill(self, obligation_id: str, evidence: Dict[str, Any]) -> bool:
        """
        Mark an obligation as fulfilled.
        
        Args:
            obligation_id: The obligation to fulfill
            evidence: Evidence of fulfillment
            
        Returns:
            True if fulfilled successfully
        """
        with self._lock:
            obligation = self._obligations.get(obligation_id)
            if not obligation or obligation.status == ObligationStatus.FULFILLED:
                return False
            
            self._obligations[obligation_id] = obligation.fulfill(evidence)
            return True
    
    def mark_violated(self, obligation_id: str) -> bool:
        """
        Mark an obligation as violated.
        
        Args:
            obligation_id: The obligation to violate
            
        Returns:
            True if marked as violated successfully
        """
        with self._lock:
            obligation = self._obligations.get(obligation_id)
            if not obligation or obligation.status == ObligationStatus.VIOLATED:
                return False
            
            self._obligations[obligation_id] = obligation.mark_violated()
            return True
    
    def get(self, obligation_id: str) -> Optional[Obligation]:
        """Get an obligation by ID."""
        return self._obligations.get(obligation_id)
    
    def get_all(self) -> List[Obligation]:
        """Get all obligations."""
        with self._lock:
            return list(self._obligations.values())
    
    def get_by_status(self, status: ObligationStatus) -> List[Obligation]:
        """Get obligations with a specific status."""
        with self._lock:
            return [
                o for o in self._obligations.values()
                if o.status == status
            ]
    
    def get_pending(self) -> List[Obligation]:
        """Get pending (not fulfilled, not violated) obligations."""
        with self._lock:
            return [
                o for o in self._obligations.values()
                if o.status in (
                    ObligationStatus.CREATED,
                    ObligationStatus.ASSIGNED,
                    ObligationStatus.PENDING,
                    ObligationStatus.IN_PROGRESS
                )
            ]
    
    def get_violations(self) -> List[Obligation]:
        """Get all violated obligations."""
        with self._lock:
            return [
                o for o in self._obligations.values()
                if o.status == ObligationStatus.VIOLATED
            ]
    
    def has_violations(self) -> bool:
        """Check if any violations exist."""
        with self._lock:
            return any(
                o.status == ObligationStatus.VIOLATED
                for o in self._obligations.values()
            )
    
    @property
    def total_obligations(self) -> int:
        """Return total number of tracked obligations."""
        with self._lock:
            return len(self._obligations)
    
    @property
    def fulfilled_count(self) -> int:
        """Return count of fulfilled obligations."""
        with self._lock:
            return len([
                o for o in self._obligations.values()
                if o.status == ObligationStatus.FULFILLED
            ])
    
    @property
    def violation_count(self) -> int:
        """Return count of violated obligations."""
        with self._lock:
            return len([
                o for o in self._obligations.values()
                if o.status == ObligationStatus.VIOLATED
            ])


__all__ = [
    # Status
    "ObligationStatus",
    
    # Obligations
    "Obligation",
    "ObligationTracker",
]