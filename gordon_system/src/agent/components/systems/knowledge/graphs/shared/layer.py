"""Graph Layer - Phase 6.8 Part 2.

This module implements the canonical GraphLayer contract according to 
Gordon Cognitive Architecture specifications (Phase 6.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# LAYER KINDS - Phase 6.8 Section 12
# =============================================================================


class LayerKind:
    """
    Kinds of graph layers.
    
    Per LAYER-LAW-001: Every Layer shall possess explicit semantics.
    
    Layer kinds:
        CONCEPT      -> Concept layer (Concept nodes)
        ASSERTION    -> Assertion layer (Assertion nodes)
        BELIEF       -> Belief layer (Belief nodes)
        MODEL        -> Model layer (Model nodes)
        CAPABILITY   -> Capability layer (Capability nodes)
        EXECUTION    -> Execution layer (Running processes)
    """
    
    CONCEPT = "concept"
    ASSERTION = "assertion"
    BELIEF = "belief"
    MODEL = "model"
    CAPABILITY = "capability"
    EXECUTION = "execution"
    
    ALL = {CONCEPT, ASSERTION, BELIEF, MODEL, CAPABILITY, EXECUTION}


# =============================================================================
# GRAPH LAYER - Phase 6.8 Section 12
# =============================================================================


@dataclass(frozen=True)
class GraphLayer:
    """
    Semantic layer in a multi-layer graph.
    
    Per LAYER-LAW-001: Every Layer shall possess explicit semantics.
    Per LAYER-LAW-002: Artifacts may belong to multiple Layers.
    Per LAYER-LAW-004: Layer revisions shall preserve lineage.
    
    Fields:
        layer_identity: Unique identifier for this layer
        layer_kind: Kind of layer (concept, assertion, belief, etc.)
        participating_nodes: Node identities in this layer
        participating_edges: Edge identities in this layer
        compatibility: Compatibility constraints with other layers
        
    Layers remain independently navigable (LAYER-LAW-007).
    """
    
    # Core identity
    layer_identity: str  # Unique layer identifier
    
    # Layer kind (required per LAYER-LAW-001)
    layer_kind: str
    
    # Participating elements
    participating_nodes: Tuple[str, ...] = field(default_factory=tuple)
    participating_edges: Tuple[str, ...] = field(default_factory=tuple)
    
    # Compatibility constraints
    compatibility: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance (required per LAYER-LAW-004, LAYER-LAW-005)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate layer after creation."""
        if not self.layer_identity:
            raise ValueError("layer_identity cannot be empty")
        if not self.layer_kind or self.layer_kind not in LayerKind.ALL:
            raise ValueError(f"Invalid layer_kind: {self.layer_kind}")
    
    @property
    def is_valid(self) -> bool:
        """Check if layer has valid foundational data."""
        return (
            len(self.layer_identity) > 0 and
            self.layer_kind in LayerKind.ALL
        )
    
    @classmethod
    def create_initial(
        cls,
        layer_kind: str,
    ) -> "GraphLayer":
        """
        Create a new initial graph layer.
        
        Args:
            layer_kind: Kind of layer (concept, assertion, belief, etc.)
            
        Returns:
            New GraphLayer with unique layer_identity
        """
        layer_id = f"layer:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Layer initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [layer_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            layer_identity=layer_id,
            layer_kind=layer_kind,
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert layer to dictionary for serialization."""
        return {
            "layer_identity": self.layer_identity,
            "layer_kind": self.layer_kind,
            "participating_nodes": list(self.participating_nodes),
            "participating_edges": list(self.participating_edges),
            "compatibility": list(self.compatibility),
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphLayer":
        """Create layer from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            layer_identity=data.get("layer_identity", str(uuid.uuid4())),
            layer_kind=data.get("layer_kind", ""),
            participating_nodes=tuple(data.get("participating_nodes", [])),
            participating_edges=tuple(data.get("participating_edges", [])),
            compatibility=tuple(data.get("compatibility", [])),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def add_node(self, node_id: str) -> "GraphLayer":
        """Add a node to this layer and return new layer."""
        if node_id in self.participating_nodes:
            return self
        
        return GraphLayer(
            layer_identity=self.layer_identity,
            layer_kind=self.layer_kind,
            participating_nodes=tuple(set(self.participating_nodes) | {node_id}),
            participating_edges=self.participating_edges,
            compatibility=self.compatibility,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added node {node_id} to layer",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.layer_identity] if self.provenance else [self.layer_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def add_edge(self, edge_id: str) -> "GraphLayer":
        """Add an edge to this layer and return new layer."""
        if edge_id in self.participating_edges:
            return self
        
        return GraphLayer(
            layer_identity=self.layer_identity,
            layer_kind=self.layer_kind,
            participating_nodes=self.participating_nodes,
            participating_edges=tuple(set(self.participating_edges) | {edge_id}),
            compatibility=self.compatibility,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added edge {edge_id} to layer",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.layer_identity] if self.provenance else [self.layer_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )


# =============================================================================
# INTER-LAYER MAPPING - Phase 6.8 Section 9
# =============================================================================


@dataclass(frozen=True)
class InterLayerMapping:
    """
    Mapping between two graph layers.
    
    Per LAYER-LAW-003: Inter-layer mappings shall remain explicit.
    Per LAYER-LAW-005: Layer provenance shall remain complete.
    
    Fields:
        mapping_identity: Unique identifier for this mapping
        source_layer: Source layer identity
        target_layer: Target layer identity
        participating_nodes: Node pairs that are mapped
        mapping_strategy: Strategy used (one-to-one, one-to-many, etc.)
        
    Mappings preserve semantic identity across layers.
    """
    
    # Core identity
    mapping_identity: str  # Unique mapping identifier
    
    # Layer references
    source_layer: str
    target_layer: str
    
    # Mapping content
    participating_nodes: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    
    # Strategy
    mapping_strategy: str = "one_to_one"
    
    # Provenance (required per LAYER-LAW-005)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate mapping after creation."""
        if not self.mapping_identity:
            raise ValueError("mapping_identity cannot be empty")
        if not self.source_layer:
            raise ValueError("source_layer cannot be empty")
        if not self.target_layer:
            raise ValueError("target_layer cannot be empty")
    
    @property
    def is_valid(self) -> bool:
        """Check if mapping has valid foundational data."""
        return (
            len(self.mapping_identity) > 0 and
            len(self.source_layer) > 0 and
            len(self.target_layer) > 0
        )
    
    @classmethod
    def create_initial(
        cls,
        source_layer: str,
        target_layer: str,
        node_pairs: Optional[List[Tuple[str, str]]] = None,
        mapping_strategy: str = "one_to_one",
    ) -> "InterLayerMapping":
        """
        Create a new inter-layer mapping.
        
        Args:
            source_layer: Source layer identity
            target_layer: Target layer identity
            node_pairs: Node pairs to map (optional)
            mapping_strategy: Strategy used for mapping
            
        Returns:
            New InterLayerMapping with unique mapping_identity
        """
        mapping_id = f"mapping:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Inter-layer mapping initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [mapping_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            mapping_identity=mapping_id,
            source_layer=source_layer,
            target_layer=target_layer,
            participating_nodes=tuple(node_pairs or []),
            mapping_strategy=mapping_strategy,
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert mapping to dictionary for serialization."""
        return {
            "mapping_identity": self.mapping_identity,
            "source_layer": self.source_layer,
            "target_layer": self.target_layer,
            "participating_nodes": [list(p) for p in self.participating_nodes],
            "mapping_strategy": self.mapping_strategy,
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InterLayerMapping":
        """Create mapping from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        node_pairs = []
        for np in data.get("participating_nodes", []):
            if isinstance(np, (list, tuple)) and len(np) >= 2:
                node_pairs.append((np[0], np[1]))
        
        return cls(
            mapping_identity=data.get("mapping_identity", str(uuid.uuid4())),
            source_layer=data.get("source_layer", ""),
            target_layer=data.get("target_layer", ""),
            participating_nodes=tuple(node_pairs),
            mapping_strategy=data.get("mapping_strategy", "one_to_one"),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Layer kinds (Phase 6.8 Section 12)
    "LayerKind",
    # Graph layer (Phase 6.8 Section 12)
    "GraphLayer",
    # Inter-layer mapping (Phase 6.8 Section 9)
    "InterLayerMapping",
]