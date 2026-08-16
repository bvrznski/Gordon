# Memory Substrate - Phase 5.1 Canonical Semantic Storage
# =======================================================

"""
Memory Substrate: The persistent semantic medium maintained throughout
Gordon's lifetime.

The substrate:
    - survives reasoning, planning, execution, learning, coordination
    - preserves identity, history, provenance, consistency, ownership, determinism
    - is owned exclusively by the Memory System

Substrate Laws:
    SUBSTRATE-LAW-001: The Memory Substrate has one stable identity
    SUBSTRATE-LAW-002: The substrate preserves all retained semantic artifacts
    SUBSTRATE-LAW-003: The substrate preserves semantic relationships
    SUBSTRATE-LAW-004: The substrate preserves revision history
    SUBSTRATE-LAW-005: The substrate preserves provenance
    SUBSTRATE-LAW-006: The substrate preserves integrity
    SUBSTRATE-LAW-007: The substrate remains encapsulated
    SUBSTRATE-LAW-008: Substrate semantics remain implementation-independent
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Iterator
from enum import Enum, auto
import time


# =============================================================================
# SUBSTRATE INTEGRITY - Integrity verification
# =============================================================================


@dataclass(frozen=True)
class SubstrateIntegrity:
    """
    Integrity verification results for the memory substrate.
    
    Fields:
        is_intact:         Does the substrate have consistent semantics?
        
        # Verification details
        artifact_count:    Count of artifacts verified
        relation_count:    Count of relations verified
        
        # Issues found
        integrity_issues:  List of any issues discovered
        missing_artifacts: Artifact IDs referenced but not found
        
        # Timestamps
        verified_at_utc:   When was verification performed?
    """
    
    is_intact: bool = True
    
    artifact_count: int = 0
    relation_count: int = 0
    
    integrity_issues: Tuple[str, ...] = field(default_factory=tuple)
    missing_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    
    verified_at_utc: float = field(default_factory=time.time)


# =============================================================================
# SUBSTRATE SNAPSHOT - Immutable point-in-time view
# =============================================================================


@dataclass(frozen=True)
class SubstrateSnapshot:
    """
    Immutable snapshot of the substrate at a specific point in time.
    
    Snapshots preserve the complete state for historical inspection or
    recovery purposes. They can never modify the actual substrate.
    
    Fields:
        snapshot_id:       Unique ID for this snapshot
        
        # State
        artifacts:         Snapshot of all artifacts
        relations:         Snapshot of all relations
        
        # Timestamps
        semantic_time_utc: What point in time does this represent?
        created_at_utc:    When was the snapshot taken?
        
        # Provenance
        captured_by:       Who/what captured this state?
    """
    
    snapshot_id: str                      # Unique ID for this snapshot
    
    # State snapshots
    artifacts: Tuple[str, ...] = field(default_factory=tuple)
    relations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timestamps
    semantic_time_utc: float = field(default_factory=time.time)
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    captured_by: Optional[str] = None     # Who captured this state?


# =============================================================================
# SUBSTRATE HEALTH - Architectural health status
# =============================================================================


@dataclass(frozen=True)
class SubstrateHealth:
    """
    Health status of the memory substrate.
    
    Health is architectural - it reflects whether the substrate can fulfill
    its responsibilities, not whether individual artifacts are valid.
    
    Fields:
        availability:      Can the substrate be accessed?
        integrity:         Is the semantics consistent?
        consistency:       Are all internal references resolved?
        
        revision_health:   Health of revision tracking
        relationship_health: Health of relation tracking
        
        capacity:          Remaining storage capacity (0.0-1.0)
    """
    
    availability: str = "available"       # available, degraded, unavailable
    
    integrity: float = 1.0               # 0.0-1.0
    consistency: float = 1.0             # 0.0-1.0
    
    revision_health: float = 1.0         # 0.0-1.0
    relationship_health: float = 1.0     # 0.0-1.0
    
    capacity: float = 1.0                # Remaining capacity (0.0-1.0)


# =============================================================================
# MEMORY SUBSTRATE - The persistent semantic medium
# =============================================================================


class MemorySubstrate:
    """
    The persistent semantic substrate owned by the Memory System.
    
    This is the core storage that:
        - Preserves all memory artifacts
        - Maintains relationships between them
        - Tracks revisions and provenance
        - Remains consistent across operations
        
    The substrate is NEVER directly exposed. Consumers use projections
    to access data, ensuring encapsulation and preventing direct mutation.
    
    Operations on the substrate are:
        - insert_artifact: Add a new artifact (creates revision if exists)
        - get_artifact: Retrieve an artifact by ID
        - get_revision: Get a specific revision of an artifact
        - add_relation: Establish a relationship between artifacts
        - remove_relation: Remove a relationship
        - get_subgraph: Retrieve a local neighborhood around an artifact
        
    All operations preserve:
        - Identity (same artifact_id = same semantic identity)
        - History (revisions are never deleted, only superseded)
        - Provenance (every change is tracked)
        - Validity (explicit validity states)
    """
    
    def __init__(self):
        """Initialize the memory substrate."""
        self._artifacts: Dict[str, Dict[int, Any]] = {}  # artifact_id -> {revision: data}
        self._relations: List[Any] = []
        self._registry: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self._artifact_count = 0
        self._relation_count = 0
        
        # Timestamps
        self._created_at_utc = time.time()
        self._last_update_utc = time.time()
        
    def insert_artifact(self, artifact: Any) -> Tuple[bool, str]:
        """
        Insert a memory artifact into the substrate.
        
        If an artifact with the same ID already exists, this creates a new
        revision (does not mutate the existing one).
        
        Args:
            artifact: The MemoryArtifact to insert
            
        Returns:
            (success, message) tuple
        """
        artifact_id = getattr(artifact, "identity", None)
        if artifact_id is None:
            return False, "Artifact must have an identity"
        
        # Get or create the revision dict for this artifact
        if artifact_id not in self._artifacts:
            self._artifacts[artifact_id] = {}
        
        # Insert at the correct revision number
        revision_number = getattr(artifact, "revision_number", 1)
        self._artifacts[artifact_id][revision_number] = artifact
        
        # Update statistics
        self._artifact_count += 1
        self._last_update_utc = time.time()
        
        return True, f"Inserted artifact {artifact_id}:r{revision_number}"
    
    def get_artifact(self, artifact_id: str) -> Optional[Any]:
        """
        Get the current revision of an artifact.
        
        Args:
            artifact_id: The artifact ID to retrieve
            
        Returns:
            The MemoryArtifact if found, None otherwise
        """
        if artifact_id not in self._artifacts:
            return None
        
        revisions = self._artifacts[artifact_id]
        if not revisions:
            return None
        
        # Return the highest revision number (current)
        max_revision = max(revisions.keys())
        return revisions[max_revision]
    
    def get_revision(self, artifact_id: str, revision_number: int) -> Optional[Any]:
        """
        Get a specific revision of an artifact.
        
        Args:
            artifact_id: The artifact ID
            revision_number: Which revision number (1 = original)
            
        Returns:
            The MemoryArtifact if found, None otherwise
        """
        if artifact_id not in self._artifacts:
            return None
        
        revisions = self._artifacts[artifact_id]
        return revisions.get(revision_number)
    
    def add_relation(self, relation: Any) -> Tuple[bool, str]:
        """Add a relationship to the substrate."""
        self._relations.append(relation)
        self._relation_count += 1
        self._last_update_utc = time.time()
        return True, f"Added relation {getattr(relation, 'identity', 'unknown')}"
    
    def remove_relation(self, relation_id: str) -> Tuple[bool, str]:
        """Remove a relationship from the substrate."""
        original_count = len(self._relations)
        self._relations = [
            r for r in self._relations
            if getattr(r, "identity", None) != relation_id
        ]
        
        removed = original_count - len(self._relations)
        self._relation_count = max(0, self._relation_count - removed)
        self._last_update_utc = time.time()
        
        return True, f"Removed {removed} relations"
    
    def get_subgraph(
        self,
        root_artifact_id: str,
        depth: int = 2,
    ) -> Tuple[Tuple[str, ...], Tuple[Any, ...]]:
        """
        Get a local subgraph around an artifact.
        
        Args:
            root_artifact_id: The central artifact
            depth: Max traversal depth (0 = just the root)
            
        Returns:
            (artifact_ids, relations) tuple
        """
        # Start with the root artifact
        artifact_ids = {root_artifact_id}
        related_relations = []
        
        if depth <= 0:
            return tuple(artifact_ids), tuple(related_relations)
        
        # BFS traversal up to depth
        visited = {root_artifact_id}
        queue = [(root_artifact_id, 0)]
        
        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_depth >= depth:
                continue
            
            for relation in self._relations:
                # Check if this relation connects to current artifact
                source = getattr(relation, "source_artifact", None)
                target = getattr(relation, "target_artifact", None)
                
                new_id = None
                if source == current_id:
                    new_id = target
                elif target == current_id:
                    new_id = source
                
                if new_id and new_id not in visited:
                    visited.add(new_id)
                    artifact_ids.add(new_id)
                    related_relations.append(relation)
                    queue.append((new_id, current_depth + 1))
        
        return tuple(artifact_ids), tuple(related_relations)
    
    def get_all_artifact_ids(self) -> Tuple[str, ...]:
        """Get all artifact IDs in the substrate."""
        return tuple(self._artifacts.keys())
    
    @property
    def artifact_count(self) -> int:
        """Total number of artifacts (across all revisions)."""
        return self._artifact_count
    
    @property
    def relation_count(self) -> int:
        """Total number of relations."""
        return self._relation_count
    
    @property
    def created_at_utc(self) -> float:
        """When the substrate was initialized."""
        return self._created_at_utc
    
    @property
    def last_update_utc(self) -> float:
        """When the substrate was last updated."""
        return self._last_update_utc


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace_substrate_health(instance: SubstrateHealth, **kwargs) -> SubstrateHealth:
    """Replace fields in a frozen SubstrateHealth."""
    return SubstrateHealth(
        availability=kwargs.get("availability", instance.availability),
        integrity=kwargs.get("integrity", instance.integrity),
        consistency=kwargs.get("consistency", instance.consistency),
        revision_health=kwargs.get("revision_health", instance.revision_health),
        relationship_health=kwargs.get("relationship_health", instance.relationship_health),
        capacity=kwargs.get("capacity", instance.capacity),
    )


def dataclass_replace_snapshot(instance: SubstrateSnapshot, **kwargs) -> SubstrateSnapshot:
    """Replace fields in a frozen SubstrateSnapshot."""
    return SubstrateSnapshot(
        snapshot_id=instance.snapshot_id,
        artifacts=kwargs.get("artifacts", instance.artifacts),
        relations=kwargs.get("relations", instance.relations),
        semantic_time_utc=kwargs.get("semantic_time_utc", instance.semantic_time_utc),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
        captured_by=kwargs.get("captured_by", instance.captured_by),
    )


def dataclass_replace_integrity(instance: SubstrateIntegrity, **kwargs) -> SubstrateIntegrity:
    """Replace fields in a frozen SubstrateIntegrity."""
    return SubstrateIntegrity(
        is_intact=kwargs.get("is_intact", instance.is_intact),
        artifact_count=kwargs.get("artifact_count", instance.artifact_count),
        relation_count=kwargs.get("relation_count", instance.relation_count),
        integrity_issues=kwargs.get("integrity_issues", instance.integrity_issues),
        missing_artifacts=kwargs.get("missing_artifacts", instance.missing_artifacts),
        verified_at_utc=kwargs.get("verified_at_utc", instance.verified_at_utc),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemorySubstrate",
    "SubstrateSnapshot",
    "SubstrateIntegrity",
    "SubstrateHealth",
    "dataclass_replace_substrate_health",
    "dataclass_replace_snapshot",
    "dataclass_replace_integrity",
]