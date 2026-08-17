# Structural Causal Model - Phase 7.5
# ===================================

"""
Canonical Structural Causal Model.

SCMs describe mechanism equations explicitly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any, Callable
from enum import Enum, auto


@dataclass(frozen=True)
class Variable:
    """
    A variable in the structural causal model.
    
    Variables can be observed or latent (unobserved).
    """
    
    # Identity
    variable_id: str                    # Unique variable identifier
    
    # Name
    name: str                           # Human-readable name
    
    # Type
    is_latent: bool = False             # Is this a latent (unobserved) variable?
    
    # Domain
    domain: Tuple[str, ...] = ()        # Possible values (if discrete)
    
    # Description
    description: str = ""               # What does this variable represent?
    
    @classmethod
    def make_observed(cls, name: str) -> Variable:
        """Create an observed (measured) variable."""
        return cls(variable_id=f"var:{uuid.uuid4().hex[:8]}", name=name, is_latent=False)
    
    @classmethod
    def make_latent(cls, name: str) -> Variable:
        """Create a latent (unobserved) variable."""
        return cls(variable_id=f"var:{uuid.uuid4().hex[:8]}", name=name, is_latent=True)


@dataclass(frozen=True)
class StructuralEquation:
    """
    A structural equation in the SCM.
    
    Describes how a variable is determined by its parents.
    """
    
    # Identity
    equation_id: str                    # Unique equation identifier
    
    # Effect variable (left-hand side)
    effect_variable: Variable           # The variable being defined
    
    # Parent variables (right-hand side)
    parent_variables: Tuple[Variable, ...]  # Input variables
    
    # Equation specification
    equation_specification: str         # e.g., "y = f(x1, x2)" or actual function
    
    # Assumptions about the equation
    assumptions: Tuple[str, ...] = ()   # Explicit assumptions
    
    @property
    def is_deterministic(self) -> bool:
        """Check if equation is deterministic (no noise term)."""
        return "noise" not in self.equation_specification.lower()


@dataclass(frozen=True)
class StructuralCausalModel:
    """
    A structural causal model with variables and equations.
    
    SCMs remain explicit and inspectable. They never modify the World Model.
    """
    
    # Identity
    scm_id: str                         # Unique SCM identifier
    semantic_identity: str              # Semantic identity (stable across runs)
    
    # Variables
    variables: Tuple[Variable, ...]     # All variables in the model
    
    # Structural equations
    structural_equations: Tuple[StructuralEquation, ...]  # All equations
    
    # Intervention support
    intervention_support: bool = True   # Can this SCM handle interventions?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def variable_count(self) -> int:
        """Number of variables in the model."""
        return len(self.variables)
    
    @property
    def equation_count(self) -> int:
        """Number of equations in the model."""
        return len(self.structural_equations)
    
    def get_variable_by_name(self, name: str) -> Optional[Variable]:
        """Get a variable by its name."""
        for v in self.variables:
            if v.name == name:
                return v
        return None
    
    def get_equations_for_variable(self, variable: Variable) -> Tuple[StructuralEquation, ...]:
        """Get equations that define a specific variable."""
        return tuple(
            eq for eq in self.structural_equations
            if eq.effect_variable.variable_id == variable.variable_id
        )
    
    def has_cycles(self) -> bool:
        """Check if the model contains causal cycles."""
        # Simple cycle detection: build adjacency and check for back-edges
        var_ids = {v.variable_id for v in self.variables}
        
        # Build parent map
        parent_map: Dict[str, Set[str]] = {}
        for eq in self.structural_equations:
            effect_id = eq.effect_variable.variable_id
            if effect_id not in parent_map:
                parent_map[effect_id] = set()
            for pv in eq.parent_variables:
                parent_map[effect_id].add(pv.variable_id)
        
        # DFS cycle detection
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def dfs(node: str) -> bool:
            if node in rec_stack:
                return True  # Cycle found
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for parent_id in parent_map.get(node, []):
                if parent_id in var_ids and dfs(parent_id):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for var_id in var_ids:
            if var_id not in visited:
                if dfs(var_id):
                    return True
        
        return False


@dataclass(frozen=True)
class SCMConstruction:
    """
    Result of an SCM construction process.
    
    Construction strategy and resulting model are preserved.
    """
    
    # Identity
    construction_id: str                # Unique construction identifier
    
    # Construction parameters
    construction_strategy: str          # e.g., "expert_specified", "data_driven"
    
    # Resulting model
    resulting_scm: StructuralCausalModel  # The constructed SCM
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()   # Construction diagnostics
    confidence_score: float = 1.0       # Overall confidence in construction
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None


def make_scm(
    name: str,
    variables: List[Variable],
    equations: List[StructuralEquation],
    intervention_support: bool = True,
) -> StructuralCausalModel:
    """Create a new SCM."""
    return StructuralCausalModel(
        scm_id=f"scm:{uuid.uuid4().hex[:16]}",
        semantic_identity=name,
        variables=tuple(variables),
        structural_equations=tuple(equations),
        intervention_support=intervention_support,
    )


def make_structural_equation(
    effect_var: Variable,
    parent_vars: Tuple[Variable, ...],
    equation_specification: str,
    assumptions: Tuple[str, ...] = (),
) -> StructuralEquation:
    """Create a new structural equation."""
    return StructuralEquation(
        equation_id=f"eq:{uuid.uuid4().hex[:8]}",
        effect_variable=effect_var,
        parent_variables=parent_vars,
        equation_specification=equation_specification,
        assumptions=assumptions,
    )


__all__ = [
    "Variable",
    "StructuralEquation",
    "StructuralCausalModel",
    "SCMConstruction",
]