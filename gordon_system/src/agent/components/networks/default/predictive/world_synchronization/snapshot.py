# Canonical World Synchronization Snapshot System - Phase 4.9.6
# ==============================================================
"""
Snapshot and revision graph system for WorldModelSynchronization subsystem.

No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class WorldSnapshot:
    """
    Immutable world model snapshot.
    
    Fields:
        snapshot_id:         Unique snapshot identifier
        world_model_ref:     Reference to world model state
        revision_number:     Revision number at snapshot time
        timestamp_ref:       Semantic time reference
        provenance:          Provenance tracking
    
    Rules:
        - Snapshots are immutable once created
        - No modification after creation
        - Complete semantic state preserved
    """
    snapshot_id: str
    world_model_ref: dict[str, Any]  # WorldModel state reference
    revision_number: int = 1
    timestamp_ref: str | None = None
    provenance: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class WorldRevisionGraph:
    """
    Immutable world model revision lineage graph.
    
    Fields:
        root_revision_id:     First revision in lineage
        current_revision_id:  Current/latest revision
        revisions:            All revisions in order
        parent_child_map:     Map of child -> parent revision IDs
    
    Rules:
        - Revision graph is immutable
        - Lineage must be acyclic
        - No modifications after creation
    """
    root_revision_id: str
    current_revision_id: str
    revisions: tuple[str, ...] = field(default_factory=tuple)
    parent_child_map: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SnapshotEngine:
    """
    Engine for creating and managing world snapshots.
    
    Methods:
        create_snapshot:   Create new snapshot from current state
        restore_snapshot:  Restore world to snapshot state
        validate_snapshot: Validate snapshot integrity
    
    Rules:
        - Engine remains immutable
        - All operations return new results
    """
    identity: str = "snapshot_engine"


@dataclass(frozen=True, slots=True)
class RevisionGraphEngine:
    """
    Engine for managing revision lineage graphs.
    
    Methods:
        add_revision:      Add new revision to graph
        get_ancestors:     Get ancestor revisions
        get_descendants:   Get descendant revisions
    
    Rules:
        - Engine remains immutable
        - Graph structure preserved
    """
    identity: str = "revision_graph_engine"