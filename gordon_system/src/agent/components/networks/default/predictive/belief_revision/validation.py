# Canonical Belief Revision Validation - Phase 4.9.5
# ====================================================
"""
Validation logic for BeliefRevision subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    Canonical validation result.
    
    Fields:
        is_valid:           Whether the validated object is valid
        errors:             List of error messages
        warnings:           List of warning messages
        trace:              Validation trace events
    """
    is_valid: bool = False
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    trace: tuple[str, ...] = field(default_factory=tuple)


class BeliefRevisionValidator:
    """
    Canonical validator for belief revision components.
    
    Rules:
        - Stateless validation
        - Side-effect free
        - Deterministic output
    """
    
    def __init__(self) -> None:
        self.trace_events: tuple[str, ...] = ()
    
    def validate_request(self, request: dict[str, Any]) -> ValidationResult:
        """Validate a BeliefRevisionRequest."""
        trace = []
        
        if not isinstance(request, dict):
            return ValidationResult(
                is_valid=False,
                errors=("Request must be a dictionary",),
                trace=tuple(trace)
            )
        
        if "belief_state" not in request:
            return ValidationResult(
                is_valid=False,
                errors=("BeliefState is required in request",),
                trace=tuple(trace)
            )
        
        trace.append("REQUEST_TYPE_VALID")
        
        # Validate belief state
        belief_state = request.get("belief_state", {})
        if not isinstance(belief_state, dict):
            return ValidationResult(
                is_valid=False,
                errors=("BeliefState must be a dictionary",),
                trace=tuple(trace)
            )
        
        trace.append("BELIEF_STATE_TYPE_VALID")
        
        # Validate precision landscape
        precision_landscape = request.get("precision_landscape", {})
        if not isinstance(precision_landscape, dict):
            return ValidationResult(
                is_valid=False,
                errors=("PrecisionLandscape must be a dictionary",),
                trace=tuple(trace)
            )
        
        trace.append("PRECISION_LANDSCAPE_TYPE_VALID")
        
        return ValidationResult(
            is_valid=True,
            trace=tuple(trace)
        )
    
    def validate_belief_state(self, state: dict[str, Any]) -> ValidationResult:
        """Validate a BeliefState."""
        trace = []
        
        if not isinstance(state, dict):
            return ValidationResult(
                is_valid=False,
                errors=("BeliefState must be a dictionary",),
                trace=tuple(trace)
            )
        
        # Validate beliefs
        beliefs = state.get("beliefs", [])
        if not isinstance(beliefs, (tuple, list)):
            return ValidationResult(
                is_valid=False,
                errors=("Beliefs must be a tuple or list",),
                trace=tuple(trace)
            )
        
        state_beliefs = state.get("beliefs", [])
        for i, belief in enumerate(state_beliefs):
            if not isinstance(belief, dict):
                return ValidationResult(
                    is_valid=False,
                    errors=(f"Belief {i} must be a dictionary",),
                    trace=tuple(trace)
                )
        
        trace.append("BELIEFS_VALID")
        
        # Validate revision graph (if present)
        revision_graph = state.get("revision_graph")
        if revision_graph is not None and not isinstance(revision_graph, dict):
            return ValidationResult(
                is_valid=False,
                errors=("RevisionGraph must be a dictionary",),
                trace=tuple(trace)
            )
        
        trace.append("REVISION_GRAPH_VALID")
        
        return ValidationResult(
            is_valid=True,
            trace=tuple(trace)
        )
    
    def validate_precision_landscape(self, landscape: dict[str, Any]) -> ValidationResult:
        """Validate a PrecisionLandscape."""
        trace = []
        
        if not isinstance(landscape, dict):
            return ValidationResult(
                is_valid=False,
                errors=("PrecisionLandscape must be a dictionary",),
                trace=tuple(trace)
            )
        
        # Validate estimates
        estimates = landscape.get("estimates", [])
        if not isinstance(estimates, (tuple, list)):
            return ValidationResult(
                is_valid=False,
                errors=("Estimates must be a tuple or list",),
                trace=tuple(trace)
            )
        
        for i, estimate in enumerate(estimates):
            if not isinstance(estimate, dict):
                return ValidationResult(
                    is_valid=False,
                    errors=(f"Estimate {i} must be a dictionary",),
                    trace=tuple(trace)
                )
            
            precision = estimate.get("precision")
            if precision is not None:
                if not isinstance(precision, (int, float)):
                    return ValidationResult(
                        is_valid=False,
                        errors=(f"Estimate {i} precision must be numeric",),
                        trace=tuple(trace)
                    )
                
                if not (0.0 <= precision <= 1.0):
                    return ValidationResult(
                        is_valid=False,
                        errors=(f"Estimate {i} precision must be between 0.0 and 1.0",),
                        trace=tuple(trace)
                    )
        
        trace.append("ESTIMATES_VALID")
        
        # Validate hierarchy
        hierarchy = landscape.get("hierarchy")
        if hierarchy is not None:
            if not isinstance(hierarchy, dict):
                return ValidationResult(
                    is_valid=False,
                    errors=("Hierarchy must be a dictionary",),
                    trace=tuple(trace)
                )
            
            for level, values in hierarchy.items():
                if not isinstance(values, (dict, tuple, list)):
                    return ValidationResult(
                        is_valid=False,
                        errors=(f"Hierarchy level '{level}' must be a dict or sequence",),
                        trace=tuple(trace)
                    )
        
        trace.append("HIERARCHY_VALID")
        
        return ValidationResult(
            is_valid=True,
            trace=tuple(trace)
        )
    
    def validate_revision_graph(self, graph: dict[str, Any]) -> ValidationResult:
        """Validate a BeliefRevisionGraph."""
        trace = []
        
        if not isinstance(graph, dict):
            return ValidationResult(
                is_valid=False,
                errors=("RevisionGraph must be a dictionary",),
                trace=tuple(trace)
            )
        
        # Validate nodes
        nodes = graph.get("nodes", [])
        if not isinstance(nodes, (tuple, list)):
            return ValidationResult(
                is_valid=False,
                errors=("Nodes must be a tuple or list",),
                trace=tuple(trace)
            )
        
        node_ids = set()
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                return ValidationResult(
                    is_valid=False,
                    errors=(f"Node {i} must be a dictionary",),
                    trace=tuple(trace)
                )
            
            node_id = node.get("node_id")
            if node_id is None:
                return ValidationResult(
                    is_valid=False,
                    errors=(f"Node {i} missing 'node_id'",),
                    trace=tuple(trace)
                )
            
            if not isinstance(node_id, str):
                return ValidationResult(
                    is_valid=False,
                    errors=(f"Node {i} node_id must be a string",),
                    trace=tuple(trace)
                )
            
            if node_id in node_ids:
                return ValidationResult(
                    is_valid=False,
                    errors=(f"Duplicate node_id '{node_id}'",),
                    trace=tuple(trace)
                )
            
            node_ids.add(node_id)
        
        trace.append("NODES_VALID")
        
        # Validate edges (if present)
        edges = graph.get("edges", [])
        if not isinstance(edges, (tuple, list)):
            return ValidationResult(
                is_valid=False,
                errors=("Edges must be a tuple or list",),
                trace=tuple(trace)
            )
        
        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                return ValidationResult(
                    is_valid=False,
                    errors=(f"Edge {i} must be a dictionary",),
                    trace=tuple(trace)
                )
            
            source = edge.get("source")
            target = edge.get("target")
            
            if source is None or target is None:
                return ValidationResult(
                    is_valid=False,
                    errors=(f"Edge {i} missing 'source' or 'target'",),
                    trace=tuple(trace)
                )
        
        trace.append("EDGES_VALID")
        
        # Check for cycles (simplified - full cycle detection would require graph traversal)
        if self._has_cycle(nodes, edges):
            return ValidationResult(
                is_valid=False,
                errors=("RevisionGraph contains a cycle",),
                trace=tuple(trace)
            )
        
        trace.append("ACYCLIC_VALIDATED")
        
        return ValidationResult(
            is_valid=True,
            trace=tuple(trace)
        )
    
    def _has_cycle(self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> bool:
        """Simple cycle detection (simplified implementation)."""
        if not nodes or not edges:
            return False
        
        # Build adjacency and check for obvious self-loops
        adj: dict[str, set[str]] = {}
        for node in nodes:
            node_id = node.get("node_id", "")
            adj[node_id] = set()
        
        for edge in edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            if source in adj:
                adj[source].add(target)
            if target in adj:
                adj[target].add(source)  # Undirected check
        
        # Check for self-loops
        for node_id, targets in adj.items():
            if node_id in targets:
                return True
        
        return False