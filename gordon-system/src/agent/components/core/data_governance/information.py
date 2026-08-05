# Information Registry - Canonical Authority
# ===========================================

"""
Information registry - canonical authority for information registration,
cataloging, and lookup.

PHASE 3.7.21 REMEDIATION:
- Records own their semantics (lifecycle_state, classification, etc.)
- Registry provides cataloging, not state management
- Ownership validation happens at record creation time
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum

from .models import (
    OwnerType,
    OwnerIdentity,
    ClassificationLevel,
    LifecycleState,
    InformationRecord,
    OwnershipRecord,
)


# =============================================================================
# Events - Immutable governance events
# =============================================================================

class InformationEventType(Enum):
    """Types of information lifecycle events."""
    CREATED = "created"
    REGISTERED = "registered"
    OWNERSHIP_ASSIGNED = "ownership_assigned"
    LIFECYCLE_UPDATED = "lifecycle_updated"
    CLASSIFICATION_CHANGED = "classification_changed"


@dataclass(frozen=True)
class InformationEvent:
    """
    Immutable event emitted by the information registry.
    
    Args:
        event_type: Type of event
        information_id: ID of the affected information
        timestamp: When event occurred
        metadata: Event-specific metadata
    """
    
    event_type: InformationEventType
    information_id: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Information Registry - Canonical Authority (PHASE 3.7.21 REMEDIATION)
# =============================================================================

class InformationRegistry:
    """
    Canonical authority for information registration and cataloging.
    
    PHASE 3.7.21 REMEDIATION:
    - Records own their semantics (lifecycle_state, classification, etc.)
    - Registry provides cataloging, not state management
    - Ownership validation happens at record creation time
    
    Core Responsibilities:
    1. Information registration with unique IDs
    2. Owner assignment and transfer tracking
    3. Cataloging and retrieval by criteria
    4. Event emission for audit trail
    
    Non-Responsibilities (moved to record types):
    - State transition management (records have lifecycle_state field)
    - Classification validation (done at record construction)
    - Privacy enforcement (data-oriented: redaction/filtering)
    
    Usage:
        # Create registry
        registry = InformationRegistry()
        
        # Register information (record owns its state)
        record = InformationRecord(
            information_id="data-123",
            content_hash="hash123",
            owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
            classification=ClassificationLevel.INTERNAL,
            lifecycle_state=LifecycleState.ACTIVE,
        )
        
        # Registry catalogs it
        await registry.register(record)
        
        # Retrieve later
        retrieved = await registry.get("data-123")
    """
    
    def __init__(self) -> None:
        """Initialize the information registry."""
        self._lock = threading.RLock()
        
        # Registered records by ID
        self._records: Dict[str, InformationRecord] = {}
        
        # Indexes for querying
        self._by_owner: Dict[str, Set[str]] = {}  # owner_id -> set of record_ids
        self._by_state: Dict[LifecycleState, Set[str]] = {state: set() for state in LifecycleState}
        self._by_classification: Dict[ClassificationLevel, Set[str]] = {
            cls: set() for cls in ClassificationLevel
        }
        
        # Event history for observability
        self._events: List[InformationEvent] = []
        
        # Statistics
        self._stats = {
            "total_registered": 0,
            "by_type": {},
        }
    
    async def register(self, record: InformationRecord) -> InformationRecord:
        """
        Register an information record.
        
        PHASE 3.7.21: The record already owns its semantics (lifecycle_state,
        classification, etc.). The registry just catalogs it for lookup.
        
        Args:
            record: Information record to register
            
        Returns:
            The registered record
        """
        with self._lock:
            information_id = record.information_id
            
            if information_id in self._records:
                raise ValueError(f"Record already registered: {information_id}")
            
            # Store the record (it owns its state)
            self._records[information_id] = record
            
            # Update indexes
            owner_id = record.owner.id
            if owner_id not in self._by_owner:
                self._by_owner[owner_id] = set()
            self._by_owner[owner_id].add(information_id)
            
            self._by_state[record.lifecycle_state].add(information_id)
            self._by_classification[record.classification].add(information_id)
            
            # Emit event
            event = InformationEvent(
                event_type=InformationEventType.REGISTERED,
                information_id=information_id,
                metadata={"owner": record.owner.id}
            )
            self._events.append(event)
            
            # Update stats
            self._stats["total_registered"] += 1
            type_key = f"{record.classification.value}_{record.lifecycle_state.value}"
            self._stats["by_type"][type_key] = self._stats["by_type"].get(type_key, 0) + 1
            
            return record
    
    async def get(self, information_id: str) -> Optional[InformationRecord]:
        """
        Get a registered record by ID.
        
        Args:
            information_id: ID of the record to retrieve
            
        Returns:
            The record if found, None otherwise
        """
        with self._lock:
            return self._records.get(information_id)
    
    async def get_by_owner(self, owner_id: str) -> List[InformationRecord]:
        """
        Get all records owned by a specific owner.
        
        Args:
            owner_id: ID of the owner
            
        Returns:
            List of records owned by the owner
        """
        with self._lock:
            record_ids = self._by_owner.get(owner_id, set())
            return [self._records[rid] for rid in record_ids if rid in self._records]
    
    async def get_by_state(self, state: LifecycleState) -> List[InformationRecord]:
        """
        Get all records in a specific lifecycle state.
        
        Args:
            state: Lifecycle state to filter by
            
        Returns:
            List of records in the specified state
        """
        with self._lock:
            record_ids = self._by_state.get(state, set())
            return [self._records[rid] for rid in record_ids if rid in self._records]
    
    async def get_by_classification(self, classification: ClassificationLevel) -> List[InformationRecord]:
        """
        Get all records with a specific classification.
        
        Args:
            classification: Classification level to filter by
            
        Returns:
            List of records with the specified classification
        """
        with self._lock:
            record_ids = self._by_classification.get(classification, set())
            return [self._records[rid] for rid in record_ids if rid in self._records]
    
    async def list_all(self) -> List[InformationRecord]:
        """Get all registered records."""
        with self._lock:
            return list(self._records.values())
    
    async def unregister(self, information_id: str) -> bool:
        """
        Remove a record from the registry.
        
        PHASE 3.7.21: Records own their lifecycle_state. Deletion is tracked
        by setting lifecycle_state to DELETED on the record itself.
        
        Args:
            information_id: ID of the record to unregister
            
        Returns:
            True if the record was unregistered, False if not found
        """
        with self._lock:
            if information_id not in self._records:
                return False
            
            record = self._records.pop(information_id)
            
            # Remove from indexes
            owner_id = record.owner.id
            if owner_id in self._by_owner:
                self._by_owner[owner_id].discard(information_id)
            
            self._by_state[record.lifecycle_state].discard(information_id)
            self._by_classification[record.classification].discard(information_id)
            
            return True
    
    def get_events(self, event_type: Optional[InformationEventType] = None) -> List[InformationEvent]:
        """
        Get event history.
        
        Args:
            event_type: Filter by event type (optional)
            
        Returns:
            List of events
        """
        with self._lock:
            if event_type is None:
                return list(self._events)
            return [e for e in self._events if e.event_type == event_type]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            return {
                "total_registered": self._stats["total_registered"],
                "by_type": dict(self._stats["by_type"]),
                "records_by_state": {s.value: len(ids) for s, ids in self._by_state.items()},
                "records_by_classification": {c.value: len(ids) for c, ids in self._by_classification.items()},
            }
    
    @property
    def total_registered(self) -> int:
        """Get count of registered records."""
        with self._lock:
            return len(self._records)
    
    def has_record(self, information_id: str) -> bool:
        """
        Check if a record is registered.
        
        Args:
            information_id: ID to check
            
        Returns:
            True if the record exists
        """
        with self._lock:
            return information_id in self._records


__all__ = [
    "InformationEventType",
    "InformationEvent",
    "InformationRegistry",
]