# Knowledge Belief System - Shared Components - Phase 6.6
# ===========================================================

"""
Shared components for the belief subsystem.

This module contains utility classes, propagation logic, and shared contracts
used across the entire belief system.
"""

from __future__ import annotations

import uuid
import time


# =============================================================================
# BELIEF DESCRIPTOR - Metadata about beliefs
# =============================================================================


class BeliefDescriptor:
    """
    Descriptor providing metadata about a belief without exposing its content.
    
    Exposes only public-facing information like identity, kind, lifecycle state,
    and acceptance status while keeping detailed metrics separate.
    """
    
    def __init__(
        self,
        belief_identity: str,
        semantic_identity: str,
        belief_kind: str = "unknown",
        lifecycle_state: str = "created",
        acceptance_state: str = "unknown",
        publication_status: str = "unpublished",
    ):
        """Initialize a belief descriptor."""
        self._identity = belief_identity
        self._semantic_identity = semantic_identity
        self._kind = belief_kind
        self._lifecycle = lifecycle_state
        self._acceptance = acceptance_state
        self._publication = publication_status
    
    @property
    def identity(self) -> str:
        """Get the belief's unique identifier."""
        return self._identity
    
    @property
    def semantic_identity(self) -> str:
        """Get the assertion's identity being believed."""
        return self._semantic_identity
    
    @property
    def kind(self) -> str:
        """Get the belief's kind classification."""
        return self._kind
    
    @property
    def lifecycle_state(self) -> str:
        """Get the current lifecycle state."""
        return self._lifecycle
    
    @property
    def acceptance_state(self) -> str:
        """Get the current acceptance state."""
        return self._acceptance
    
    @property
    def publication_status(self) -> str:
        """Get the publication status."""
        return self._publication
    
    def to_dict(self) -> dict:
        """Convert descriptor to dictionary."""
        return {
            "belief_identity": self._identity,
            "semantic_identity": self._semantic_identity,
            "belief_kind": self._kind,
            "lifecycle_state": self._lifecycle,
            "acceptance_state": self._acceptance,
            "publication_status": self._publication,
            "timestamp_utc": time.time(),
        }
    
    def update_lifecycle(self, new_state: str) -> "BeliefDescriptor":
        """Create a new descriptor with updated lifecycle state."""
        return BeliefDescriptor(
            belief_identity=self._identity,
            semantic_identity=self._semantic_identity,
            belief_kind=self._kind,
            lifecycle_state=new_state,
            acceptance_state=self._acceptance,
            publication_status=self._publication,
        )
    
    def update_acceptance(self, new_state: str) -> "BeliefDescriptor":
        """Create a new descriptor with updated acceptance state."""
        return BeliefDescriptor(
            belief_identity=self._identity,
            semantic_identity=self._semantic_identity,
            belief_kind=self._kind,
            lifecycle_state=self._lifecycle,
            acceptance_state=new_state,
            publication_status=self._publication,
        )
    
    def publish(self) -> "BeliefDescriptor":
        """Mark the descriptor as published."""
        return BeliefDescriptor(
            belief_identity=self._identity,
            semantic_identity=self._semantic_identity,
            belief_kind=self._kind,
            lifecycle_state=self._lifecycle,
            acceptance_state=self._acceptance,
            publication_status="published",
        )


# =============================================================================
# PROPAGATION ENGINE - Base propagation logic
# =============================================================================


class PropagationEngine:
    """
    Base engine for propagating epistemic metrics through belief graphs.
    
    Handles confidence, uncertainty, and dependency propagation while preserving
    provenance throughout the system.
    """
    
    def __init__(self):
        """Initialize the propagation engine."""
        self._propagations: list = []
    
    @property
    def propagation_count(self) -> int:
        """Get the number of recorded propagations."""
        return len(self._propagations)
    
    def record_propagation(
        self,
        source_ids: list,
        target_ids: list,
        strategy: str,
        result: dict,
        provenance: dict = None,
    ) -> str:
        """
        Record a propagation event.
        
        Args:
            source_ids: IDs of source beliefs
            target_ids: IDs of target beliefs  
            strategy: Propagation strategy used
            result: Resulting metrics
            provenance: Additional context
        
        Returns:
            Propagation identity string
        """
        propagation_id = f"propagation:{uuid.uuid4().hex[:16]}"
        
        self._propagations.append({
            "identity": propagation_id,
            "source_ids": source_ids,
            "target_ids": target_ids,
            "strategy": strategy,
            "result": result,
            "provenance": provenance or {},
            "timestamp_utc": time.time(),
        })
        
        return propagation_id
    
    def get_propagation(self, identity: str) -> dict | None:
        """Get a specific propagation record."""
        for p in self._propagations:
            if p["identity"] == identity:
                return p
        return None
    
    def clear_propagations(self):
        """Clear all recorded propagations."""
        self._propagations.clear()


# =============================================================================
# DEPENDENCY GRAPH - In-memory dependency tracking
# =============================================================================


class DependencyGraph:
    """
    In-memory graph structure for tracking belief dependencies.
    
    Supports efficient traversal and propagation of changes through the
    epistemic dependency network.
    """
    
    def __init__(self):
        """Initialize an empty dependency graph."""
        self._edges: dict = {}  # {belief_id: [dependent_belief_ids]}
        self._reverse_edges: dict = {}  # {belief_id: [supporting_belief_ids]}
        self._kinds: dict = {}  # {edge_id: kind}
    
    @property
    def node_count(self) -> int:
        """Get the number of nodes in the graph."""
        all_nodes = set(self._edges.keys()) | set(self._reverse_edges.keys())
        return len(all_nodes)
    
    @property
    def edge_count(self) -> int:
        """Get the number of edges in the graph."""
        total = sum(len(v) for v in self._edges.values())
        return total
    
    def add_edge(self, dependent_id: str, supporting_id: str, kind: str = "evidence") -> None:
        """
        Add a dependency edge.
        
        Args:
            dependent_id: The belief that depends on another
            supporting_id: The belief being depended upon
            kind: Kind of dependency (default: "evidence")
        """
        # Forward edge: dependent -> dependents
        if dependent_id not in self._edges:
            self._edges[dependent_id] = []
        self._edges[dependent_id].append(supporting_id)
        
        # Reverse edge: supporting -> supporters  
        if supporting_id not in self._reverse_edges:
            self._reverse_edges[supporting_id] = []
        self._reverse_edges[supporting_id].append(dependent_id)
    
    def remove_edge(self, dependent_id: str, supporting_id: str) -> None:
        """Remove a dependency edge."""
        if dependent_id in self._edges:
            self._edges[dependent_id] = [
                s for s in self._edges[dependent_id] if s != supporting_id
            ]
        if supporting_id in self._reverse_edges:
            self._reverse_edges[supporting_id] = [
                d for d in self._reverse_edges[supporting_id] if d != dependent_id
            ]
    
    def get_dependents(self, belief_id: str) -> list:
        """Get beliefs that depend on the given belief."""
        return self._edges.get(belief_id, [])
    
    def get_supporters(self, belief_id: str) -> list:
        """Get beliefs that the given belief depends on."""
        return self._reverse_edges.get(belief_id, [])
    
    def get_all_beliefs(self) -> set:
        """Get all belief IDs in the graph."""
        return set(self._edges.keys()) | set(self._reverse_edges.keys())
    
    def to_dict(self) -> dict:
        """Convert graph to dictionary representation."""
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "edges": {k: list(v) for k, v in self._edges.items()},
            "reverse_edges": {k: list(v) for k, v in self._reverse_edges.items()},
        }
    
    def clear(self):
        """Clear all edges from the graph."""
        self._edges.clear()
        self._reverse_edges.clear()


# =============================================================================
# CONFLICT RESOLVER - Detect and track belief conflicts
# =============================================================================


class ConflictResolver:
    """
    Detects and tracks conflicts between beliefs.
    
    A conflict represents beliefs that disagree about related semantic content,
    without automatically resolving them (that requires higher-level policy).
    """
    
    def __init__(self):
        """Initialize the conflict resolver."""
        self._conflicts: list = []
    
    @property
    def conflict_count(self) -> int:
        """Get the number of active conflicts."""
        return len(self._conflicts)
    
    def detect_conflict(
        self,
        belief_ids: list,
        reason: str,
        scope: str = "semantic",
    ) -> str:
        """
        Register a detected conflict.
        
        Args:
            belief_ids: IDs of conflicting beliefs (minimum 2)
            reason: Explanation for the conflict
            scope: Scope of conflict (default: "semantic")
            
        Returns:
            Conflict identity string
        """
        if len(belief_ids) < 2:
            raise ValueError("Conflict requires at least 2 beliefs")
        
        conflict_id = f"conflict:{uuid.uuid4().hex[:16]}"
        
        self._conflicts.append({
            "identity": conflict_id,
            "belief_ids": belief_ids,
            "reason": reason,
            "scope": scope,
            "resolution_status": "pending",
            "created_at_utc": time.time(),
        })
        
        return conflict_id
    
    def resolve_conflict(self, conflict_id: str, resolution: str) -> bool:
        """
        Mark a conflict as resolved.
        
        Args:
            conflict_id: ID of the conflict to resolve
            resolution: Description of how it was resolved
            
        Returns:
            True if conflict was found and resolved
        """
        for conflict in self._conflicts:
            if conflict["identity"] == conflict_id:
                conflict["resolution_status"] = "resolved"
                conflict["resolution"] = resolution
                conflict["resolved_at_utc"] = time.time()
                return True
        return False
    
    def get_conflict(self, identity: str) -> dict | None:
        """Get a specific conflict."""
        for c in self._conflicts:
            if c["identity"] == identity:
                return c
        return None
    
    def get_active_conflicts(self) -> list:
        """Get all unresolved conflicts."""
        return [
            c for c in self._conflicts 
            if c.get("resolution_status") != "resolved"
        ]
    
    def clear_conflicts(self):
        """Clear all conflict records."""
        self._conflicts.clear()


# =============================================================================
# CONSISTENCY EVALUATOR - Evaluate belief consistency
# =============================================================================


class ConsistencyEvaluator:
    """
    Evaluates consistency among beliefs.
    
    Checks for logical, causal, temporal, and other consistency relations
    without modifying the beliefs themselves (observational only).
    """
    
    def __init__(self):
        """Initialize the consistency evaluator."""
        self._evaluations: list = []
    
    @property
    def evaluation_count(self) -> int:
        """Get the number of recorded evaluations."""
        return len(self._evaluations)
    
    def evaluate_consistency(
        self,
        belief_ids: list,
        findings: dict | None = None,
    ) -> tuple[bool, float]:
        """
        Evaluate consistency among a set of beliefs.
        
        Args:
            belief_ids: IDs of beliefs to evaluate
            findings: Additional findings dictionary (optional)
            
        Returns:
            Tuple of (is_consistent, consistency_score)
        """
        evaluation_id = f"consistency:{uuid.uuid4().hex[:16]}"
        
        # Default consistency score (assume consistent if no evidence against)
        score = 1.0
        violations = []
        
        if findings:
            for key, value in findings.items():
                if "violation" in key.lower() and value:
                    violations.append(value)
                    score *= 0.9
        
        is_consistent = len(violations) == 0
        
        self._evaluations.append({
            "identity": evaluation_id,
            "belief_ids": belief_ids,
            "violations": violations,
            "consistency_score": score,
            "findings": findings or {},
            "timestamp_utc": time.time(),
        })
        
        return is_consistent, score
    
    def get_evaluation(self, identity: str) -> dict | None:
        """Get a specific evaluation."""
        for e in self._evaluations:
            if e["identity"] == identity:
                return e
        return None
    
    def get_latest_evaluation(self, belief_id: str) -> dict | None:
        """Get the most recent evaluation for a specific belief."""
        matching = [
            e for e in self._evaluations 
            if belief_id in e.get("belief_ids", [])
        ]
        if not matching:
            return None
        return sorted(matching, key=lambda x: x["timestamp_utc"])[-1]
    
    def clear_evaluations(self):
        """Clear all recorded evaluations."""
        self._evaluations.clear()


__all__ = [
    "BeliefDescriptor",
    "PropagationEngine", 
    "DependencyGraph",
    "ConflictResolver",
    "ConsistencyEvaluator",
]