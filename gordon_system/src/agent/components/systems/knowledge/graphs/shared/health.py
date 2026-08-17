"""Graph Health - Phase 6.8 Part 2.

This module implements the canonical graph health metrics according to 
Gordon Cognitive Architecture specifications (Phase 6.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# HEALTH METRICS - Phase 6.8 Section 24
# =============================================================================


@dataclass(frozen=True)
class HealthMetrics:
    """
    Metrics describing graph health.
    
    Per TOPOLOGY-LAW-005: Topology validation shall remain inspectable.
    Per VALIDATION-LAW-007: Validation shall remain independently inspectable.
    Per GOVERNANCE-LAW-008: Equivalent graph states shall produce equivalent governance evaluations.
    
    Metrics:
        node_count: Total number of nodes in the graph
        edge_count: Total number of edges in the graph
        average_degree: Average connections per node
        connected_components: Number of disconnected components
        density: Edge count relative to maximum possible
        isolation_score: Proportion of isolated nodes
        redundancy_score: Proportion of redundant structures
        ontology_consistency: Consistency with declared ontology
        belief_consistency: Consistency of belief statements
        
    Health remains descriptive - it doesn't prescribe changes.
    """
    
    # Graph statistics
    node_count: int = 0
    edge_count: int = 0
    
    # Topological metrics
    average_degree: float = 0.0
    connected_components: int = 1
    density: float = 0.0
    
    # Quality metrics
    isolation_score: float = 0.0  # Lower is better (0 = no isolated nodes)
    redundancy_score: float = 0.0  # Lower is better (0 = no redundancy)
    
    # Semantic consistency
    ontology_consistency: float = 1.0  # Higher is better (1 = fully consistent)
    belief_consistency: float = 1.0  # Higher is better (1 = all beliefs consistent)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "average_degree": self.average_degree,
            "connected_components": self.connected_components,
            "density": self.density,
            "isolation_score": self.isolation_score,
            "redundancy_score": self.redundancy_score,
            "ontology_consistency": self.ontology_consistency,
            "belief_consistency": self.belief_consistency,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HealthMetrics:
        """Create metrics from dictionary."""
        return cls(
            node_count=int(data.get("node_count", 0)),
            edge_count=int(data.get("edge_count", 0)),
            average_degree=float(data.get("average_degree", 0.0)),
            connected_components=int(data.get("connected_components", 1)),
            density=float(data.get("density", 0.0)),
            isolation_score=float(data.get("isolation_score", 0.0)),
            redundancy_score=float(data.get("redundancy_score", 0.0)),
            ontology_consistency=float(data.get("ontology_consistency", 1.0)),
            belief_consistency=float(data.get("belief_consistency", 1.0)),
        )
    
    def is_healthy(self, thresholds: Optional[Dict[str, float]] = None) -> bool:
        """
        Check if graph health meets threshold requirements.
        
        Args:
            thresholds: Optional dict of metric name to minimum value
                - ontology_consistency >= 0.8 (default)
                - belief_consistency >= 0.8 (default)
                - isolation_score <= 0.1 (default) 
                
        Returns:
            True if health meets all thresholds, False otherwise
        """
        thresholds = thresholds or {}
        
        if self.ontology_consistency < thresholds.get("ontology_consistency", 0.8):
            return False
        
        if self.belief_consistency < thresholds.get("belief_consistency", 0.8):
            return False
        
        if self.isolation_score > thresholds.get("isolation_score", 0.1):
            return False
        
        return True


# =============================================================================
# GRAPH HEALTH - Phase 6.8 Section 24
# =============================================================================


@dataclass(frozen=True)
class GraphHealth:
    """
    Health evaluation of a Knowledge Graph.
    
    Per TOPOLOGY-LAW-005: Topology validation shall remain inspectable.
    Per VALIDATION-LAW-007: Validation shall remain independently inspectable.
    Per GOVERNANCE-LAW-008: Equivalent graph states shall produce equivalent governance evaluations.
    
    Fields:
        health_identity: Unique identifier for this health evaluation
        graph: Graph being evaluated
        metrics: Health metrics values
        diagnostics: Additional diagnostic information
        
    Health remains descriptive - it doesn't modify the graph.
    """
    
    # Core identity
    health_identity: str  # Unique health identifier
    
    # Graph reference
    graph: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics (required per GOVERNANCE-LAW-008)
    metrics: HealthMetrics = field(default_factory=HealthMetrics)
    
    # Diagnostics
    diagnostics: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate health after creation."""
        if not self.health_identity:
            raise ValueError("health_identity cannot be empty")
    
    @property
    def is_valid(self) -> bool:
        """Check if health has valid foundational data."""
        return len(self.health_identity) > 0
    
    @classmethod
    def create_initial(
        cls,
        graph_id: str,
        metrics: Optional[HealthMetrics] = None,
    ) -> "GraphHealth":
        """
        Create a new graph health evaluation.
        
        Args:
            graph_id: ID of the graph to evaluate
            metrics: Initial metrics (optional)
            
        Returns:
            New GraphHealth with unique identity
        """
        health_id = f"health:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Graph health evaluation initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [health_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            health_identity=health_id,
            graph={"graph_identity": graph_id},
            metrics=metrics or HealthMetrics(),
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health to dictionary for serialization."""
        return {
            "health_identity": self.health_identity,
            "graph": dict(self.graph),
            "metrics": self.metrics.to_dict(),
            "diagnostics": [d for d in self.diagnostics],
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphHealth":
        """Create health from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        metrics = None
        metrics_data = data.get("metrics")
        if metrics_data:
            metrics = HealthMetrics.from_dict(metrics_data)
        
        diagnostics = []
        for d_data in data.get("diagnostics", []):
            if isinstance(d_data, dict):
                diagnostics.append(d_data)
        
        return cls(
            health_identity=data.get("health_identity", str(uuid.uuid4())),
            graph=dict(data.get("graph", {})),
            metrics=metrics or HealthMetrics(),
            diagnostics=tuple(diagnostics),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def update_metrics(self, new_metrics: HealthMetrics) -> "GraphHealth":
        """Update health metrics and return new evaluation."""
        return GraphHealth(
            health_identity=self.health_identity,
            graph=self.graph,
            metrics=new_metrics,
            diagnostics=self.diagnostics,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Graph health metrics update",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.health_identity] if self.provenance else [self.health_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def add_diagnostic(self, diagnostic: Dict[str, Any]) -> "GraphHealth":
        """Add a diagnostic and return new evaluation."""
        return GraphHealth(
            health_identity=self.health_identity,
            graph=self.graph,
            metrics=self.metrics,
            diagnostics=tuple(list(self.diagnostics) + [diagnostic]),
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added health diagnostic: {diagnostic.get('category', 'unknown')}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.health_identity] if self.provenance else [self.health_identity],
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
    # Health metrics (Phase 6.8 Section 24)
    "HealthMetrics",
    # Graph health (Phase 6.8 Section 24)
    "GraphHealth",
]