# Readiness Gates - Dependency-Aware Evaluation
# ==============================================

"""
Readiness gates for dependency-aware evaluation.

This module provides:
- Deterministic gate ordering for readiness evaluation
- Cycle detection in dependency graphs
- Required vs optional dependency handling
- Gate result propagation through graph

Gates are evaluated in a specific order to ensure deterministic results.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
import time


# =============================================================================
# GATE TYPES
# =============================================================================

class GateResult(Enum):
    """Result of evaluating one readiness gate."""
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"      # Blocked by dependency failure
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class GateEvaluation:
    """Result of a single gate evaluation."""
    gate_id: str
    result: GateResult
    reason: Optional[str] = None
    dependencies_failed: Tuple[str, ...] = field(default_factory=tuple)
    evaluated_at_utc: float = field(default_factory=time.time)


# =============================================================================
# READINESS GATE DEFINITION
# =============================================================================

@dataclass(frozen=True)
class ReadinessGate:
    """
    A readiness gate that must pass for readiness.
    
    Gates are evaluated in order. Failure at any gate blocks readiness.
    """
    gate_id: str
    description: str
    mandatory: bool  # If False, failure = degraded, not blocked
    
    # Dependency configuration
    depends_on_gates: Tuple[str, ...] = field(default_factory=tuple)
    
    # Evaluation properties
    evaluation_cost: "GateCost" = field(default="LIGHT")
    timeout_seconds: float = 30.0
    
    def is_mandatory(self) -> bool:
        return self.mandatory


class GateCost(Enum):
    """Execution cost classification for gates."""
    LIGHT = "light"          # < 1ms
    MODERATE = "moderate"    # 1-10ms
    EXPENSIVE = "expensive"  # > 10ms


# =============================================================================
# READINESS GRAPH WITH GATES
# =============================================================================

@dataclass(frozen=True)
class ReadinessGateNode:
    """A node in the readiness gate graph."""
    gate_id: str
    depends_on: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ReadinessGraphConfig:
    """Configuration for a readiness dependency graph."""
    nodes: List[ReadinessGateNode]
    
    def validate(self) -> None:
        """Validate the graph configuration."""
        node_ids = {n.gate_id for n in self.nodes}
        
        # Check all dependencies reference existing nodes
        for node in self.nodes:
            for dep in node.depends_on:
                if dep not in node_ids:
                    raise ValueError(
                        f"Node '{node.gate_id}' depends on unknown node '{dep}'"
                    )
        
        # Detect cycles using DFS
        self._detect_cycles(node_ids)
    
    def _detect_cycles(self, node_ids: Set[str]) -> None:
        """Detect cycles in the dependency graph."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def has_cycle(node_id: str) -> bool:
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False
            
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for node in self.nodes:
                if node.gate_id == node_id:
                    for dep in node.depends_on:
                        if has_cycle(dep):
                            return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in node_ids:
            if has_cycle(node_id):
                raise ValueError("Readiness graph contains a cycle")


# =============================================================================
# GATE EVALUATOR
# =============================================================================

class GateEvaluator:
    """
    Evaluates readiness gates in dependency order.
    
    This is NOT the authority - it only evaluates and reports results.
    The ReadinessController owns the final decision.
    """
    
    def __init__(self, graph_config: ReadinessGraphConfig):
        self._config = graph_config
        self._evaluated_gates: Dict[str, GateEvaluation] = {}
        
        # Topologically sort gates for deterministic evaluation order
        self._evaluation_order = self._topological_sort()
    
    def _topological_sort(self) -> List[str]:
        """Get topologically sorted list of gate IDs."""
        node_ids = {n.gate_id for n in self._config.nodes}
        dependencies: Dict[str, Set[str]] = {
            n.gate_id: set(n.depends_on) for n in self._config.nodes
        }
        
        # Kahn's algorithm for topological sort
        result = []
        no_deps = [nid for nid in node_ids if not dependencies[nid]]
        
        while no_deps:
            node = no_deps.pop(0)
            result.append(node)
            
            # Find nodes that depend on this one
            for nid in node_ids:
                if node in dependencies[nid]:
                    dependencies[nid].discard(node)
                    if not dependencies[nid] and nid not in result:
                        no_deps.append(nid)
        
        return result
    
    def evaluate_gate(
        self,
        gate_id: str,
        check_fn: Optional[callable] = None
    ) -> GateEvaluation:
        """
        Evaluate a single gate.
        
        Args:
            gate_id: Which gate to evaluate
            check_fn: Function that returns (passed: bool, reason: Optional[str])
            
        Returns:
            GateEvaluation with result and details
        """
        if gate_id in self._evaluated_gates:
            return self._evaluated_gates[gate_id]
        
        # Check dependencies first
        node = None
        for n in self._config.nodes:
            if n.gate_id == gate_id:
                node = n
                break
        
        failed_deps = []
        if node:
            for dep_id in node.depends_on:
                dep_result = self.evaluate_gate(dep_id)
                if dep_result.result != GateResult.PASSED:
                    failed_deps.append(dep_id)
        
        # Evaluate the gate itself
        result = GateResult.PASSED
        reason: Optional[str] = None
        
        if check_fn:
            try:
                passed, reason = check_fn()
                if not passed:
                    result = GateResult.FAILED
            except Exception as e:
                result = GateResult.UNKNOWN
                reason = f"Evaluation error: {e}"
        
        # Check for dependency failure
        if failed_deps:
            result = GateResult.BLOCKED
            reason = f"Blocked by dependencies: {', '.join(failed_deps)}"
        
        evaluation = GateEvaluation(
            gate_id=gate_id,
            result=result,
            reason=reason,
            dependencies_failed=tuple(failed_deps)
        )
        
        self._evaluated_gates[gate_id] = evaluation
        return evaluation
    
    def evaluate_all(self) -> List[GateEvaluation]:
        """Evaluate all gates in dependency order."""
        results = []
        for gate_id in self._evaluation_order:
            result = self.evaluate_gate(gate_id)
            results.append(result)
        return results