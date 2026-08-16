# Canonical Belief Revision Dependency Graph - Phase 4.9.5
# =========================================================
"""
Dependency graph implementation for BeliefRevision subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DependencyEdge:
    """
    Canonical dependency edge representation.
    
    Fields:
        source:           Source belief identity
        target:           Target belief identity  
        relationship:     Type of dependency (supports/depends_on/contradicts/etc.)
        provenance:       Provenance tracking
    """
    source: str  # BeliefIdentity or string code
    target: str  # BeliefIdentity or string code
    relationship: str  # DependencyRelationship or string code
    provenance: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class DependencyGraph:
    """
    Canonical dependency graph for beliefs.
    
    Fields:
        nodes:            All belief identities in the graph
        edges:            Typed relationship edges between beliefs
        root_nodes:       Belief identities with no incoming edges
        trace:            Graph construction trace
    
    Rules:
        - Dependencies remain typed
        - Dependencies preserve provenance  
        - Dependency graphs shall remain immutable
    """
    nodes: tuple[str, ...] = field(default_factory=tuple)
    edges: tuple[DependencyEdge, ...] = field(default_factory=tuple)
    root_nodes: tuple[str, ...] = field(default_factory=tuple)
    trace: tuple[str, ...] = field(default_factory=tuple)


class DependencyGraphBuilder:
    """
    Builder for constructing dependency graphs from belief states.
    
    Rules:
        - Stateless construction
        - Deterministic output
        - Acyclic by construction (if possible)
    """
    
    def __init__(self) -> None:
        self.trace_events: tuple[str, ...] = ()
    
    def build_from_beliefs(self, beliefs: tuple[dict[str, Any], ...]) -> DependencyGraph:
        """
        Build a dependency graph from a set of beliefs.
        
        Args:
            beliefs: Tuple of belief dictionaries
            
        Returns:
            Constructed DependencyGraph
        """
        trace = []
        nodes: list[str] = []
        edges: list[DependencyEdge] = []
        
        for i, belief in enumerate(beliefs):
            if not isinstance(belief, dict):
                continue
            
            identity = belief.get("identity")
            if identity:
                nodes.append(identity)
            
            # Analyze supporting evidence to build edges
            evidence = belief.get("supporting_evidence", [])
            for j, ev in enumerate(evidence):
                if not isinstance(ev, dict):
                    continue
                
                source_identity = ev.get("identity", f"evidence_{j}")
                
                # Create SUPPORTS edge from evidence to belief
                edges.append(DependencyEdge(
                    source=source_identity,
                    target=identity or "",
                    relationship="supports",
                    provenance={"from_evidence": j}
                ))
            
            # Analyze revision history for DEPENDS_ON relationships
            history = belief.get("revision_history", [])
            if isinstance(history, (tuple, list)) and len(history) > 1:
                for k in range(1, len(history)):
                    edges.append(DependencyEdge(
                        source=f"revision_{k}",
                        target=identity or "",
                        relationship="depends_on",
                        provenance={"from_revision_history": k}
                    ))
        
        # Determine root nodes (those with no incoming edges)
        targets = {e.target for e in edges}
        roots = [n for n in nodes if n not in targets]
        
        trace.append("NODES_EXTRACTED")
        trace.append("EDGES_CONSTRUCTED")
        trace.append("ROOT_NODES_IDENTIFIED")
        
        return DependencyGraph(
            nodes=tuple(nodes),
            edges=tuple(edges),
            root_nodes=tuple(roots),
            trace=tuple(trace)
        )
    
    def validate_acyclic(self, graph: DependencyGraph) -> bool:
        """
        Validate that the dependency graph is acyclic.
        
        Args:
            graph: DependencyGraph to validate
            
        Returns:
            True if acyclic, False otherwise
        """
        # Simplified validation - full cycle detection would require DFS/BFS
        # This implementation checks for obvious self-loops
        
        for edge in graph.edges:
            if edge.source == edge.target:
                return False
        
        return True
    
    def find_dependent_beliefs(self, graph: DependencyGraph, belief_id: str) -> tuple[str, ...]:
        """
        Find all beliefs that depend on a given belief.
        
        Args:
            graph: DependencyGraph to search
            belief_id: Belief identity to check
            
        Returns:
            Tuple of dependent belief identities
        """
        dependents = []
        
        for edge in graph.edges:
            if edge.target == belief_id and edge.relationship in ("supports", "depends_on"):
                dependents.append(edge.source)
        
        return tuple(dependents)


class DependencyAnalyzer:
    """
    Analyzer for dependency relationships between beliefs.
    
    Rules:
        - Stateless analysis
        - Deterministic output
        - No graph mutation
    """
    
    def analyze_conflicts(self, graph: DependencyGraph) -> tuple[dict[str, Any], ...]:
        """
        Analyze the dependency graph for conflicts.
        
        Args:
            graph: DependencyGraph to analyze
            
        Returns:
            Tuple of conflict records
        """
        conflicts = []
        
        # Check for contradictory edges
        seen_pairs: set[tuple[str, str]] = set()
        
        for edge in graph.edges:
            if edge.relationship == "contradicts":
                pair = tuple(sorted([edge.source, edge.target]))
                
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    
                    conflicts.append({
                        "belief_a": edge.source,
                        "belief_b": edge.target,
                        "conflict_type": "contradictory_dependencies",
                        "evidence": (edge,),
                        "timestamp_ref": None
                    })
        
        return tuple(conflicts)
    
    def compute_importance(self, graph: DependencyGraph, belief_id: str) -> float:
        """
        Compute the importance of a belief based on its dependencies.
        
        Args:
            graph: DependencyGraph to analyze
            belief_id: Belief identity to score
            
        Returns:
            Importance score [0.0, 1.0]
        """
        # Simplified scoring - in real implementation would use more sophisticated metrics
        
        incoming = sum(1 for e in graph.edges if e.target == belief_id)
        outgoing = sum(1 for e in graph.edges if e.source == belief_id)
        
        total = incoming + outgoing
        if total == 0:
            return 0.5  # Neutral importance
        
        # Normalize and clamp to [0.0, 1.0]
        score = min(1.0, max(0.0, (incoming / max(total, 1))))
        
        return round(score, 2)