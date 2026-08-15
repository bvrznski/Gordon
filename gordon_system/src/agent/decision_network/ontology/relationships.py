# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Relationships Ontology

This module defines the canonical Action relationship taxonomy that describes
how Actions relate to each other semantically.

ACTION RELATIONSHIPS TAXONOMY
=============================

Relationships describe how Actions are connected in semantic space - which
Actions enable, depend on, conflict with, or replace others.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet, Tuple


# =============================================================================
# ACTION RELATIONSHIPS - Semantic connections between Actions
# =============================================================================

class ActionRelationship(Enum):
    """
    A semantic relationship between two Actions.
    
    Relationships describe how Actions are connected in semantic space.
    They enable reasoning about Action compatibility, dependencies,
    and composition without requiring runtime information.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # HIERARCHICAL RELATIONSHIPS - Taxonomic connections
    # =============================================================================
    
    IS_A = "is_a"
    """Generalization/specialization relationship."""
    
    SPECIALIZES = "specializes"
    """More specific than another Action."""
    
    GENERALIZES = "generalizes"
    """More general than another Action."""
    
    INHERITS_FROM = "inherits_from"
    """Inherits semantic properties from parent."""
    
    # =============================================================================
    # DEPENDENCY RELATIONSHIPS - Required conditions
    # =============================================================================
    
    DEPENDS_ON = "depends_on"
    """Requires another Action to be valid."""
    
    REQUIRES = "requires"
    """Needs another Action for preconditions."""
    
    ENABLED_BY = "enabled_by"
    """Only possible if another Action exists."""
    
    BLOCKED_BY = "blocked_by"
    """Cannot execute if another Action is active."""
    
    # =============================================================================
    # COMPOSITION RELATIONSHIPS - Structural connections
    # =============================================================================
    
    COMPOSES = "composes"
    """Part of a composite Action."""
    
    PART_OF = "part_of"
    """Constituent part of whole."""
    
    CONTAINS = "contains"
    """Contains other Actions as parts."""
    
    COMPOSED_OF = "composed_of"
    """Made up of constituent Actions."""
    
    # =============================================================================
    # EFFECT RELATIONSHIPS - Outcome connections
    # =============================================================================
    
    ENABLES = "enables"
    """Makes another Action possible."""
    
    DISABLES = "disables"
    """Prevents another Action from being valid."""
    
    INVALIDATES = "invalidates"
    """Makes another Action no longer applicable."""
    
    REPLACES = "replaces"
    """Substitutes for another Action."""
    
    SUPERSEDES = "supersedes"
    """Replaces with stronger authority."""
    
    # =============================================================================
    # REVERSAL RELATIONSHIPS - Correction connections
    # =============================================================================
    
    COMPENSATES_FOR = "compensates_for"
    """Compensates for effects of another Action."""
    
    ROLLS_BACK = "rolls_back"
    """Reverses effects of another Action."""
    
    UNDOES = "undoes"
    """Cancels out effects of another Action."""
    
    RESTORES = "restores"
    """Returns to state before another Action."""
    
    # =============================================================================
    # TEMPORAL RELATIONSHIPS - Order connections
    # =============================================================================
    
    PRECEDES = "precedes"
    """Must happen before another Action."""
    
    FOLLOWS = "follows"
    """Must happen after another Action."""
    
    CONCURRENT_WITH = "concurrent_with"
    """Can happen at the same time as another Action."""
    
    PARALLEL_TO = "parallel_to"
    """Executes in parallel with another Action."""
    
    # =============================================================================
    # COMPATIBILITY RELATIONSHIPS - Coexistence connections
    # =============================================================================
    
    COMPATIBLE_WITH = "compatible_with"
    """Can coexist without conflict."""
    
    CONFLICTS_WITH = "conflicts_with"
    """Mutually exclusive or incompatible."""
    
    EXCLUSIVE_WITH = "exclusive_with"
    """Cannot both be selected."""
    
    ALTERNATIVE_TO = "alternative_to"
    """Alternative option to another Action."""
    
    EQUIVALENT_TO = "equivalent_to"
    """Semantically equivalent to another Action."""
    
    # =============================================================================
    # CAUSAL RELATIONSHIPS - Cause/effect connections
    # =============================================================================
    
    CAUSES = "causes"
    """Directly causes effects of another."""
    
    EFFECT_OF = "effect_of"
    """Is an effect of another Action."""
    
    TRIGGERS = "triggers"
    """Triggers execution of another."""
    
    RESULT_OF = "result_of"
    """Is result of another Action."""
    
    # =============================================================================
    # SPECIAL RELATIONSHIPS
    # =============================================================================
    
    EQUIVALENT = "equivalent"
    """Semantically identical."""
    
    ORTHOGONAL_TO = "orthogonal_to"
    """No semantic relationship."""
    
    UNKNOWN = "unknown"
    """Relationship is unknown or undetermined."""


# =============================================================================
# UTILITY TYPES - Relationship collections
# =============================================================================

class ActionRelationships(FrozenSet[ActionRelationship]):
    """A collection of ActionRelationship values."""
    
    def __new__(cls, relationships: Tuple[ActionRelationship, ...] = ()):
        return super().__new__(cls, relationships)
    
    @classmethod
    def all(cls) -> "ActionRelationships":
        """Get all canonical ActionRelationships."""
        return cls(tuple(ActionRelationship))
    
    @classmethod
    def hierarchical(cls) -> "ActionRelationships":
        """Get all hierarchical relationships."""
        return cls((
            ActionRelationship.IS_A,
            ActionRelationship.SPECIALIZES,
            ActionRelationship.GENERALIZES,
            ActionRelationship.INHERITS_FROM,
        ))
    
    @classmethod
    def reversal(cls) -> "ActionRelationships":
        """Get all reversal/correction relationships."""
        return cls((
            ActionRelationship.COMPENSATES_FOR,
            ActionRelationship.ROLLS_BACK,
            ActionRelationship.UNDOES,
            ActionRelationship.RESTORES,
        ))


__all__ = [
    "ActionRelationship",
    "ActionRelationships",
]