# Mathematical Set - Phase 7.46
# =============================

"""
Canonical Mathematical Set representation.

A Mathematical Set defines:
    - formal variables
    - constraints
    - axioms
    - objective functions
    - proof obligations

Mathematical Sets remain immutable during reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from enum import Enum, auto


class VariableType(Enum):
    """Variable types in mathematical sets."""
    
    CONTINUOUS = "continuous"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    DISCRETE = "discrete"
    SYMBOLIC = "symbolic"


@dataclass(frozen=True)
class Variable:
    """
    Mathematical variable definition.
    
    Variables are immutable identifiers that represent quantities or symbols
    in mathematical problems.
    """
    
    variable_id: str              # Unique identifier
    name: str                     # Display name (e.g., "x", "y_1")
    variable_type: VariableType   # Type of variable
    domain: Optional[str] = None  # Domain specification (e.g., "R", "Z", "[0,1]")
    bounds: Optional[Tuple[Any, Any]] = None  # [min, max] for numeric variables
    initial_value: Optional[Any] = None       # Initial value if known
    
    @classmethod
    def create(
        cls,
        name: str,
        variable_type: VariableType = VariableType.CONTINUOUS,
        domain: Optional[str] = None,
        bounds: Optional[Tuple[Any, Any]] = None,
        initial_value: Optional[Any] = None,
    ) -> Variable:
        """Create a new variable."""
        return cls(
            variable_id=f"variable:{uuid.uuid4().hex[:16]}",
            name=name,
            variable_type=variable_type,
            domain=domain,
            bounds=bounds,
            initial_value=initial_value,
        )


class ConstraintType(Enum):
    """Constraint types."""
    
    EQUALITY = "equality"
    INEQUALITY = "inequality"
    INTEGER_CONSTRAINT = "integer_constraint"
    DISJUNCTIVE = "disjunctive"
    LOGICAL = "logical"
    PROBABILITY = "probability"


@dataclass(frozen=True)
class Constraint:
    """
    Mathematical constraint definition.
    
    Constraints define formal requirements that solutions must satisfy.
    """
    
    constraint_id: str                    # Unique identifier
    expression: str                       # Formal expression (e.g., "x + y <= 10")
    constraint_type: ConstraintType       # Type of constraint
    is_hard: bool = True                  # Hard constraints must be satisfied
    slack: float = 0.0                    # Allowable violation for soft constraints
    weight: float = 1.0                   # Priority weight for soft constraints
    
    @classmethod
    def create_equality(
        cls,
        expression: str,
        is_hard: bool = True,
        weight: float = 1.0,
    ) -> Constraint:
        """Create an equality constraint."""
        return cls(
            constraint_id=f"constraint:{uuid.uuid4().hex[:16]}",
            expression=expression,
            constraint_type=ConstraintType.EQUALITY,
            is_hard=is_hard,
            weight=weight,
        )
    
    @classmethod
    def create_inequality(
        cls,
        expression: str,
        is_hard: bool = True,
        slack: float = 0.0,
        weight: float = 1.0,
    ) -> Constraint:
        """Create an inequality constraint."""
        return cls(
            constraint_id=f"constraint:{uuid.uuid4().hex[:16]}",
            expression=expression,
            constraint_type=ConstraintType.INEQUALITY,
            is_hard=is_hard,
            slack=slack,
            weight=weight,
        )


@dataclass(frozen=True)
class ObjectiveFunction:
    """
    Optimization objective function definition.
    
    Objectives define what we want to maximize or minimize.
    """
    
    objective_id: str                     # Unique identifier
    expression: str                       # Formal expression (e.g., "x^2 + y^2")
    objective_type: str = "minimize"      # "minimize" or "maximize"
    weight: float = 1.0                   # Weight in multi-objective problems
    
    @classmethod
    def create(
        cls,
        expression: str,
        objective_type: str = "minimize",
        weight: float = 1.0,
    ) -> ObjectiveFunction:
        """Create a new objective function."""
        return cls(
            objective_id=f"objective:{uuid.uuid4().hex[:16]}",
            expression=expression,
            objective_type=objective_type,
            weight=weight,
        )


@dataclass(frozen=True)
class MathematicalSet:
    """
    Complete mathematical problem definition.
    
    A Mathematical Set contains all formal information about a mathematical
    reasoning problem, including variables, constraints, objectives, and
    proof obligations.
    """
    
    set_id: str                           # Unique identifier
    problem_name: str                     # Human-readable name
    
    # Components
    variables: List[Variable]             # All decision/symbolic variables
    constraints: List[Constraint]         # All formal constraints
    objective_functions: List[ObjectiveFunction]  # Objectives (for optimization)
    
    # Axioms and assumptions
    axioms: List[str] = field(default_factory=list)       # Accepted axioms
    assumptions: List[str] = field(default_factory=list)  # Working assumptions
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_id: Optional[str] = None   # If derived from another set
    
    @property
    def variable_count(self) -> int:
        """Count total variables."""
        return len(self.variables)
    
    @property
    def constraint_count(self) -> int:
        """Count total constraints."""
        return len(self.constraints)
    
    @property
    def hard_constraint_count(self) -> int:
        """Count only hard constraints."""
        return sum(1 for c in self.constraints if c.is_hard)
    
    @classmethod
    def create(
        cls,
        problem_name: str,
        variables: List[Variable],
        constraints: List[Constraint],
        objective_functions: Optional[List[ObjectiveFunction]] = None,
        axioms: Optional[List[str]] = None,
        assumptions: Optional[List[str]] = None,
    ) -> MathematicalSet:
        """Create a new mathematical set."""
        return cls(
            set_id=f"mathematical_set:{uuid.uuid4().hex[:16]}",
            problem_name=problem_name,
            variables=list(variables),
            constraints=list(constraints),
            objective_functions=objective_functions or [],
            axioms=axioms or [],
            assumptions=assumptions or [],
        )


__all__ = [
    "VariableType",
    "Variable",
    "ConstraintType",
    "Constraint",
    "ObjectiveFunction",
    "MathematicalSet",
]