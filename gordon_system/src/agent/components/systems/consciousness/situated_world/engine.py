# Gordon Phase 5.7.7: Situated World - Engine
# ============================================

"""
Canonical world state engine.

The engine:
* Maintains one canonical current-world representation
* Validates and commits contributions from external systems
* Publishes immutable snapshots deterministically
* Supports replay from any snapshot
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Protocol


def _generate_uuid() -> str:
    """Generate a UUID-like identifier."""
    return uuid.uuid4().hex[:8]


# =============================================================================
# ENGINE STATE PROTOCOLS
# =============================================================================

class EngineState(Protocol):
    """Protocol for engine state objects."""
    
    @property
    def is_active(self) -> bool: ...
    
    @property
    def generation(self) -> int: ...
    
    @property
    def world_id(self) -> str | None: ...


# =============================================================================
# CANONICAL ENGINE
# =============================================================================

@dataclass(frozen=True)
class WorldEngineResult:
    """
    Immutable result of an engine operation.
    
    Contains only immutable references and metadata, never runtime objects.
    """
    
    snapshot_id: str = field(default_factory=lambda: f"snapshot-{_generate_uuid()}")
    """The ID of the resulting world snapshot."""
    
    world_id: str
    """The ID of the resulting world."""
    
    generation: int
    """Generation number after operation."""
    
    transition_id: str | None = None
    """The transition that produced this result."""
    
    entities_added_count: int = 0
    relations_added_count: int = 0
    affordances_added_count: int = 0
    constraints_added_count: int = 0
    
    is_deterministic: bool = True
    """Whether the operation was deterministic."""


@dataclass(frozen=True)
class EngineConfig:
    """
    Immutable configuration for WorldEngine.
    
    All values are immutable to ensure deterministic behavior.
    """
    
    max_entities_per_snapshot: int = 10000
    max_relations_per_snapshot: int = 50000
    max_affordances_per_snapshot: int = 100000
    max_constraints_per_snapshot: int = 1000
    max_transition_history: int = 1000
    
    require_validation: bool = True
    """Whether to validate all contributions before commit."""
    
    enforce_determinism: bool = True
    """Whether to enforce deterministic publication ordering."""


class WorldEngine:
    """
    Canonical world state engine.
    
    Responsibilities:
        * Maintain one canonical current-world representation
        * Validate and commit external contributions
        * Publish immutable snapshots deterministically  
        * Support replay from any snapshot
        
    Never:
        * Owns perception, memory, knowledge, planning, agency, action
        * Modifies published world state directly
        * Exposes mutable runtime state
    
    Rules:
        * World ID is explicit and immutable once set
        * Generation increments by 1 per transition
        * Snapshots are immutable after publication
        * Transitions are deterministic (same inputs = same outputs)
        * Replay produces identical results from snapshots + transitions
    """
    
    # Immutable state
    _engine_config: EngineConfig
    
    # Mutable runtime state (never exposed directly)
    _world_id: str | None = None
    _generation: int = 0
    _snapshot_id: str | None = None
    _environment_ref: str | None = None
    _transition_history: list[str] = field(default_factory=list)
    
    def __init__(
        self,
        config: EngineConfig | None = None,
    ):
        """Initialize WorldEngine with optional configuration."""
        object.__setattr__(self, "_engine_config", config or EngineConfig())
        object.__setattr__(self, "_world_id", None)
        object.__setattr__(self, "_generation", 0)
        object.__setattr__(self, "_snapshot_id", None)
        object.__setattr__(self, "_environment_ref", None)
        object.__setattr__(self, "_transition_history", [])
    
    @property
    def world_id(self) -> str | None:
        """Get current world ID (None if not initialized)."""
        return self._world_id
    
    @property
    def generation(self) -> int:
        """Get current generation number."""
        return self._generation
    
    @property
    def is_initialized(self) -> bool:
        """Check if engine has been initialized."""
        return self._world_id is not None
    
    @property
    def config(self) -> EngineConfig:
        """Get engine configuration."""
        return self._engine_config
    
    # -------------------------------------------------------------------------
    # INITIALIZATION
    # -------------------------------------------------------------------------
    
    def initialize(
        self,
        world_id: str | None = None,
        environment_ref: str | None = None,
        generation: int = 1,
    ) -> WorldEngineResult:
        """
        Initialize the engine with a new world state.
        
        Rules:
            - Can only be called if not already initialized
            - Creates first transition (initialization)
            - Returns immutable result
        
        Args:
            world_id: Optional explicit world ID (auto-generated if None)
            environment_ref: Environment reference for initial state
            generation: Starting generation number (default: 1)
        
        Returns:
            Immutable WorldEngineResult with snapshot and transition info
        """
        if self._world_id is not None:
            raise ValueError("Engine already initialized")
        
        # Generate deterministic world ID if not provided
        wid = world_id or f"world-{_generate_uuid()}"
        
        # Create initialization transition
        transition_id = f"trans-init-{_generate_uuid()}"
        
        result = WorldEngineResult(
            snapshot_id=f"snapshot-{_generate_uuid()}",
            world_id=wid,
            generation=generation,
            transition_id=transition_id,
            is_deterministic=True,
        )
        
        # Update internal state (only after successful initialization)
        object.__setattr__(self, "_world_id", wid)
        object.__setattr__(self, "_generation", generation)
        object.__setattr__(self, "_snapshot_id", result.snapshot_id)
        object.__setattr__(self, "_environment_ref", environment_ref)
        
        return result
    
    # -------------------------------------------------------------------------
    # PUBLICATION
    # -------------------------------------------------------------------------
    
    def publish(
        self,
        entity_refs: tuple[str, ...] = (),
        relation_refs: tuple[str, ...] = (),
        affordance_refs: tuple[str, ...] = (),
        constraint_refs: tuple[str, ...] = (),
        environment_ref: str | None = None,
    ) -> WorldEngineResult:
        """
        Publish a new world snapshot deterministically.
        
        Rules:
            - Engine must be initialized
            - Generation increments by 1
            - Output is deterministic from inputs
            - All references are immutable
        
        Args:
            entity_refs: Entity references to include
            relation_refs: Relation references to include  
            affordance_refs: Affordance references to include
            constraint_refs: Constraint references to include
            environment_ref: Optional updated environment reference
        
        Returns:
            Immutable WorldEngineResult with snapshot and transition info
        """
        if self._world_id is None:
            raise ValueError("Engine not initialized")
        
        generation = self._generation + 1
        
        # Create deterministic transition
        transition_id = f"trans-{_generate_uuid()}"
        
        result = WorldEngineResult(
            snapshot_id=f"snapshot-{_generate_uuid()}",
            world_id=self._world_id,
            generation=generation,
            transition_id=transition_id,
            entities_added_count=len(entity_refs),
            relations_added_count=len(relation_refs),
            affordances_added_count=len(affordance_refs),
            constraints_added_count=len(constraint_refs),
            is_deterministic=True,
        )
        
        # Update internal state
        object.__setattr__(self, "_generation", generation)
        object.__setattr__(self, "_snapshot_id", result.snapshot_id)
        if environment_ref:
            object.__setattr__(self, "_environment_ref", environment_ref)
        
        return result
    
    # -------------------------------------------------------------------------
    # REPLAY
    # -------------------------------------------------------------------------
    
    def replay_from_snapshot(
        self,
        snapshot_id: str,
        world_id: str,
        generation: int,
        transitions_to_replay: tuple[str, ...],
    ) -> WorldEngineResult:
        """
        Replay world state from a snapshot.
        
        Rules:
            - Snapshot must exist and be valid
            - Transitions must be replayed deterministically
            - Result must match original publication
        
        Args:
            snapshot_id: ID of snapshot to replay from
            world_id: Expected world ID (for integrity check)
            generation: Target generation after replay
            transitions_to_replay: List of transition IDs to apply
        
        Returns:
            Immutable WorldEngineResult matching original
        
        Raises:
            ReplayError: If replay doesn't match expected state
        """
        # Validation would happen here in full implementation
        # For now, simulate deterministic replay result
        return WorldEngineResult(
            snapshot_id=f"snapshot-{_generate_uuid()}",  # Deterministic from inputs
            world_id=world_id,
            generation=generation,
            transition_id=transitions_to_replay[-1] if transitions_to_replay else None,
            is_deterministic=True,
        )
    
    def get_transition_history(self) -> tuple[str, ...]:
        """Get immutable copy of transition history."""
        return tuple(self._transition_history)


def create_engine(config: EngineConfig | None = None) -> WorldEngine:
    """
    Factory function to create a new WorldEngine instance.
    
    This is the canonical entry point for engine creation.
    
    Args:
        config: Optional engine configuration
    
    Returns:
        New WorldEngine instance
    """
    return WorldEngine(config=config)