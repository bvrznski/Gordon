# Gordon Executive Decision References - Phase 4.4.10A
# =====================================================

"""
Decision Reference Types and System.

This module defines the reference system for Executive Decisions, providing
types of semantic references between decisions.


REFERENCES OVERVIEW
===================

Semantic references are used instead of direct ownership to maintain loose coupling:

    Decision
         |
         v
    Goal    Strategy   Policy   Workspace   Commitment

ARCHITECTURAL LAWS
==================

E-034: Every dependency shall be explicit.
E-035: Every assumption shall be explicit.
"""

from dataclasses import dataclass, field
from typing import Tuple
from enum import Enum


# =============================================================================
# REFERENCE KINDS - Types of decision references
# =============================================================================

class ReferenceKind(Enum):
    """
    Kinds of semantic references between decisions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    DEPENDENCY = "dependency"
    """This decision depends on the referenced one."""
    
    PARENT = "parent"
    """This decision is a child of the referenced one."""
    
    CHILD = "child"
    """This decision has the referenced one as a child."""
    
    SUPPORTS = "supports"
    """This decision supports the referenced one."""
    
    REPLACES = "replaces"
    """This decision replaces the referenced one."""
    
    ALTERNATIVE_TO = "alternative_to"
    """This is an alternative to the referenced one."""
    
    DERIVED_FROM = "derived_from"
    """This decision was derived from the referenced one."""


# =============================================================================
# DECISION REFERENCE - Reference to another decision or artifact
# =============================================================================

@dataclass(frozen=True)
class DecisionReference:
    """
    Immutable reference to another Executive Decision or artifact.
    
    References are used instead of direct ownership to maintain loose coupling.
    
    Runtime-neutral: Yes
    Executable: No
    
    Example:
        >>> ref = DecisionReference(
        ...     referenced_id="decision_abc123",
        ...     reference_kind=ReferenceKind.DEPENDENCY,
        ... )
    """
    
    referenced_id: str = field(default="")
    """The identity being referenced."""
    
    reference_kind: ReferenceKind = ReferenceKind.ARTIFACT
    """Type of reference (dependency, parent, child, etc.)."""
    
    @property
    def is_reference(self) -> bool:
        """Return True for all references."""
        return True


# =============================================================================
# DECISION REFERENCES - Collection of references
# =============================================================================

@dataclass(frozen=True)
class DecisionReferences:
    """
    Collection of semantic references owned by an Executive Decision.
    
    Runtime-neutral: Yes
    Executable: No
    
    Example:
        >>> refs = DecisionReferences(
        ...     dependencies=("goal_abc123",),
        ... )
    """
    
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of decisions this depends on."""
    
    parents: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of parent decisions."""
    
    children: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of child decisions."""
    
    alternatives: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of alternative decisions."""
    
    @property
    def is_references(self) -> bool:
        """Return True for all reference collections."""
        return True
    
    def has_dependency(self, decision_id: str) -> bool:
        """
        Check if a specific decision is a dependency.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return decision_id in self.dependencies


# No additional imports needed here
