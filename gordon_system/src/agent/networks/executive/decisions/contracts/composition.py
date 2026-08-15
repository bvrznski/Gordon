# Gordon Executive Decision Composition - Phase 4.4.10A
# =======================================================

"""
Decision Composition System.

This module defines the semantic composition elements for Executive Decisions:
assumptions, constraints, and dependencies.


COMPOSITION OVERVIEW
====================

An Executive Decision is semantically composed of:

    Context + Scope + Assumptions + Constraints + Dependencies

Each component is immutable and independently serializable.

ARCHITECTURAL LAWS
==================

E-018: Every Executive Decision shall identify its governed subject.
E-019: Every Executive Decision shall expose explicit purpose.
E-020: Every Executive Decision shall define assumptions and constraints
       independently.
"""

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# DECISION ASSUMPTIONS - Accepted propositions
# =============================================================================

@dataclass(frozen=True)
class DecisionAssumptions:
    """
    Record of propositions accepted during decision formation.
    
    Assumptions are immutable. Revisions replace assumptions rather than
    modifying them.
    
    Runtime-neutral: Yes
    Executable: No
    
    Examples:
        - Resources remain available
        - Policy remains unchanged  
        - Goal remains active
        - Workspace remains valid
        - External service remains reachable
        
    Example:
        >>> assumptions = DecisionAssumptions(
        ...     resource_available=True,
        ... )
    """
    
    assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """List of accepted propositions."""
    
    @property
    def is_assumptions(self) -> bool:
        """Return True for all assumption records."""
        return True
    
    def contains(self, assumption: str) -> bool:
        """
        Check if a specific assumption is present.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return assumption in self.assumptions


# =============================================================================
# DECISION CONSTRAINTS - Semantic boundaries
# =============================================================================

@dataclass(frozen=True)
class DecisionConstraints:
    """
    Record of semantic boundaries that shall not be violated.
    
    Constraints never prescribe implementation. They define what must NOT
    happen, not how to achieve the decision.
    
    Runtime-neutral: Yes
    Executable: No
    
    Examples:
        - Policy constraints
        - Security constraints
        - Ethical constraints
        - Architectural constraints
        - Capability constraints
        - Temporal constraints
        - Resource constraints
        
    Example:
        >>> constraints = DecisionConstraints(
        ...     policy_violations_prohibited=True,
        ... )
    """
    
    policy_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Policy-based constraints."""
    
    security_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Security-based constraints."""
    
    ethical_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Ethical constraints."""
    
    capability_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Capability-based constraints."""
    
    @property
    def is_constraints(self) -> bool:
        """Return True for all constraint records."""
        return True
    
    def has_policy_constraint(self, policy_id: str) -> bool:
        """Check if a specific policy constraint exists."""
        return policy_id in self.policy_constraints


# =============================================================================
# DECISION DEPENDENCIES - Required semantic objects
# =============================================================================

@dataclass(frozen=True)
class DecisionDependencies:
    """
    Record of other semantic objects required for validity.
    
    Dependencies form an acyclic semantic graph. They must exist and remain
    valid for the decision to remain valid.
    
    Runtime-neutral: Yes
    Executable: No
    
    Examples:
        - Goals
        - Strategies
        - Commitments
        - Policies
        - Resources
        
    Example:
        >>> dependencies = DecisionDependencies(
        ...     required_goals=("goal_abc123",),
        ... )
    """
    
    goals: Tuple[str, ...] = field(default_factory=tuple)
    """Required goal IDs."""
    
    strategies: Tuple[str, ...] = field(default_factory=tuple)
    """Required strategy IDs."""
    
    commitments: Tuple[str, ...] = field(default_factory=tuple)
    """Required commitment IDs."""
    
    policies: Tuple[str, ...] = field(default_factory=tuple)
    """Required policy IDs."""
    
    resources: Tuple[str, ...] = field(default_factory=tuple)
    """Required resource IDs."""
    
    @property
    def is_dependencies(self) -> bool:
        """Return True for all dependency records."""
        return True
    
    def requires_goal(self, goal_id: str) -> bool:
        """Check if a specific goal is required."""
        return goal_id in self.goals


# =============================================================================
# DECISION COMPOSITION - Complete semantic composition
# =============================================================================

@dataclass(frozen=True)
class DecisionComposition:
    """
    Complete semantic composition record for an Executive Decision.
    
    This bundles all composition elements together: assumptions, constraints,
    and dependencies. Each component is immutable and independently serializable.
    
    Runtime-neutral: Yes
    Executable: No
    
    Example:
        >>> composition = DecisionComposition(
        ...     assumptions=DecisionAssumptions(),
        ...     constraints=DecisionConstraints(),
        ...     dependencies=DecisionDependencies(),
        ... )
    """
    
    assumptions: DecisionAssumptions = field(default_factory=DecisionAssumptions)
    """Accepted propositions during decision formation."""
    
    constraints: DecisionConstraints = field(default_factory=DecisionConstraints)
    """Semantic boundaries that shall not be violated."""
    
    dependencies: DecisionDependencies = field(default_factory=DecisionDependencies)
    """Other semantic objects required for validity."""
    
    @property
    def is_composition(self) -> bool:
        """Return True for all composition records."""
        return True
    
    @classmethod
    def empty(cls) -> "DecisionComposition":
        """Create an empty composition with no assumptions, constraints, or dependencies."""
        return cls()