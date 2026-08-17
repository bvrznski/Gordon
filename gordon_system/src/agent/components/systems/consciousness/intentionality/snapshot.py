# Gordon Phase 5.7.3-I: Intentional Context Engine - Snapshots Model
# ===============================================================================
#
# Immutable intentional context snapshots capturing the complete directed
# cognitive state at a point in time.
#

"""
Intentional Context Snapshots for the Intentional Context Engine.

A snapshot captures:
    - All intentional objects currently referenced
    - All intentional relations between field and objects
    - All intentional targets with their states
    - Transition metadata for lineage tracking
    
Snapshots are immutable, versioned by generation, and may be superseded by
new generations through atomic transitions.
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
# INTENTIONAL CONTEXT SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class IntentionalContextSnapshot:
    """
    Immutable snapshot of the intentional context at a point in time.
    
    A snapshot represents the complete, bounded intentional state after
    construction. Snapshots are versioned by generation and may be superseded
    by newer generations through atomic transitions.
    
    Snapshot properties:
        - Immutable: Once created, never modified
        - Bounded: All collections respect capacity limits
        - Versioned: Has explicit context_id and generation
        - Provenance-preserving: Links to previous generation for lineage
    
    NOT included (external):
        - Runtime state objects
        - Full payloads (only references)
        - External service connections
    """
    
    # Identity and versioning (required fields first)
    context_id: str
    """Unique identifier for this logical intentional context."""
    
    generation: int = 0
    """Current generation number (strictly monotonic)."""
    
    previous_generation: Optional[int] = None
    """Previous generation (for lineage tracking)."""
    
    transition_id: Optional[str] = None
    """Transition that produced this snapshot (if any)."""
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    """When this snapshot was created."""
    
    # Intentional objects reference
    object_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to intentional objects in the context."""
    
    # Intentional relations
    relation_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to intentional relations in the context."""
    
    # Intentional targets
    target_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to intentional targets in the context."""
    
    # Current directedness summary (bounded)
    active_target_count: int = 0
    """Number of active targets (computed from target_references)."""
    
    relation_count: int = 0
    """Number of intentional relations (computed from relation_references)."""
    
    # Source information
    experiential_field_context_id: Optional[str] = None
    """Reference to current experiential field context."""
    
    source_owners: Tuple[str, ...] = field(default_factory=tuple)
    """Set of unique source owners in this snapshot."""
    
    # Status and health
    build_status: str = "valid"
    """Current status (building, valid, degraded, invalid)."""
    
    degradation_modes: Tuple[str, ...] = field(default_factory=tuple)
    """Any degradation modes active in this snapshot."""
    
    # Summary classifications
    privacy_summary: str = "internal"
    """Summary privacy classification of all objects/relations/targets."""
    
    trust_summary: str = "medium"
    """Summary trust classification of all objects/relations/targets."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance information for this snapshot."""
    
    def __post_init__(self) -> None:
        """Post-initialization validation and computed fields."""
        object.__setattr__(self, "active_target_count", len(self.target_references))
        object.__setattr__(self, "relation_count", len(self.relation_references))
        
        # Extract unique source owners (would be populated in real implementation)
        object.__setattr__(self, "source_owners", tuple(sorted(set(
            self._extract_source_owners()
        ))))
    
    def _extract_source_owners(self) -> Tuple[str, ...]:
        """Extract unique source owners from references."""
        # In a full implementation, this would parse the references
        return tuple()
    
    @classmethod
    def initial(cls, context_id: str) -> "IntentionalContextSnapshot":
        """
        Create an initial empty snapshot.
        
        Args:
            context_id: ID for this logical intentional context
            
        Returns:
            Initial snapshot with zero contents and generation 0
        """
        return cls(
            context_id=context_id,
            generation=0,
            previous_generation=None,
            created_at_utc=time.time(),
            build_status="valid",
        )
    
    def next_generation(self, transition_id: str) -> "IntentionalContextSnapshot":
        """
        Create the next generation snapshot from this one.
        
        Args:
            transition_id: ID of the transition producing this generation
            
        Returns:
            New IntentionalContextSnapshot with generation + 1
        """
        return IntentionalContextSnapshot(
            context_id=self.context_id,
            generation=self.generation + 1,
            previous_generation=self.generation,
            transition_id=transition_id,
            created_at_utc=time.time(),
            object_references=self.object_references,
            relation_references=self.relation_references,
            target_references=self.target_references,
            build_status="valid",
        )
    
    @property
    def is_empty(self) -> bool:
        """Check if this snapshot has no intentional objects."""
        return len(self.object_references) == 0
    
    @property
    def is_valid(self) -> bool:
        """Check if this snapshot's status indicates validity."""
        return self.build_status in ("valid", "building")
    
    @property
    def is_degraded(self) -> bool:
        """Check if this snapshot is in degraded mode."""
        return len(self.degradation_modes) > 0
    
    def with_objects(
        self,
        *object_references: str,
    ) -> "IntentionalContextSnapshot":
        """Return a copy with updated object references."""
        return dataclass_replace(
            self,
            object_references=tuple(object_references),
        )
    
    def with_relations(
        self,
        *relation_references: str,
    ) -> "IntentionalContextSnapshot":
        """Return a copy with updated relation references."""
        return dataclass_replace(
            self,
            relation_references=tuple(relation_references),
        )
    
    def with_targets(
        self,
        *target_references: str,
    ) -> "IntentionalContextSnapshot":
        """Return a copy with updated target references."""
        return dataclass_replace(
            self,
            target_references=tuple(target_references),
        )


# Import dataclass_replace for methods
from dataclasses import replace as dataclass_replace


# =============================================================================
# INTENTIONAL CONTEXT SNAPSHOT BUILDER
# =============================================================================

class IntentionalContextSnapshotBuilder:
    """
    Builder for constructing intentional context snapshots.
    
    Provides a fluent API for incrementally building snapshots before
    publishing them atomically via transitions.
    
    Building process:
        1. Initialize with context_id and generation
        2. Add objects, relations, targets
        3. Apply classifications (privacy, trust)
        4. Finalize into an immutable snapshot
        
    Builder is NOT thread-safe - each thread should create its own builder.
    """
    
    def __init__(self, context_id: str, generation: int = 0):
        """
        Initialize the builder with a context ID and initial generation.
        
        Args:
            context_id: ID for this intentional context
            generation: Initial generation number (default 0)
        """
        self._context_id = context_id
        self._generation = generation
        self._previous_generation: Optional[int] = None
        self._created_at_utc = time.time()
        
        self._object_references: list[str] = []
        self._relation_references: list[str] = []
        self._target_references: list[str] = []
        
        self._experiential_field_context_id: Optional[str] = None
        
        self._build_status = "building"
        self._degradation_modes: list[str] = []
        
        self._privacy_summary = "internal"
        self._trust_summary = "medium"
    
    def set_previous_generation(self, generation: int) -> "IntentionalContextSnapshotBuilder":
        """Set the previous generation for lineage tracking."""
        self._previous_generation = generation
        return self
    
    def add_object_reference(self, reference: str) -> "IntentionalContextSnapshotBuilder":
        """Add an intentional object reference."""
        if reference not in self._object_references:
            self._object_references.append(reference)
        return self
    
    def add_relation_reference(self, reference: str) -> "IntentionalContextSnapshotBuilder":
        """Add an intentional relation reference."""
        if reference not in self._relation_references:
            self._relation_references.append(reference)
        return self
    
    def add_target_reference(self, reference: str) -> "IntentionalContextSnapshotBuilder":
        """Add an intentional target reference."""
        if reference not in self._target_references:
            self._target_references.append(reference)
        return self
    
    def set_experiential_field_context_id(
        self,
        context_id: Optional[str],
    ) -> "IntentionalContextSnapshotBuilder":
        """Set the experiential field context ID."""
        self._experiential_field_context_id = context_id
        return self
    
    def with_status(self, status: str) -> "IntentionalContextSnapshotBuilder":
        """Set the build status."""
        self._build_status = status
        return self
    
    def add_degradation_mode(self, mode: str) -> "IntentionalContextSnapshotBuilder":
        """Add a degradation mode."""
        if mode not in self._degradation_modes:
            self._degradation_modes.append(mode)
        return self
    
    def with_privacy_summary(self, summary: str) -> "IntentionalContextSnapshotBuilder":
        """Set the privacy classification summary."""
        self._privacy_summary = summary
        return self
    
    def with_trust_summary(self, summary: str) -> "IntentionalContextSnapshotBuilder":
        """Set the trust classification summary."""
        self._trust_summary = summary
        return self
    
    def build(self) -> IntentionalContextSnapshot:
        """
        Build and return an immutable intentional context snapshot.
        
        Returns:
            New IntentionalContextSnapshot with all accumulated state
        
        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        if not self._context_id:
            raise ValueError("Context ID is required")
        
        return IntentionalContextSnapshot(
            context_id=self._context_id,
            generation=self._generation,
            previous_generation=self._previous_generation,
            created_at_utc=self._created_at_utc,
            object_references=tuple(self._object_references),
            relation_references=tuple(self._relation_references),
            target_references=tuple(self._target_references),
            experiential_field_context_id=self._experiential_field_context_id,
            build_status=self._build_status,
            degradation_modes=tuple(self._degradation_modes),
            privacy_summary=self._privacy_summary,
            trust_summary=self._trust_summary,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "IntentionalContextSnapshot",
    "IntentionalContextSnapshotBuilder",
)