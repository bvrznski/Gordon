# Gordon Phase 5.7.7: Situated World - Canonical Package
# ==========================================================

"""
Canonical Situated World capability for Gordon Consciousness.

This package provides the canonical computational representation of the current
operational environment relative to the active Perspective. It answers:

    "What bounded, current, agent-relative operational world surrounds 
     the active Perspective?"

## Key Principles

* Immutable Snapshots: Once published, world state is never modified.
* Agent-Relative: World representation is bounded by perspective scope.
* Operational: Describes what can be acted upon, not what is known.
* Canonical Authority: Single source of truth for world state.

## Architecture

The Situated World package implements:

* WorldIdentity - Unique identifier for a world state
* EnvironmentReference - Reference to current environment context
* EntityReference - Immutable reference to world entities
* RelationReference - Immutable reference to world relations
* AffordanceReference - Non-authoritative affordance descriptions
* ConstraintReference - Environmental constraints (not policy)

## Separation from Other Capabilities

Situated World is NOT:
* Perception (no sensory processing)
* Memory (no long-term storage)
* Knowledge (no semantic reasoning)
* Working Memory (no active task items)
* Planning (no future state generation)
* Prediction (no outcome forecasting)
* Agency (no action selection)
* Action (no effectors control)
* Perspective (no viewpoint management)
* Runtime State (no live execution objects)

Situated World consumes immutable references from other capabilities and
publishes canonical world snapshots that others reference.

## Usage Pattern

External systems propose world evidence:

    contribution = ContributionEnvelope(...)
    transition = world_engine.propose_contribution(contribution)

Only Situated World validates, organizes, and commits state:

    snapshot = world_engine.publish_snapshot()

Snapshots are immutable publications referenced by other capabilities.
"""

from __future__ import annotations

# Core exports
from gordon_system.src.agent.capabilities.consciousness.situated_world.constants import (
    WORLD_AVAILABLE,
    WORLD_UNAVAILABLE,
    WORLD_STATE_ACTIVE,
    WORLD_STATE_DEGRADED,
    WORLD_STATE_FAILED,
)

from gordon_system.src.agent.capabilities.consciousness.situated_world.exceptions import (
    WorldError,
    WorldStateError,
    WorldTransitionError,
    WorldSnapshotError,
)

# Types and identities
from gordon_system.src.agent.capabilities.consciousness.situated_world.types import (
    WorldId,
    EnvironmentReference,
    EntityReference,
    RelationReference,
    AffordanceReference,
    ConstraintReference,
    SnapshotId,
)

__all__: tuple[str, ...] = (
    # Constants
    "WORLD_AVAILABLE",
    "WORLD_UNAVAILABLE", 
    "WORLD_STATE_ACTIVE",
    "WORLD_STATE_DEGRADED",
    "WORLD_STATE_FAILED",
    # Exceptions
    "WorldError",
    "WorldStateError",
    "WorldTransitionError",
    "WorldSnapshotError",
    # Types
    "WorldId",
    "EnvironmentReference", 
    "EntityReference",
    "RelationReference",
    "AffordanceReference",
    "ConstraintReference",
    "SnapshotId",
)