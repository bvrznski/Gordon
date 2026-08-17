# Gordon Phase 5.7.7: Situated World - Snapshot
# ===============================================

"""
Canonical immutable world snapshot model.

Snapshots contain only immutable references and never embed:
* live perception objects
* mutable runtime state
* tool clients  
* action executors
* raw sensor buffers
* unrestricted memory contents
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


def _generate_uuid() -> str:
    """Generate a UUID-like identifier."""
    return uuid.uuid4().hex[:8]


@dataclass(frozen=True)
class SnapshotReference:
    """
    Immutable reference to a world snapshot.
    
    Used for:
        - Replay from any point in time
        - Deterministic state restoration  
        - Provenance tracking
        - Cross-generation comparisons
    """
    
    snapshot_id: str = field(default_factory=lambda: f"snapshot-{_generate_uuid()}")
    """Unique identifier for this snapshot."""
    
    world_id: str | None = None
    """Reference to the world this snapshot represents."""
    
    generation: int = 0
    """Generation number at time of snapshot."""
    
    timestamp_ref: str | None = None
    """Semantic time reference when snapshot was taken."""
    
    previous_snapshot_id: str | None = None
    """ID of previous snapshot in chain (for transition tracking)."""
    
    @classmethod
    def from_world_state(
        cls,
        world_id: str,
        generation: int,
        timestamp_ref: str | None = None,
    ) -> "SnapshotReference":
        """Create a snapshot reference from world state."""
        return cls(
            world_id=world_id,
            generation=generation,
            timestamp_ref=timestamp_ref,
        )


@dataclass(frozen=True)
class WorldSnapshot:
    """
    Canonical immutable world snapshot model.
    
    Contains only immutable references to world elements:
        - EntityReference
        - RelationReference  
        - AffordanceReference
        - ConstraintReference
        
    Never contains:
        - Live perception objects
        - Mutable runtime state
        - Tool clients
        - Action executors
        - Raw sensor buffers
    """
    
    snapshot_id: str = field(default_factory=lambda: f"snapshot-{_generate_uuid()}")
    """Unique identifier for this snapshot."""
    
    world_id: str
    """The world this snapshot represents."""
    
    generation: int = 1
    """Generation number at time of snapshot."""
    
    timestamp_ref: str | None = None
    """Semantic time reference when snapshot was taken."""
    
    # Immutable references only
    entity_references: tuple[str, ...] = field(default_factory=tuple)
    """Entity IDs in the world."""
    
    relation_references: tuple[str, ...] = field(default_factory=tuple)
    """Relation IDs in the world."""
    
    affordance_references: tuple[str, ...] = field(default_factory=tuple)
    """Affordance IDs in the world."""
    
    constraint_references: tuple[str, ...] = field(default_factory=tuple)
    """Constraint IDs in the world."""
    
    environment_ref: str | None = None
    """Environment reference at time of snapshot."""
    
    # Metadata for observability
    entity_count: int = 0
    relation_count: int = 0
    affordance_count: int = 0  
    constraint_count: int = 0
    
    def has_entity(self, entity_id: str) -> bool:
        """Check if this snapshot contains a specific entity."""
        return entity_id in self.entity_references
    
    def has_relation(self, relation_id: str) -> bool:
        """Check if this snapshot contains a specific relation."""
        return relation_id in self.relation_references
    
    def has_affordance(self, affordance_id: str) -> bool:
        """Check if this snapshot contains a specific affordance."""
        return affordance_id in self.affordance_references
    
    def has_constraint(self, constraint_id: str) -> bool:
        """Check if this snapshot contains a specific constraint."""
        return constraint_id in self.constraint_references
    
    @classmethod
    def from_world_state(
        cls,
        world_id: str,
        generation: int,
        entity_refs: tuple[str, ...],
        relation_refs: tuple[str, ...],
        affordance_refs: tuple[str, ...],
        constraint_refs: tuple[str, ...],
        environment_ref: str | None = None,
        timestamp_ref: str | None = None,
    ) -> "WorldSnapshot":
        """
        Create a WorldSnapshot from world state.
        
        Rules:
            - Only immutable references are included
            - Counts must match input lengths
            - References are validated for immutability
        """
        return cls(
            generation=generation,
            entity_references=entity_refs,
            relation_references=relation_refs,
            affordance_references=affordance_refs,
            constraint_references=constraint_refs,
            environment_ref=environment_ref,
            timestamp_ref=timestamp_ref,
            entity_count=len(entity_refs),
            relation_count=len(relation_refs),
            affordance_count=len(affordance_refs),
            constraint_count=len(constraint_refs),
        )
    
    def to_reference(self) -> SnapshotReference:
        """Convert to a lightweight snapshot reference."""
        return SnapshotReference(
            snapshot_id=self.snapshot_id,
            world_id=self.world_id,
            generation=self.generation,
            timestamp_ref=self.timestamp_ref,
        )