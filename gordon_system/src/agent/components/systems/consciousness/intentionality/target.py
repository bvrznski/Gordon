# Gordon Phase 5.7.3-I: Intentional Context Engine - Targets Model
# ===============================================================================
#
# Immutable targets representing objects the agent is currently oriented toward.
# Targets combine intentional objects with their context-specific properties.
#

"""
Targets Model for the Intentional Context Engine.

A target represents an intentional object in a specific context, preserving:
    - Identity: Stable identifier across transitions
    - Provenance: Origin chain from source system
    - Trust: Estimated trust level from source or system
    - Privacy: Classification determining access controls
    - Uncertainty: Confidence level in the target's validity

Targets are canonical references that preserve ownership semantics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional
import uuid


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    return uuid.uuid4().hex[:8]


# =============================================================================
# TARGET STATUS
# =============================================================================

class TargetStatus:
    """
    Enum-like status values for targets.
    
    Lifecycle states:
        - ACTIVE: Currently active in intentional context
        - SUSPENDED: Temporarily inactive (can be resumed)
        - COMPLETED: Target completed successfully
        - ABANDONED: Target abandoned
        - FAILED: Target failed to achieve goal
    """
    
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    FAILED = "failed"
    
    ALL: Tuple[str, ...] = (ACTIVE, SUSPENDED, COMPLETED, ABANDONED, FAILED)


# =============================================================================
# INTENTIONAL TARGET
# =============================================================================

@dataclass(frozen=True)
class IntentionalTarget:
    """
    Immutable intentional target representing a current directed orientation.
    
    A target combines an intentional object with context-specific properties:
        - source_owner: The subsystem that owns the reference
        - identity: Stable identifier from the source system
        - provenance: Chain of transitions leading to this reference
        - trust: Estimated trust level (system-assigned or inherited)
        - privacy: Privacy classification for access control
        - uncertainty: Confidence level in target validity
    
    NOT included:
        - Full payload content (only references)
        - Runtime state from source systems
        - Reasoning about the target
    """
    
    # Identity (required fields first - no defaults before required)
    target_id: str
    """Unique identifier for this intentional target."""
    
    # Target reference (intentional object in context)
    object_reference: str
    """Reference to the intentional object being targeted."""
    
    source_owner: str
    """Source subsystem that owns this target reference (e.g., 'perception', 'memory')."""
    
    # Classification and properties
    privacy_classification: str = "internal"
    """Privacy level for access control decisions."""
    
    trust_level: float = 0.5
    """Trust level estimate (0.0 to 1.0)."""
    
    uncertainty: float = 0.0
    """Uncertainty in target validity (complement of confidence)."""
    
    # Status and lifecycle
    status: str = field(default=TargetStatus.ACTIVE)
    """Current lifecycle state."""
    
    priority_reference: Optional[str] = None
    """Reference to priority assessment (e.g., 'high', 'medium', 'low')."""
    
    # Timing
    established_at_utc: float = field(default_factory=time.time)
    """When this target was first established."""
    
    expires_at_utc: Optional[float] = None
    """Optional expiration time for this target."""
    
    last_updated_at_utc: float = field(default_factory=time.time)
    """When this target was last updated."""
    
    # Provenance (for auditability and replay)
    provenance_chain: Tuple[str, ...] = field(default_factory=tuple)
    """Chain of transitions leading to this reference."""
    
    transition_id: Optional[str] = None
    """Transition that established or last updated this target."""
    
    generation: int = 0
    """Generation number for this target's lineage."""
    
    # Metadata (for extensibility)
    metadata: Dict[str, str] = field(default_factory=dict)
    """Optional metadata key-value pairs for extension."""
    
    @property
    def is_expired(self) -> bool:
        """Check if this target has expired."""
        if self.expires_at_utc is None:
            return False
        return time.time() > self.expires_at_utc
    
    @property
    def confidence(self) -> float:
        """Get confidence level (1.0 - uncertainty)."""
        return max(0.0, min(1.0, 1.0 - self.uncertainty))
    
    @classmethod
    def create_target(
        cls,
        object_reference: str,
        source_owner: str,
        privacy_classification: str = "internal",
        trust_level: float = 0.5,
        uncertainty: float = 0.2,
        priority_reference: Optional[str] = None,
    ) -> "IntentionalTarget":
        """
        Create a new intentional target.
        
        Args:
            object_reference: Reference to the intentional object
            source_owner: Source subsystem owning this reference
            privacy_classification: Privacy level
            trust_level: Trust estimate (0.0 to 1.0)
            uncertainty: Uncertainty in validity (0.0 to 1.0)
            priority_reference: Priority assessment reference
            
        Returns:
            New IntentionalTarget with status='active'
        """
        return cls(
            target_id=f"target-{_generate_uuid()}",
            object_reference=object_reference,
            source_owner=source_owner,
            privacy_classification=privacy_classification,
            trust_level=trust_level,
            uncertainty=uncertainty,
            priority_reference=priority_reference,
        )
    
    @classmethod
    def create_from_existing(
        cls,
        existing_target: "IntentionalTarget",
        transition_id: str,
        generation: int,
        new_status: Optional[str] = None,
        provenance_update: Tuple[str, ...] = tuple(),
    ) -> "IntentionalTarget":
        """
        Create a new target from an existing one (for transitions).
        
        This preserves identity while updating context-specific properties.
        
        Args:
            existing_target: The source target to copy
            transition_id: ID of the transition creating this version
            generation: New generation number
            new_status: Optional status override
            provenance_update: Additional provenance chain entries
            
        Returns:
            New IntentionalTarget with updated transition info
        """
        return cls(
            target_id=existing_target.target_id,
            object_reference=existing_target.object_reference,
            source_owner=existing_target.source_owner,
            privacy_classification=existing_target.privacy_classification,
            trust_level=existing_target.trust_level,
            uncertainty=existing_target.uncertainty,
            status=new_status or existing_target.status,
            priority_reference=existing_target.priority_reference,
            established_at_utc=existing_target.established_at_utc,  # Keep original
            expires_at_utc=existing_target.expires_at_utc,
            last_updated_at_utc=time.time(),
            provenance_chain=existing_target.provenance_chain + provenance_update,
            transition_id=transition_id,
            generation=generation,
            metadata=dict(existing_target.metadata),
        )
    
    def with_status(self, new_status: str) -> "IntentionalTarget":
        """Return a copy with updated status."""
        return dataclass_replace(self, status=new_status, last_updated_at_utc=time.time())
    
    def with_priority(self, priority_reference: str) -> "IntentionalTarget":
        """Return a copy with updated priority reference."""
        return dataclass_replace(
            self,
            priority_reference=priority_reference,
            last_updated_at_utc=time.time(),
        )
    
    def suspend(self) -> "IntentionalTarget":
        """Suspend this target (for resumption later)."""
        return self.with_status(TargetStatus.SUSPENDED)
    
    def complete(self) -> "IntentionalTarget":
        """Mark this target as completed."""
        return self.with_status(TargetStatus.COMPLETED)
    
    def abandon(self) -> "IntentionalTarget":
        """Abandon this target."""
        return self.with_status(TargetStatus.ABANDONED)
    
    def fail(self) -> "IntentionalTarget":
        """Mark this target as failed."""
        return self.with_status(TargetStatus.FAILED)


# Import dataclass_replace for methods
from dataclasses import replace as dataclass_replace


# =============================================================================
# TARGET REGISTRY
# =============================================================================

class IntentionalTargetRegistry:
    """
    Registry for managing intentional targets.
    
    Provides:
        - Target identity management with lifecycle state tracking
        - Source-based filtering and lookups
        - Deterministic ordering (for replayability)
        - Transition tracking for provenance
    
    Targets are never mutated in place. Each transition creates a new generation
    of the target, preserving the previous version for audit/replay.
    """
    
    def __init__(self) -> None:
        """Initialize the registry with empty storage."""
        self._targets: Dict[str, IntentionalTarget] = {}
        self._object_indices: Dict[str, set] = {}
        self._source_indices: Dict[str, set] = {}
        self._status_indices: Dict[str, set] = {status: set() for status in TargetStatus.ALL}
    
    def register(self, target: IntentionalTarget) -> bool:
        """
        Register an intentional target.
        
        Args:
            target: The target to register
            
        Returns:
            True if registered (or already exists), False on conflict
        """
        # Check for duplicate
        if target.target_id in self._targets:
            return False
        
        self._targets[target.target_id] = target
        self._object_indices.setdefault(target.object_reference, set()).add(target.target_id)
        self._source_indices.setdefault(target.source_owner, set()).add(target.target_id)
        self._status_indices[target.status].add(target.target_id)
        
        return True
    
    def get(self, target_id: str) -> Optional[IntentionalTarget]:
        """Get a target by ID."""
        return self._targets.get(target_id)
    
    def get_by_object_reference(self, object_ref: str) -> Tuple[IntentionalTarget, ...]:
        """Get all targets for a specific object reference."""
        ids = self._object_indices.get(object_ref, set())
        return tuple(self._targets[tid] for tid in ids if tid in self._targets)
    
    def get_by_source_owner(self, source: str) -> Tuple[IntentionalTarget, ...]:
        """Get all targets from a specific source owner."""
        ids = self._source_indices.get(source, set())
        return tuple(self._targets[tid] for tid in ids if tid in self._targets)
    
    def get_by_status(self, status: str) -> Tuple[IntentionalTarget, ...]:
        """Get all targets with a specific status."""
        ids = self._status_indices.get(status, set())
        return tuple(self._targets[tid] for tid in ids if tid in self._targets)
    
    def update(self, target: IntentionalTarget, provenance_update: Tuple[str, ...] = tuple()) -> None:
        """
        Update a target (creates new generation with transition info).
        
        Args:
            target: The updated target (should have same target_id)
            provenance_update: Additional provenance chain entries
        """
        if target.target_id not in self._targets:
            raise KeyError(f"Target not found: {target.target_id}")
        
        # Update existing record
        self._targets[target.target_id] = target
        
        # Re-index by status (status may have changed)
        old_status = self._get_target_status(target.target_id)
        if old_status and old_status != target.status:
            self._status_indices[old_status].discard(target.target_id)
        self._status_indices[target.status].add(target.target_id)
    
    def _get_target_status(self, target_id: str) -> Optional[str]:
        """Get the current status of a target by ID."""
        for status, ids in self._status_indices.items():
            if target_id in ids:
                return status
        return None
    
    def remove(self, target_id: str) -> bool:
        """Remove a target by ID."""
        target = self._targets.get(target_id)
        if target is None:
            return False
        
        del self._targets[target_id]
        obj_idx = self._object_indices.get(target.object_reference)
        if obj_idx:
            obj_idx.discard(target_id)
        
        src_idx = self._source_indices.get(target.source_owner)
        if src_idx:
            src_idx.discard(target_id)
        
        self._status_indices[target.status].discard(target_id)
        
        return True
    
    @property
    def registered_count(self) -> int:
        """Return total number of registered targets."""
        return len(self._targets)
    
    @property
    def active_target_count(self) -> int:
        """Return count of active (non-completed/abandoned) targets."""
        active_statuses = {TargetStatus.ACTIVE, TargetStatus.SUSPENDED}
        return sum(
            len(self._status_indices.get(s, set()))
            for s in active_statuses
        )
    
    @property
    def status_counts(self) -> Dict[str, int]:
        """Return dict mapping statuses to their target counts."""
        return {status: len(ids) for status, ids in self._status_indices.items()}


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "TargetStatus",
    "IntentionalTarget",
    "IntentionalTargetRegistry",
)