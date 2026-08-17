"""Graph Descriptor - Phase 6.8 Part 2.

This module implements the canonical contract for graph metadata and lifecycle
tracking according to Gordon Cognitive Architecture specifications.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# GRAPH KINDS - Phase 6.8 Section 3
# =============================================================================


class GraphKind(Enum):
    """
    Kinds of Knowledge Graphs.
    
    Semantic Organization:
        SEMANTIC      -> Organizes Concepts and Relations
        EPISTEMIC     -> Organizes Assertions, Beliefs, Evidence
        ONTOLOGY      -> Organizes domain ontologies
        DOMAIN        -> Domain-specific graph (Python, Linux, etc.)
        SELF          -> Gordon's self-representation
        WORLD         -> External environment representation
        TASK          -> Task planning graph
        TEMPORAL      -> Time-ordered graphs
        CAUSAL        -> Causality graphs
        MULTI_LAYER   -> Multi-layer graph organization
    
    Special kinds:
        UNKNOWN       -> Unspecified or unrecognized kind
    """
    
    SEMANTIC = "semantic"
    EPISTEMIC = "epistemic"
    ONTOLOGY = "ontology"
    DOMAIN = "domain"
    SELF = "self"
    WORLD = "world"
    TASK = "task"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    MULTI_LAYER = "multi_layer"
    UNKNOWN = "unknown"


# =============================================================================
# GRAPH LIFECYCLE STATES - Phase 6.8 Section 18
# =============================================================================


class GraphLifecycleState(Enum):
    """
    States of graph lifecycle progression.
    
    Progression:
        CREATED     -> Initial creation (not yet validated)
        VALIDATING  -> Under validation review
        ACTIVE      -> Published and in use
        REVISED     -> Has been superseded by newer revision
        SUPERSEDED  -> Replaced by another graph
        ARCHIVED    -> Preserved for historical purposes
        INVALID     -> Failed validation, not for use
    """
    
    CREATED = "created"
    VALIDATING = "validating"
    ACTIVE = "active"
    REVISED = "revised"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
    INVALID = "invalid"


# =============================================================================
# PROVENANCE RECORD - Phase 6.8 LAW-004
# =============================================================================


@dataclass(frozen=True)
class ProvenanceRecord:
    """
    Records the origin and evolution history of a graph.
    
    Per GRAPH-LAW-004: Graphs shall preserve provenance.
    Per GRAPH-LAW-005: Graphs shall preserve revision lineage.
    
    Fields:
        provenance_identity: Unique identifier for this provenance record
        originating_request: Request that triggered this state change
        originating_system: System that originated the change
        originating_revision: Revision number at time of change
        evidence_references: References to supporting evidence
        grounding_references: References to semantic grounding
        revision_chain: Chain of revisions leading to this point
        authority: Authority that approved this change
        timestamp_utc: UTC timestamp of the change
    """
    
    provenance_identity: str
    originating_request: str
    originating_system: str
    originating_revision: int
    evidence_references: List[str]
    grounding_references: List[str]
    revision_chain: List[str]
    authority: str
    timestamp_utc: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert provenance record to dictionary."""
        return {
            "provenance_identity": self.provenance_identity,
            "originating_request": self.originating_request,
            "originating_system": self.originating_system,
            "originating_revision": self.originating_revision,
            "evidence_references": list(self.evidence_references),
            "grounding_references": list(self.grounding_references),
            "revision_chain": list(self.revision_chain),
            "authority": self.authority,
            "timestamp_utc": self.timestamp_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProvenanceRecord:
        """Create provenance record from dictionary."""
        return cls(
            provenance_identity=data.get("provenance_identity", ""),
            originating_request=data.get("originating_request", ""),
            originating_system=data.get("originating_system", "unknown"),
            originating_revision=int(data.get("originating_revision", 1)),
            evidence_references=list(data.get("evidence_references", [])),
            grounding_references=list(data.get("grounding_references", [])),
            revision_chain=list(data.get("revision_chain", [])),
            authority=data.get("authority", ""),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
        )


# =============================================================================
# GRAPH DESCRIPTOR - Phase 6.8 Section 1
# =============================================================================


@dataclass(frozen=True)
class GraphDescriptor:
    """
    Descriptor for a Knowledge Graph.
    
    This is the canonical metadata contract that exposes graph information
    independently of its contents, per Phase 6.8 Part 2 Section 1.
    
    Per GRAPH-LAW-001: Every Knowledge Graph shall possess one immutable Semantic Identity.
    Per GRAPH-LAW-002: Graphs shall organize semantic artifacts only.
    Per GRAPH-LAW-003: Graphs shall preserve semantic identities of all referenced artifacts.
    Per GRAPH-LAW-004: Graphs shall preserve provenance.
    Per GRAPH-LAW-005: Graphs shall preserve revision lineage.
    
    Fields:
        graph_identity: Unique identifier for this graph
        semantic_identity: Semantic identity the graph represents
        graph_kind: Kind of graph (semantic, epistemic, etc.)
        lifecycle_state: Current state in the lifecycle progression
        graph_revision: Current revision number
        publication_status: Availability status
        provenance: Complete origin and evolution trail
        
    Invariants:
        * graph_identity remains immutable once created
        * semantic_identity uniquely identifies the represented knowledge
        * All references to artifacts preserve their semantic identities
    """
    
    # Core identity (required - immutable per GRAPH-LAW-001)
    graph_identity: str  # Unique graph identifier
    
    # Semantic identity (required)
    semantic_identity: str  # Identity of represented knowledge
    
    # Graph kind (required)
    graph_kind: GraphKind
    
    # Lifecycle tracking (required)
    lifecycle_state: GraphLifecycleState
    graph_revision: int = 1
    
    # Publication status
    publication_status: str = "private"
    
    # Provenance (required per GRAPH-LAW-004, GRAPH-LAW-005)
    provenance: Tuple[ProvenanceRecord, ...] = field(default_factory=tuple)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Graph properties
    node_count: int = 0
    edge_count: int = 0
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate descriptor after creation."""
        if not self.graph_identity:
            raise ValueError("graph_identity cannot be empty")
        if not self.semantic_identity:
            raise ValueError("semantic_identity cannot be empty")
        if self.graph_revision < 1:
            raise ValueError("graph_revision must be >= 1")
    
    @property
    def is_valid(self) -> bool:
        """Check if descriptor has valid foundational data."""
        return (
            len(self.graph_identity) > 0 and
            len(self.semantic_identity) > 0 and
            self.lifecycle_state is not None and
            self.graph_kind is not None
        )
    
    @property
    def has_provenance(self) -> bool:
        """Check if graph has provenance records."""
        return len(self.provenance) > 0
    
    @classmethod
    def create_initial(
        cls,
        semantic_identity: str,
        graph_kind: GraphKind,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "GraphDescriptor":
        """
        Create a new initial graph descriptor.
        
        Args:
            semantic_identity: Semantic identity of the represented knowledge
            graph_kind: Kind of graph to create
            metadata: Additional graph metadata (optional)
            
        Returns:
            New GraphDescriptor in CREATED lifecycle state with revision 1
            
        This method creates the initial version of a graph, setting up:
            - Unique graph_identity
            - Initial provenance record
            - Created_at timestamp
            - LifecycleState.CREATED state
            - Revision 1
        """
        graph_id = f"graph:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            ProvenanceRecord(
                provenance_identity=f"provenance:{uuid.uuid4().hex[:16]}",
                originating_request="Graph initialization",
                originating_system="knowledge-graph-system",
                originating_revision=1,
                evidence_references=[],
                grounding_references=[],
                revision_chain=[graph_id],
                authority="system",
                timestamp_utc=time.time(),
            ),
        )
        
        return cls(
            graph_identity=graph_id,
            semantic_identity=semantic_identity,
            graph_kind=graph_kind,
            lifecycle_state=GraphLifecycleState.CREATED,
            graph_revision=1,
            publication_status="private",
            provenance=initial_provenance,
            metadata=metadata or {},
            created_at_utc=time.time(),
        )
    
    def with_revision(
        self,
        new_revision: int,
        change_summary: Optional[str] = None,
    ) -> "GraphDescriptor":
        """
        Create a new revision of this graph descriptor.
        
        Args:
            new_revision: The revision number
            change_summary: Brief description of changes (optional)
            
        Returns:
            New GraphDescriptor with updated revision
            
        Per GRAPH-LAW-004: Provenance is preserved across revisions.
        Per GRAPH-LAW-005: Revision lineage is maintained.
        """
        new_provenance = tuple(list(self.provenance) + [
            ProvenanceRecord(
                provenance_identity=f"provenance:{uuid.uuid4().hex[:16]}",
                originating_request=f"Revision {new_revision}: {change_summary or 'unknown change'}",
                originating_system="knowledge-graph-system",
                originating_revision=new_revision,
                evidence_references=[],
                grounding_references=[],
                revision_chain=list(self.provenance[-1].revision_chain) + [self.graph_identity] if self.provenance else [self.graph_identity],
                authority=self.metadata.get("authority", "system"),
                timestamp_utc=time.time(),
            ),
        ])
        
        return GraphDescriptor(
            graph_identity=self.graph_identity,
            semantic_identity=self.semantic_identity,
            graph_kind=self.graph_kind,
            lifecycle_state=self.lifecycle_state,
            graph_revision=new_revision,
            publication_status=self.publication_status,
            provenance=new_provenance,
            metadata=self.metadata.copy(),
            node_count=self.node_count,
            edge_count=self.edge_count,
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert descriptor to dictionary for serialization."""
        return {
            "graph_identity": self.graph_identity,
            "semantic_identity": self.semantic_identity,
            "graph_kind": self.graph_kind.value,
            "lifecycle_state": self.lifecycle_state.value,
            "graph_revision": self.graph_revision,
            "publication_status": self.publication_status,
            "provenance": [p.to_dict() for p in self.provenance],
            "metadata": dict(self.metadata),
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphDescriptor":
        """Create descriptor from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(ProvenanceRecord.from_dict(p_data))
        
        return cls(
            graph_identity=data.get("graph_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            graph_kind=GraphKind(data.get("graph_kind", "unknown")),
            lifecycle_state=GraphLifecycleState(data.get("lifecycle_state", "created")),
            graph_revision=int(data.get("graph_revision", 1)),
            publication_status=data.get("publication_status", "private"),
            provenance=tuple(provenance),
            metadata=dict(data.get("metadata", {})),
            node_count=int(data.get("node_count", 0)),
            edge_count=int(data.get("edge_count", 0)),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def update_metadata(self, key: str, value: Any) -> "GraphDescriptor":
        """Update a metadata field and return new descriptor."""
        new_metadata = self.metadata.copy()
        new_metadata[key] = value
        return GraphDescriptor(
            graph_identity=self.graph_identity,
            semantic_identity=self.semantic_identity,
            graph_kind=self.graph_kind,
            lifecycle_state=self.lifecycle_state,
            graph_revision=self.graph_revision + 1,
            publication_status=self.publication_status,
            provenance=tuple(list(self.provenance) + [
                ProvenanceRecord(
                    provenance_identity=f"provenance:{uuid.uuid4().hex[:16]}",
                    originating_request=f"Metadata update: {key}",
                    originating_system="knowledge-graph-system",
                    originating_revision=self.graph_revision + 1,
                    evidence_references=[],
                    grounding_references=[],
                    revision_chain=list(self.provenance[-1].revision_chain) + [self.graph_identity] if self.provenance else [self.graph_identity],
                    authority=self.metadata.get("authority", "system"),
                    timestamp_utc=time.time(),
                ),
            ]),
            metadata=new_metadata,
            node_count=self.node_count,
            edge_count=self.edge_count,
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Graph kinds (Phase 6.8 Section 3)
    "GraphKind",
    # Lifecycle states (Phase 6.8 Section 18)
    "GraphLifecycleState",
    # Provenance record (Phase 6.8 LAW-004, LAW-005)
    "ProvenanceRecord",
    # Graph descriptor (Phase 6.8 Section 1)
    "GraphDescriptor",
]