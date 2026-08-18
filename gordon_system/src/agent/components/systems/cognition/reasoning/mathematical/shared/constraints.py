# Constraint Management - Phase 7.46
# ====================================

"""
Canonical constraint management for mathematical reasoning.

Constraint analysis evaluates:
    - hard constraints
    - soft constraints  
    - feasibility
    - consistency
    - completeness
    - constraint dependency

Constraints remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ConstraintAnalysis:
    """
    Analysis of a constraint set.
    
    A constraint analysis includes feasibility determination,
    consistency checking, and dependency mapping.
    """
    
    analysis_id: str                  # Unique identifier
    constraint_set_id: str            # ID of analyzed constraints
    
    # Analysis results
    is_feasible: bool                 # Does any solution exist?
    is_consistent: bool               # Are constraints mutually satisfiable?
    completeness_score: float = 1.0   # Coverage of constraint space
    
    # Dependencies
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)  # constraint_id -> dependent_ids
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_infeasible(self) -> bool:
        """Check if problem is infeasible."""
        return not self.is_feasible
    
    @classmethod
    def create(
        cls,
        constraint_set_id: str,
        is_feasible: bool,
        is_consistent: bool,
        completeness_score: float = 1.0,
        dependency_graph: Optional[Dict[str, List[str]]] = None,
    ) -> ConstraintAnalysis:
        """Create a new constraint analysis."""
        return cls(
            analysis_id=f"constraint_analysis:{uuid.uuid4().hex[:16]}",
            constraint_set_id=constraint_set_id,
            is_feasible=is_feasible,
            is_consistent=is_consistent,
            completeness_score=completeness_score,
            dependency_graph=dependency_graph or {},
        )


@dataclass(frozen=True)
class ConstraintSet:
    """
    A complete set of constraints.
    
    Contains both hard and soft constraints with metadata.
    """
    
    constraint_set_id: str                  # Unique identifier
    name: str                               # Human-readable name
    
    hard_constraints: List[str] = field(default_factory=list)     # Must be satisfied
    soft_constraints: List[Tuple[str, float]] = field(default_factory=list)  # (expr, weight)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def hard_count(self) -> int:
        """Count hard constraints."""
        return len(self.hard_constraints)
    
    @property
    def soft_count(self) -> int:
        """Count soft constraints."""
        return len(self.soft_constraints)
    
    @classmethod
    def create(
        cls,
        name: str,
        hard_constraints: Optional[List[str]] = None,
        soft_constraints: Optional[List[Tuple[str, float]]] = None,
    ) -> ConstraintSet:
        """Create a new constraint set."""
        return cls(
            constraint_set_id=f"constraint_set:{uuid.uuid4().hex[:16]}",
            name=name,
            hard_constraints=hard_constraints or [],
            soft_constraints=soft_constraints or [],
        )


@dataclass(frozen=True)
class HardConstraint:
    """
    A hard (must-satisfy) constraint.
    
    Hard constraints are strict requirements that must be satisfied
    by any valid solution.
    """
    
    constraint_id: str                      # Unique identifier
    expression: str                         # Formal mathematical expression
    description: Optional[str] = None       # Human-readable description
    
    @classmethod
    def create(cls, expression: str, description: Optional[str] = None) -> HardConstraint:
        """Create a new hard constraint."""
        return cls(
            constraint_id=f"hard_constraint:{uuid.uuid4().hex[:16]}",
            expression=expression,
            description=description,
        )


@dataclass(frozen=True)
class SoftConstraint:
    """
    A soft (prefer-but-not-required) constraint.
    
    Soft constraints can be violated with a penalty proportional
    to the violation amount and weight.
    """
    
    constraint_id: str                      # Unique identifier
    expression: str                         # Formal mathematical expression
    slack: float = 0.0                      # Allowable violation amount
    weight: float = 1.0                     # Priority weight (higher = more important)
    description: Optional[str] = None       # Human-readable description
    
    @classmethod
    def create(
        cls,
        expression: str,
        slack: float = 0.0,
        weight: float = 1.0,
        description: Optional[str] = None,
    ) -> SoftConstraint:
        """Create a new soft constraint."""
        return cls(
            constraint_id=f"soft_constraint:{uuid.uuid4().hex[:16]}",
            expression=expression,
            slack=slack,
            weight=weight,
            description=description,
        )


@dataclass(frozen=True)
class ConstraintDependencyGraph:
    """
    Graph representation of constraint dependencies.
    
    Nodes are constraints, edges represent logical or numerical
    dependencies between them.
    """
    
    graph_id: str                           # Unique identifier
    
    # Structure
    nodes: Dict[str, str] = field(default_factory=dict)  # constraint_id -> expression
    edges: List[Tuple[str, str]] = field(default_factory=list)  # (from_id, to_id)
    
    # Properties
    is_directed: bool = True                # Dependencies are directional
    
    @classmethod
    def create(
        cls,
        constraints: Dict[str, str],
        dependencies: Optional[List[Tuple[str, str]]] = None,
    ) -> ConstraintDependencyGraph:
        """Create a new constraint dependency graph."""
        return cls(
            graph_id=f"constraint_graph:{uuid.uuid4().hex[:16]}",
            nodes=dict(constraints),
            edges=dependencies or [],
        )


__all__ = [
    "ConstraintAnalysis",
    "ConstraintSet",
    "HardConstraint",
    "SoftConstraint",
    "ConstraintDependencyGraph",
]