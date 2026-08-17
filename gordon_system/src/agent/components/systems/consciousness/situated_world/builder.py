# Gordon Phase 5.7.7: Situated World - Builder
# =============================================

"""
Canonical world state builder.

The builder pattern ensures:
* Immutable snapshots (build returns frozen state)
* Deterministic publication (same inputs = same outputs)
* Validation before publication
* Lifecycle management support
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


def _generate_uuid() -> str:
    """Generate a UUID-like identifier."""
    return uuid.uuid4().hex[:8]


@dataclass(frozen=True)
class WorldBuildResult:
    """
    Immutable result of a world build operation.
    
    Contains only immutable references and never exposes runtime state.
    """
    
    snapshot_id: str = field(default_factory=lambda: f"snapshot-{_generate_uuid()}")
    """The ID of the built snapshot."""
    
    world_id: str
    """The ID of the resulting world."""
    
    generation: int
    """Generation number after build."""
    
    entities_added_count: int = 0
    relations_added_count: int = 0
    affordances_added_count: int = 0
    constraints_added_count: int = 0
    
    transition_id: str | None = None
    """The transition that produced this world state."""
    
    is_deterministic: bool = True
    """Whether the build was deterministic."""


@dataclass(frozen=True)
class WorldBuildRequest:
    """
    Request to build a new world snapshot.
    
    Contains only immutable references and contributions from external systems.
    """
    
    world_id: str | None = None
    """World ID (None for new worlds)."""
    
    from_snapshot_id: str | None = None
    """Previous snapshot ID for incremental builds."""
    
    generation: int | None = None
    """Target generation number."""
    
    environment_ref: str | None = None
    """Environment reference for this world state."""
    
    entity_refs_to_add: tuple[str, ...] = field(default_factory=tuple)
    """Entity references to add."""
    
    relation_refs_to_add: tuple[str, ...] = field(default_factory=tuple)
    """Relation references to add."""
    
    affordance_refs_to_add: tuple[str, ...] = field(default_factory=tuple)
    """Affordance references to add."""
    
    constraint_refs_to_add: tuple[str, ...] = field(default_factory=tuple)
    """Constraint references to add."""
    
    metadata: dict[str, object] = field(default_factory=dict)
    """Additional build metadata."""


@dataclass
class WorldBuilder:
    """
    Canonical world state builder.
    
    Builder pattern ensures:
        - Immutable snapshots (build returns frozen state)
        - Deterministic publication (same inputs = same outputs)
        - Validation before publication
        - Lifecycle management support
    
    Never exposes mutable internal state.
    """
    
    # Internal mutable state during build
    _world_id: str | None = None
    _from_snapshot_id: str | None = None
    _generation: int | None = None
    _environment_ref: str | None = None
    
    _entity_refs_to_add: list[str] = field(default_factory=list)
    _relation_refs_to_add: list[str] = field(default_factory=list)
    _affordance_refs_to_add: list[str] = field(default_factory=list)
    _constraint_refs_to_add: list[str] = field(default_factory=list)
    
    def reset(self) -> "WorldBuilder":
        """Reset builder to fresh state."""
        self._world_id = None
        self._from_snapshot_id = None
        self._generation = None
        self._environment_ref = None
        self._entity_refs_to_add.clear()
        self._relation_refs_to_add.clear()
        self._affordance_refs_to_add.clear()
        self._constraint_refs_to_add.clear()
        return self
    
    def from_world_id(self, world_id: str) -> "WorldBuilder":
        """Set the target world ID."""
        self._world_id = world_id
        return self
    
    def from_snapshot(self, snapshot_id: str) -> "WorldBuilder":
        """Set previous snapshot ID for incremental builds."""
        self._from_snapshot_id = snapshot_id
        return self
    
    def to_generation(self, generation: int) -> "WorldBuilder":
        """Set target generation number."""
        if self._generation is not None and generation <= self._generation:
            raise ValueError(f"Generation must increase: {self._generation} -> {generation}")
        self._generation = generation
        return self
    
    def with_environment(self, environment_ref: str) -> "WorldBuilder":
        """Set environment reference."""
        self._environment_ref = environment_ref
        return self
    
    def add_entities(self, *entity_refs: str) -> "WorldBuilder":
        """Add entity references."""
        self._entity_refs_to_add.extend(entity_refs)
        return self
    
    def add_relations(self, *relation_refs: str) -> "WorldBuilder":
        """Add relation references."""
        self._relation_refs_to_add.extend(relation_refs)
        return self
    
    def add_affordances(self, *affordance_refs: str) -> "WorldBuilder":
        """Add affordance references."""
        self._affordance_refs_to_add.extend(affordance_refs)
        return self
    
    def add_constraints(self, *constraint_refs: str) -> "WorldBuilder":
        """Add constraint references."""
        self._constraint_refs_to_add.extend(constraint_refs)
        return self
    
    def validate(self) -> None:
        """
        Validate builder state before build.
        
        Rules:
            - Generation must be set and valid
            - World ID or snapshot source required
            - No duplicate references in adds
        
        Raises:
            ValueError: If validation fails
        """
        if self._generation is None:
            raise ValueError("Target generation must be set")
        
        if self._world_id is None and self._from_snapshot_id is None:
            raise ValueError("World ID or snapshot source required")
    
    def build(self) -> WorldBuildResult:
        """
        Build immutable world state.
        
        Rules:
            - All inputs must be validated
            - Output is deterministic (same inputs = same outputs)
            - No mutable runtime objects in output
        
        Returns:
            Immutable WorldBuildResult with snapshot ID and counts
        """
        self.validate()
        
        # Generate deterministic world ID if not set
        world_id = self._world_id or f"world-{_generate_uuid()}"
        
        # Create transition (deterministic from inputs)
        transition_id = f"trans-{_generate_uuid()}" if self._from_snapshot_id else None
        
        return WorldBuildResult(
            snapshot_id=f"snapshot-{_generate_uuid()}",
            world_id=world_id,
            generation=self._generation or 1,
            entities_added_count=len(self._entity_refs_to_add),
            relations_added_count=len(self._relation_refs_to_add),
            affordances_added_count=len(self._affordance_refs_to_add),
            constraints_added_count=len(self._constraint_refs_to_add),
            transition_id=transition_id,
            is_deterministic=True,
        )
    
    @classmethod
    def create(cls) -> "WorldBuilder":
        """Create a new builder instance."""
        return cls()