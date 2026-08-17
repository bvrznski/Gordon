# Gordon Phase 5.7.7: Situated World - Types
# ===========================================

"""
Canonical type definitions for the Situated World capability.

Types are immutable by design and use frozen dataclasses to ensure:
* Deterministic publication (same inputs = same outputs)
* Replayability (state can be recreated from references)
* Concurrency safety (no mutable shared state)
"""

from __future__ import annotations

from dataclasses import dataclass, field
import uuid


def _generate_uuid() -> str:
    """Generate a deterministic UUID-like identifier."""
    return uuid.uuid4().hex[:8]


# =============================================================================
# WORLD IDENTITIES
# =============================================================================

@dataclass(frozen=True)
class WorldId:
    """
    Unique identifier for a Situated World state.
    
    Rules:
        - Must be globally unique across all agents and sessions
        - Generated deterministically from environment + generation
        - Immutable once created (no modification allowed)
    """
    
    value: str = field(default_factory=lambda: f"world-{_generate_uuid()}")
    """The UUID value of this world identity."""
    
    @classmethod
    def from_environment_and_generation(
        cls, 
        environment_id: str,
        generation: int,
    ) -> "WorldId":
        """
        Create a WorldId deterministically from environment and generation.
        
        This ensures equivalent environments at the same generation produce
        identical WorldIds, enabling replayability.
        """
        return cls(value=f"world-{environment_id}-gen{generation}")


@dataclass(frozen=True)
class SnapshotId:
    """
    Unique identifier for a world snapshot.
    
    Rules:
        - Tied to specific WorldId and generation
        - Immutable once created
        - Enables replay from any point in time
    """
    
    value: str = field(default_factory=lambda: f"snapshot-{_generate_uuid()}")
    """The UUID value of this snapshot."""
    
    world_id: str | None = None
    """Reference to the world this snapshot represents (if known)."""
    
    generation: int = 0
    """Generation number at time of snapshot."""
    
    timestamp_ref: str | None = None
    """Semantic time reference for when snapshot was taken."""


# =============================================================================
# ENVIRONMENT REFERENCES
# =============================================================================

@dataclass(frozen=True)
class EnvironmentReference:
    """
    Immutable reference to an environment context.
    
    This is a bounded view of the current operational environment - not
    a full representation, just what's needed for world state determination.
    """
    
    environment_id: str
    """Unique identifier for this environment."""
    
    type: str = "physical"
    """Environment type (physical, desktop, application, etc.)."""
    
    spatial_bounds: tuple[tuple[float, float], tuple[float, float]] | None = None
    """Spatial bounds as ((min_x, min_y), (max_x, max_y))."""
    
    temporal_window: tuple[str, str] | None = None
    """Temporal window as (start_ref, end_ref) semantic time references."""
    
    scope: tuple[str, ...] = field(default_factory=tuple)
    """Additional scope identifiers for this environment."""


# =============================================================================
# ENTITY REFERENCES
# =============================================================================

@dataclass(frozen=True)
class EntityReference:
    """
    Immutable reference to an entity in the world.
    
    This is a canonical identity - not the full entity state. External systems
    can reference entities without accessing their full representation.
    """
    
    entity_id: str
    """Unique identifier for this entity."""
    
    kind: str = "entity"
    """Kind of entity (for type checking)."""
    
    environment_ref: str | None = None
    """Environment this entity belongs to."""
    
    generation_created: int = 0
    """Generation when entity was first created."""
    
    provenance: str | None = None
    """Source that proposed/provided this entity."""
    
    @classmethod
    def create(
        cls,
        entity_id: str,
        environment_ref: str | None = None,
        generation_created: int = 0,
        provenance: str | None = None,
    ) -> "EntityReference":
        """
        Create an EntityReference with validation.
        
        Rules:
            - entity_id must be non-empty
            - environment_ref, if present, must be valid
            - provenance tracks source but doesn't grant authority
        """
        if not entity_id or not isinstance(entity_id, str):
            raise ValueError("entity_id must be a non-empty string")
        
        return cls(
            entity_id=entity_id,
            kind="entity",
            environment_ref=environment_ref,
            generation_created=generation_created,
            provenance=provenance,
        )


# =============================================================================
# RELATION REFERENCES
# =============================================================================

@dataclass(frozen=True)
class RelationReference:
    """
    Immutable reference to a relation between entities.
    
    Relations represent semantic connections between entities. They are:
    * Typed (has a specific kind of relationship)
    * Directional (source -> target)
    * Immutable (once published, never modified)
    """
    
    relation_id: str
    """Unique identifier for this relation."""
    
    source_entity_ref: EntityReference
    """Source entity reference."""
    
    target_entity_ref: EntityReference
    """Target entity reference."""
    
    kind: str = "related_to"
    """Kind/type of relation (e.g., 'part_of', 'causes', 'affects')."""
    
    provenance: str | None = None
    """Source that proposed this relation."""
    
    @classmethod
    def create(
        cls,
        source_entity_ref: EntityReference,
        target_entity_ref: EntityReference,
        kind: str = "related_to",
        provenance: str | None = None,
    ) -> "RelationReference":
        """
        Create a RelationReference with validation.
        
        Rules:
            - Source and target must be different entities
            - Kind should be from known relation types
            - Provenance tracks source but doesn't grant authority
        """
        if source_entity_ref.entity_id == target_entity_ref.entity_id:
            raise ValueError("Source and target cannot be the same entity")
        
        return cls(
            relation_id=f"rel-{source_entity_ref.entity_id[:8]}-{target_entity_ref.entity_id[:8]}",
            source_entity_ref=source_entity_ref,
            target_entity_ref=target_entity_ref,
            kind=kind,
            provenance=provenance,
        )


# =============================================================================
# AFFORDANCE REFERENCES
# =============================================================================

@dataclass(frozen=True)
class AffordanceReference:
    """
    Reference to a possible interaction affordance.
    
    Affordances describe what actions are *possible* in the current world state,
    not what is authorized. They never grant action authority.
    
    Rules:
        - Describes possibility, not permission
        - Requires preconditions that must be satisfied
        - Context-dependent (only valid for specific environment)
    """
    
    affordance_id: str
    """Unique identifier for this affordance."""
    
    possible_action: str
    """Description of the possible action."""
    
    required_preconditions: tuple[str, ...] = field(default_factory=tuple)
    """Precondition references that must be satisfied."""
    
    expected_effects: tuple[str, ...] = field(default_factory=tuple)
    """Expected outcome references if action is performed."""
    
    context_ref: str | None = None
    """Environment/context where this affordance applies."""
    
    @classmethod
    def create(
        cls,
        possible_action: str,
        context_ref: str | None = None,
        required_preconditions: tuple[str, ...] | None = None,
        expected_effects: tuple[str, ...] | None = None,
    ) -> "AffordanceReference":
        """
        Create an AffordanceReference.
        
        Rules:
            - Possible action must be specified
            - Preconditions and effects describe conditions/outcomes
            - Affordances never authorize actions
        """
        if not possible_action:
            raise ValueError("possible_action must be non-empty")
        
        return cls(
            affordance_id=f"aff-{_generate_uuid()}",
            possible_action=possible_action,
            required_preconditions=required_preconditions or (),
            expected_effects=expected_effects or (),
            context_ref=context_ref,
        )


# =============================================================================
# CONSTRAINT REFERENCES
# =============================================================================

@dataclass(frozen=True)
class ConstraintReference:
    """
    Reference to an environmental constraint.
    
    Constraints represent limitations on the current world. They are NOT
    policy decisions, but rather descriptions of what is currently possible.
    
    Categories:
        - environmental: Physical/biological limitations
        - policy: References to external policy (not enforcement)
        - security: Authorization-related (not enforcement)
    """
    
    constraint_id: str
    """Unique identifier for this constraint."""
    
    kind: str = "environmental"
    """Constraint category (environmental, policy, security)."""
    
    description: str
    """Human-readable description of the constraint."""
    
    scope: tuple[str, ...] = field(default_factory=tuple)
    """Entities/contexts this constraint applies to."""
    
    @classmethod
    def create(
        cls,
        kind: str,
        description: str,
        scope: tuple[str, ...] | None = None,
    ) -> "ConstraintReference":
        """
        Create a ConstraintReference.
        
        Rules:
            - Kind must be from valid categories
            - Description explains what is constrained
            - Scope identifies affected entities/contexts
        """
        if kind not in ("environmental", "policy", "security"):
            raise ValueError(f"Invalid constraint kind: {kind}")
        
        return cls(
            constraint_id=f"c-{_generate_uuid()}",
            kind=kind,
            description=description,
            scope=scope or (),
        )


# =============================================================================
# WORLD STATE METADATA
# =============================================================================

@dataclass(frozen=True)
class WorldMetadata:
    """
    Metadata about the world state for observability.
    
    This provides operational insights without exposing private content.
    Safe for monitoring and diagnostics systems.
    """
    
    entity_count: int = 0
    """Number of entities in current world state."""
    
    relation_count: int = 0
    """Number of relations in current world state."""
    
    affordance_count: int = 0
    """Number of affordances in current world state."""
    
    constraint_count: int = 0
    """Number of constraints in current world state."""
    
    last_transition_id: str | None = None
    """Last transition that modified this world state."""
    
    health_state: str = "active"
    """Current health state (active, degraded, failed)."""
    
    generation: int = 1
    """Current generation number."""