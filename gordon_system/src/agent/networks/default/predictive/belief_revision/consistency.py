# Canonical Belief Revision Consistency Validation - Phase 4.9.5
# ===============================================================
"""
Consistency validation implementation for BeliefRevision subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ConsistencyCheckResult:
    """
    Result of consistency validation.
    
    Fields:
        is_consistent:      Whether the state passes all consistency checks
        failures:           List of failed consistency rules
        warnings:           Non-fatal consistency issues
        trace:              Validation trace events
    
    Rules:
        - Consistency validation shall precede belief updates
        - Consistency validation shall not repair beliefs
        - Consistency findings remain typed
    """
    is_consistent: bool = False
    failures: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    warnings: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    trace: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ConsistencyRule:
    """
    Canonical consistency validation rule.
    
    Fields:
        name:           Rule identifier
        description:    Human-readable rule description
        check_func:     Function that returns (is_valid, failure_reasons)
    
    Rules:
        - Rules are immutable and deterministic
        - No side effects in checks
    """
    name: str
    description: str
    # check_func is callable but we keep it as reference to avoid runtime dep


class ConsistencyValidator:
    """
    Validator for belief state consistency.
    
    Rules:
        - Stateless validation
        - Side-effect free
        - Deterministic output
    """
    
    def __init__(self) -> None:
        self.trace_events: tuple[str, ...] = ()
        self._rules: tuple[ConsistencyRule, ...] = self._build_rules()
    
    def _build_rules(self) -> tuple[ConsistencyRule, ...]:
        """Build the set of consistency validation rules."""
        return (
            ConsistencyRule(
                name="hierarchy_consistent",
                description="Beliefs at each hierarchy level must be consistent"
            ),
            ConsistencyRule(
                name="no_cycles",
                description="Dependency graph must be acyclic"
            ),
            ConsistencyRule(
                name="schema_compatible",
                description="All beliefs must have compatible schemas"
            ),
            ConsistencyRule(
                name="confidence_bounded",
                description="Confidence values must be in [0.0, 1.0]"
            ),
            ConsistencyRule(
                name="uncertainty_non_negative",
                description="Uncertainty components must be non-negative"
            )
        )
    
    def validate_state(self, state: dict[str, Any]) -> ConsistencyCheckResult:
        """
        Validate an entire belief state for consistency.
        
        Args:
            state: BeliefState representation
            
        Returns:
            ConsistencyCheckResult
        """
        trace = []
        failures: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        
        # Check beliefs exist
        beliefs = state.get("beliefs", [])
        if not isinstance(beliefs, (tuple, list)):
            failures.append({
                "rule": "hierarchy_consistent",
                "reason": "Beliefs must be a tuple or list",
                "severity": "error"
            })
            return ConsistencyCheckResult(
                is_consistent=False,
                failures=tuple(failures),
                warnings=tuple(warnings),
                trace=tuple(trace)
            )
        
        # Validate each belief
        for i, belief in enumerate(beliefs):
            if not isinstance(belief, dict):
                failures.append({
                    "rule": "hierarchy_consistent",
                    "reason": f"Belief {i} must be a dictionary",
                    "severity": "error"
                })
                continue
            
            # Check confidence bounds
            confidence = belief.get("confidence", 0.5)
            if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
                failures.append({
                    "rule": "confidence_bounded",
                    "reason": f"Belief {i} confidence must be in [0.0, 1.0]",
                    "severity": "error"
                })
        
        # Check revision graph consistency (if present)
        revision_graph = state.get("revision_graph")
        if revision_graph is not None:
            if not isinstance(revision_graph, dict):
                failures.append({
                    "rule": "no_cycles",
                    "reason": "RevisionGraph must be a dictionary",
                    "severity": "error"
                })
        
        trace.append("STATE_TYPE_VALIDATED")
        trace.append("BELIEFS_ITERATED")
        
        return ConsistencyCheckResult(
            is_consistent=len(failures) == 0,
            failures=tuple(failures),
            warnings=tuple(warnings),
            trace=tuple(trace)
        )
    
    def validate_dependency_graph(self, graph: dict[str, Any]) -> ConsistencyCheckResult:
        """
        Validate a dependency graph for consistency.
        
        Args:
            graph: DependencyGraph representation
            
        Returns:
            ConsistencyCheckResult
        """
        trace = []
        failures: list[dict[str, Any]] = []
        
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        if not isinstance(nodes, (tuple, list)) or not isinstance(edges, (tuple, list)):
            failures.append({
                "rule": "schema_compatible",
                "reason": "Nodes and edges must be tuples/lists",
                "severity": "error"
            })
        
        # Check for self-loops
        for edge in edges:
            if isinstance(edge, dict):
                source = edge.get("source")
                target = edge.get("target")
                if source == target and source is not None:
                    failures.append({
                        "rule": "no_cycles",
                        "reason": f"Self-loop detected at node '{source}'",
                        "severity": "error"
                    })
        
        trace.append("GRAPH_NODES_VALIDATED")
        trace.append("GRAPH_EDGES_VALIDATED")
        
        return ConsistencyCheckResult(
            is_consistent=len(failures) == 0,
            failures=tuple(failures),
            warnings=tuple(),
            trace=tuple(trace)
        )
    
    def validate_revision_graph(self, graph: dict[str, Any]) -> ConsistencyCheckResult:
        """
        Validate a revision graph for consistency.
        
        Args:
            graph: BeliefRevisionGraph representation
            
        Returns:
            ConsistencyCheckResult
        """
        trace = []
        failures: list[dict[str, Any]] = []
        
        # Check required fields
        if "nodes" not in graph:
            failures.append({
                "rule": "schema_compatible",
                "reason": "RevisionGraph must have 'nodes'",
                "severity": "error"
            })
        elif not isinstance(graph["nodes"], (tuple, list)):
            failures.append({
                "rule": "schema_compatible",
                "reason": "RevisionGraph nodes must be a tuple/list",
                "severity": "error"
            })
        
        # Check node uniqueness
        if isinstance(graph.get("nodes"), (tuple, list)):
            node_ids = [n.get("node_id") for n in graph["nodes"] 
                       if isinstance(n, dict) and n.get("node_id")]
            if len(node_ids) != len(set(node_ids)):
                failures.append({
                    "rule": "no_cycles",
                    "reason": "Duplicate node IDs detected",
                    "severity": "error"
                })
        
        trace.append("REVISION_GRAPH_VALIDATED")
        
        return ConsistencyCheckResult(
            is_consistent=len(failures) == 0,
            failures=tuple(failures),
            warnings=tuple(),
            trace=tuple(trace)
        )