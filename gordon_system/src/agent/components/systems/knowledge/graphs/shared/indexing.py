"""Graph Indexing - Phase 6.8 Part 2.

This module implements the canonical graph indexing contracts according to 
Gordon Cognitive Architecture specifications (Phase 6.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# INDEXING STRATEGY - Phase 6.8 Section 13
# =============================================================================


class IndexingStrategy:
    """
    Indexing strategies for graph access acceleration.
    
    Per INDEX-LAW-001: Indexes shall remain auxiliary structures.
    Per INDEX-LAW-002: Indexes shall never become semantic authority.
    
    Strategy kinds:
        NODE        -> Node identity index
        RELATION    -> Relation identity index
        CONCEPT     -> Concept lookup index
        BELIEF      -> Belief lookup index
        SEMANTIC    -> Semantic similarity index
        
    Indexes remain auxiliary and never replace the canonical graph structure.
    """
    
    NODE = "node"
    RELATION = "relation"
    CONCEPT = "concept"
    BELIEF = "belief"
    SEMANTIC = "semantic"
    
    ALL = {NODE, RELATION, CONCEPT, BELIEF, SEMANTIC}


# =============================================================================
# GRAPH INDEX ENTRY - Phase 6.8 Section 14
# =============================================================================


@dataclass(frozen=True)
class GraphIndexEntry:
    """
    Entry in a graph index.
    
    Per INDEX-LAW-005: Index invalidation shall remain explicit.
    Per INDEX-LAW-007: Indexes shall remain independently inspectable.
    
    Fields:
        entry_identity: Unique identifier for this index entry
        indexed_artifact: Identity of the artifact being indexed
        index: Index key(s) for lookup
        lookup_keys: Keys that can be used to find this entry
        revision: Revision number of indexed artifact
        
    Index entries are auxiliary and preserve semantic identity.
    """
    
    # Core identity
    entry_identity: str  # Unique entry identifier
    
    # Indexed artifact reference
    indexed_artifact: Dict[str, Any] = field(default_factory=dict)
    
    # Index keys (required for lookup)
    index: Tuple[str, ...] = field(default_factory=tuple)
    
    # Lookup keys
    lookup_keys: Tuple[str, ...] = field(default_factory=tuple)
    
    # Revision tracking
    revision: int = 1
    
    # Provenance (required per INDEX-LAW-004, INDEX-LAW-005)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate entry after creation."""
        if not self.entry_identity:
            raise ValueError("entry_identity cannot be empty")
    
    @property
    def is_valid(self) -> bool:
        """Check if entry has valid foundational data."""
        return (
            len(self.entry_identity) > 0 and
            "referenced_identity" in self.indexed_artifact
        )
    
    @classmethod
    def create_initial(
        cls,
        artifact_id: str,
        index_keys: Optional[List[str]] = None,
        lookup_keys: Optional[List[str]] = None,
    ) -> "GraphIndexEntry":
        """
        Create a new index entry.
        
        Args:
            artifact_id: Identity of the artifact being indexed
            index_keys: Keys for primary indexing (optional)
            lookup_keys: Additional keys for lookup (optional)
            
        Returns:
            New GraphIndexEntry with unique identity
        """
        entry_id = f"index_entry:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Index entry creation",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [entry_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            entry_identity=entry_id,
            indexed_artifact={"referenced_identity": artifact_id},
            index=tuple(index_keys or []),
            lookup_keys=tuple(lookup_keys or []),
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for serialization."""
        return {
            "entry_identity": self.entry_identity,
            "indexed_artifact": dict(self.indexed_artifact),
            "index": list(self.index),
            "lookup_keys": list(self.lookup_keys),
            "revision": self.revision,
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphIndexEntry":
        """Create entry from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            entry_identity=data.get("entry_identity", str(uuid.uuid4())),
            indexed_artifact=dict(data.get("indexed_artifact", {})),
            index=tuple(data.get("index", [])),
            lookup_keys=tuple(data.get("lookup_keys", [])),
            revision=int(data.get("revision", 1)),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )


# =============================================================================
# GRAPH INDEX - Phase 6.8 Section 13
# =============================================================================


@dataclass(frozen=True)
class GraphIndex:
    """
    Index for accelerating graph access.
    
    Per INDEX-LAW-001: Indexes shall remain auxiliary structures.
    Per INDEX-LAW-002: Indexes shall never become semantic authority.
    Per INDEX-LAW-003: Index revisions shall preserve history.
    
    Fields:
        index_identity: Unique identifier for this index
        indexed_graph: Graph being indexed
        indexing_strategy: Strategy used for indexing
        supported_queries: Queries the index can accelerate
        
    Indexes never become semantic authority (INDEX-LAW-002).
    """
    
    # Core identity
    index_identity: str  # Unique index identifier
    
    # Indexed graph reference
    indexed_graph: Dict[str, Any] = field(default_factory=dict)
    
    # Strategy (required per INDEX-LAW-003)
    indexing_strategy: Tuple[str, ...] = field(default_factory=tuple)
    
    # Supported query types
    supported_queries: Tuple[str, ...] = field(default_factory=tuple)
    
    # Index entries (the actual indexed data)
    entries: Tuple[GraphIndexEntry, ...] = field(default_factory=tuple)
    
    # Provenance (required per INDEX-LAW-004)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate index after creation."""
        if not self.index_identity:
            raise ValueError("index_identity cannot be empty")
    
    @property
    def is_valid(self) -> bool:
        """Check if index has valid foundational data."""
        return len(self.index_identity) > 0
    
    @classmethod
    def create_initial(
        cls,
        graph_id: str,
        indexing_strategies: Optional[List[str]] = None,
        supported_queries: Optional[List[str]] = None,
    ) -> "GraphIndex":
        """
        Create a new initial graph index.
        
        Args:
            graph_id: ID of the graph being indexed
            indexing_strategies: Strategies to use (optional)
            supported_queries: Query types to support (optional)
            
        Returns:
            New GraphIndex with unique identity
        """
        index_id = f"graph_index:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Graph index initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [index_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            index_identity=index_id,
            indexed_graph={"graph_identity": graph_id},
            indexing_strategy=tuple(indexing_strategies or []),
            supported_queries=tuple(supported_queries or []),
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert index to dictionary for serialization."""
        return {
            "index_identity": self.index_identity,
            "indexed_graph": dict(self.indexed_graph),
            "indexing_strategy": list(self.indexing_strategy),
            "supported_queries": list(self.supported_queries),
            "entries": [e.to_dict() for e in self.entries],
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphIndex":
        """Create index from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        entries = []
        for e_data in data.get("entries", []):
            if isinstance(e_data, dict):
                entries.append(GraphIndexEntry.from_dict(e_data))
        
        return cls(
            index_identity=data.get("index_identity", str(uuid.uuid4())),
            indexed_graph=dict(data.get("indexed_graph", {})),
            indexing_strategy=tuple(data.get("indexing_strategy", [])),
            supported_queries=tuple(data.get("supported_queries", [])),
            entries=tuple(entries),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def add_entry(self, entry: GraphIndexEntry) -> "GraphIndex":
        """Add an index entry and return new index."""
        if any(e.entry_identity == entry.entry_identity for e in self.entries):
            return self
        
        return GraphIndex(
            index_identity=self.index_identity,
            indexed_graph=self.indexed_graph,
            indexing_strategy=self.indexing_strategy,
            supported_queries=self.supported_queries,
            entries=tuple(list(self.entries) + [entry]),
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added index entry: {entry.entry_identity}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.index_identity] if self.provenance else [self.index_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def invalidate(self, reason: str) -> "GraphIndex":
        """Mark index as invalidated."""
        return GraphIndex(
            index_identity=self.index_identity,
            indexed_graph=self.indexed_graph,
            indexing_strategy=self.indexing_strategy,
            supported_queries=self.supported_queries,
            entries=(),
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Index invalidated: {reason}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.index_identity] if self.provenance else [self.index_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Indexing strategy (Phase 6.8 Section 13)
    "IndexingStrategy",
    # Graph index entry (Phase 6.8 Section 14)
    "GraphIndexEntry",
    # Graph index (Phase 6.8 Section 13)
    "GraphIndex",
]