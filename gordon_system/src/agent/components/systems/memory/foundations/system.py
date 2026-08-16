# Memory System - Phase 5.1 Canonical Owner Interface
# =====================================================

"""
Memory System: The exclusive owner of the Memory Substrate.

The Memory System owns:
    - Memory Substrate (persistent semantic medium)
    - Memory Artifacts (semantic units)
    - Memory Relations (graph edges)
    - Memory Identities (stable identifiers)
    - Memory Revisions (versioned evolution)
    - Memory Provenance (origin tracking)
    - Memory Validity (validation states)
    - Memory State (substrate summary)

The Memory System does NOT own:
    - Reasoning
    - Knowledge interpretation
    - Planning
    - Coordination
    - Learning
    - Perception

Memory Laws:
    MEMORY-LAW-001: There shall exist exactly one Memory System
    MEMORY-LAW-002: The Memory System shall own exactly one Memory Substrate
    MEMORY-LAW-003: The Memory System shall remain the exclusive owner of all Memory Artifacts
    MEMORY-LAW-004: Memory ownership shall never be delegated
    MEMORY-LAW-005: Memory shall expose only explicit interfaces and projections
    MEMORY-LAW-006: Memory shall preserve semantic continuity
    MEMORY-LAW-007: Memory shall remain independently testable
    MEMORY-LAW-008: Memory behavior shall remain deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# MEMORY SYSTEM - Owner of the Substrate
# =============================================================================


@dataclass(frozen=True)
class MemorySystem:
    """
    The exclusive owner of Gordon's Memory Substrate.
    
    Responsibilities:
        - Own and maintain the Memory Substrate
        - Provide interfaces for artifact management
        - Expose projections (never expose substrate internals)
        - Validate all changes before application
        - Preserve determinism and history
        
    Never delegates ownership. External components may use Memory via
    projections and queries but never modify artifacts directly.
    
    Fields:
        system_id:         Unique identifier for this memory system instance
        substrate:         The persistent semantic storage (owned by this system)
        
        # Statistics
        artifact_count:    Total artifacts across all revisions
        relation_count:    Total relationships
        
        # Timestamps
        created_at_utc:    When the memory system was initialized
        last_update_utc:   When the last change was made
        
        # State summary
        health_status:     Current health status of the substrate
        integrity_score:   Overall integrity (0.0-1.0)
    """
    
    system_id: str                        # Unique identifier for this instance
    
    # The owned substrate - NEVER exposed directly to consumers
    _substrate: Any = field(default=None)  # MemorySubstrate instance
    
    # Statistics
    artifact_count: int = 0
    relation_count: int = 0
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    last_update_utc: float = field(default_factory=time.time)
    
    # State summary
    health_status: str = "ready"
    integrity_score: float = 1.0
    
    def __post_init__(self):
        """Initialize the memory system after dataclass construction."""
        if self._substrate is None:
            from .substrate import MemorySubstrate
            object.__setattr__(self, "_substrate", MemorySubstrate())
    
    # --------------------------------------------------------------------------
    # Artifact Management (owned operations)
    # --------------------------------------------------------------------------
    
    def insert_artifact(
        self,
        artifact: Any,
    ) -> Tuple[bool, str]:
        """
        Insert a memory artifact into the substrate.
        
        This is the ONLY way to add artifacts. External components must go
        through Memory System - they cannot modify the substrate directly.
        
        Args:
            artifact: The MemoryArtifact to insert
            
        Returns:
            (success, message) tuple
        """
        if self._substrate is None:
            return False, "Memory substrate not initialized"
        
        success, message = self._substrate.insert_artifact(artifact)
        if success:
            # Update statistics
            object.__setattr__(self, "last_update_utc", time.time())
            object.__setattr__(self, "artifact_count", self.artifact_count + 1)
        
        return success, message
    
    def get_artifact(self, artifact_id: str) -> Optional[Any]:
        """
        Retrieve a memory artifact by its ID.
        
        Args:
            artifact_id: The unique identifier of the artifact
            
        Returns:
            The MemoryArtifact if found, None otherwise
        """
        if self._substrate is None:
            return None
        
        return self._substrate.get_artifact(artifact_id)
    
    def get_revision(
        self,
        artifact_id: str,
        revision_number: int,
    ) -> Optional[Any]:
        """
        Retrieve a specific revision of an artifact.
        
        Args:
            artifact_id: The artifact's ID
            revision_number: Which revision (1 = original)
            
        Returns:
            The MemoryArtifact if found, None otherwise
        """
        if self._substrate is None:
            return None
        
        return self._substrate.get_revision(artifact_id, revision_number)
    
    def add_relation(
        self,
        relation: Any,
    ) -> Tuple[bool, str]:
        """
        Add a semantic relationship between artifacts.
        
        Args:
            relation: The MemoryRelation to establish
            
        Returns:
            (success, message) tuple
        """
        if self._substrate is None:
            return False, "Memory substrate not initialized"
        
        success, message = self._substrate.add_relation(relation)
        if success:
            object.__setattr__(self, "last_update_utc", time.time())
            object.__setattr__(self, "relation_count", self.relation_count + 1)
        
        return success, message
    
    # --------------------------------------------------------------------------
    # Projections (exposed interfaces - never substrate internals)
    # --------------------------------------------------------------------------
    
    def get_projection(
        self,
        boundary: Optional[str] = None,
        boundary_value: Optional[str] = None,
    ) -> Any:
        """
        Get an immutable projection of the memory state.
        
        This is how consumers access memory. They NEVER see the substrate
        itself - only projections that represent what they need to know.
        
        Args:
            boundary: Type of boundary (optional)
            boundary_value: Value for boundary type (optional)
            
        Returns:
            MemoryProjection instance
        """
        from .projection import (
            MemoryProjection,
            ProjectionBoundary,
        )
        from .substrate import SubstrateSnapshot
        
        # Get current state
        artifact_ids = self._substrate.get_all_artifact_ids() if self._substrate else tuple()
        
        # Build a simple projection (in real implementation, would include more details)
        return MemoryProjection(
            projection_identity=f"projection:{time.time()}",
            boundary=ProjectionBoundary.GLOBAL,
            projected_artifacts=tuple(artifact_ids),
            projected_revisions={aid: 1 for aid in artifact_ids},
        )
    
    def query(self, query_spec: Any) -> Any:
        """
        Execute a read-only query against the memory substrate.
        
        All queries are:
            - Read-only (never mutate)
            - Deterministic
            - Semantic (work with artifacts, not storage)
        
        Args:
            query_spec: Query specification (MemoryQuery or compatible)
            
        Returns:
            QueryResult with matching items
        """
        from .query import MemoryQuery, MemoryQueryKind
        
        # Determine query type and execute appropriately
        if isinstance(query_spec, MemoryQuery):
            if query_spec.query_kind == MemoryQueryKind.ARTIFACT:
                return self._execute_artifact_query(query_spec.artifact_query)
            elif query_spec.query_kind == MemoryQueryKind.SUBGRAPH:
                return self._execute_subgraph_query(query_spec.subgraph_query)
        
        # Default: get all artifacts
        artifact_ids = tuple(self._substrate.get_all_artifact_ids()) if self._substrate else ()
        
        from .query import QueryResult
        return QueryResult(
            result_id=f"query:{time.time()}",
            results=artifact_ids,
            query_type="default",
            total_count=len(artifact_ids),
        )
    
    def _execute_artifact_query(self, query_spec: Any) -> Any:
        """Execute an artifact query."""
        from .query import QueryResult
        from .substrate import SubstrateSnapshot
        
        # For now, return all artifacts (in real implementation, would filter)
        artifact_ids = tuple(self._substrate.get_all_artifact_ids()) if self._substrate else ()
        
        return QueryResult(
            result_id=f"artifact_query:{time.time()}",
            results=artifact_ids,
            query_type="artifact",
            total_count=len(artifact_ids),
        )
    
    def _execute_subgraph_query(self, query_spec: Any) -> Any:
        """Execute a subgraph query."""
        from .query import QueryResult
        from .substrate import SubstrateSnapshot
        
        root_id = getattr(query_spec, "root_artifact", None)
        if not root_id or self._substrate is None:
            return QueryResult(
                result_id=f"subgraph_query:{time.time()}",
                results=tuple(),
                query_type="subgraph",
                total_count=0,
            )
        
        # Get the subgraph
        artifact_ids, relations = self._substrate.get_subgraph(root_id)
        
        return QueryResult(
            result_id=f"subgraph_query:{time.time()}",
            results=artifact_ids,
            metadata={
                "root_artifact": root_id,
                "relations_count": len(relations),
            },
            query_type="subgraph",
            total_count=len(artifact_ids),
        )
    
    # --------------------------------------------------------------------------
    # Statistics and Health (observability)
    # --------------------------------------------------------------------------
    
    def get_statistics(self) -> Any:
        """Get memory substrate statistics."""
        from .state import MemoryStatistics
        
        return MemoryStatistics(
            artifact_count=self.artifact_count,
            relation_count=self.relation_count,
            integrity=self.integrity_score,
        )
    
    def get_health(self) -> Any:
        """Get memory substrate health status."""
        from .state import MemoryHealth, MemoryState
        
        return MemoryState(
            artifact_count=self.artifact_count,
            relation_count=self.relation_count,
            health_status=MemoryHealth.READY if self.health_status == "ready" else MemoryHealth.DEGRADED,
            integrity=self.integrity_score,
        )
    
    # --------------------------------------------------------------------------
    # Utility methods
    # --------------------------------------------------------------------------
    
    @property
    def substrate_snapshot(self) -> Any:
        """
        Get an immutable snapshot of the current state.
        
        This is for internal use - external consumers should use projections.
        """
        if self._substrate is None:
            from .substrate import SubstrateSnapshot
            return SubstrateSnapshot(
                snapshot_id="empty",
                artifacts=tuple(),
                relations=tuple(),
            )
        
        artifact_ids = tuple(self._substrate.get_all_artifact_ids())
        
        from .substrate import SubstrateSnapshot
        return SubstrateSnapshot(
            snapshot_id=f"snapshot:{time.time()}",
            artifacts=artifact_ids,
            relations=tuple(),  # Relations would be included in full implementation
            semantic_time_utc=self.last_update_utc,
            captured_by="system",
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace_system(instance: MemorySystem, **kwargs) -> MemorySystem:
    """Replace fields in a frozen MemorySystem."""
    return MemorySystem(
        system_id=kwargs.get("system_id", instance.system_id),
        _substrate=kwargs.get("_substrate", instance._substrate),
        artifact_count=kwargs.get("artifact_count", instance.artifact_count),
        relation_count=kwargs.get("relation_count", instance.relation_count),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
        last_update_utc=kwargs.get("last_update_utc", instance.last_update_utc),
        health_status=kwargs.get("health_status", instance.health_status),
        integrity_score=kwargs.get("integrity_score", instance.integrity_score),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemorySystem",
    "dataclass_replace_system",
]