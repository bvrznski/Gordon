# Internal Episode Parent-Child Relationship Model
# ================================================

"""
Parent-child relationship model for episode derivation and coordination.

Child episodes must have independent identity, purpose, and bounded scope.
They are not subroutines but separate coordination units.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True, slots=True)
class InternalEpisodeRelationship:
    """
    Record of a relationship between parent and child episodes.
    
    Child episodes must have independent identity, purpose, and bounded scope.
    They are not subroutines but separate coordination units.
    
    RELATIONSHIP KINDS:
        • derived_from: Child derived from parent's result or insight
        • decomposes: Parent decomposed into child for bounded work
        • supports: Child supports parent's main purpose
        • validates: Child validates part of parent's work
        • challenges: Child challenges or tests parent's assumptions
        • continues: Child continues work that parent could not complete
        • refines: Child refines or specializes parent's result
        • supersedes: Child replaces or supersedes parent
        
    PROPERTIES:
        • relationship_id: Unique identifier for this relationship record
        • parent_episode_id: Parent episode ID
        • child_episode_id: Child episode ID
        • kind: Type of relationship (RelationshipKind.*)
        • result_integration_contract: How results should be integrated
        
    BOUNDEDNESS:
        • maximum_depth: Max parent-child depth (enforced by configuration)
        • maximum_descendants: Max descendants per root episode
        
    NOT RESPONSIBLE FOR:
        • Runtime coordination between episodes
        • Creating ExecutionThreads for child episodes
        • Scheduling execution order
    """
    
    # Identity
    relationship_id: str
    """Unique identifier for this relationship record."""
    
    parent_episode_id: str
    """ID of the parent episode."""
    
    child_episode_id: str
    """ID of the child episode."""
    
    kind: str  # RelationshipKind.*
    """Type of relationship between parent and child."""
    
    created_at_utc: str = ""
    """When this relationship was established."""
    
    result_integration_contract: Optional[str] = None
    """How child results should be integrated into parent (optional)."""
    
    @classmethod
    def create(
        cls,
        parent_episode_id: str,
        child_episode_id: str,
        kind: str,
    ) -> InternalEpisodeRelationship:
        """
        Create a new episode relationship record.
        
        Args:
            parent_episode_id: Parent episode ID
            child_episode_id: Child episode ID
            kind: Type of relationship (RelationshipKind.*)
            
        Returns:
            New InternalEpisodeRelationship instance
        """
        return cls(
            relationship_id=f"relationship_{parent_episode_id}_{child_episode_id}",
            parent_episode_id=parent_episode_id,
            child_episode_id=child_episode_id,
            kind=kind,
        )


@dataclass(frozen=True, slots=True)
class DerivationKind:
    """
    Categories of episode derivation.
    
    Defines what kind of relationship exists between parent and derived episodes.
    """
    
    # Derivation from parent's result
    INSIGHT = "insight"
    """Derived from a new insight produced by the parent."""
    
    PROPOSAL = "proposal"
    """Derived from a proposal made by the parent."""
    
    UNRESOLVED = "unresolved"
    """Derived to address issues left unresolved by the parent."""
    
    # Derivation for bounded decomposition
    DECOMPOSITION = "decomposition"
    """Parent decomposed its work into child episodes for bounded processing."""
    
    SUBTASK = "subtask"
    """Child handles a specific subtask of the parent's work."""
    
    # Verification and validation
    VALIDATION = "validation"
    """Derived to validate part of parent's result."""
    
    CHALLENGE = "challenge"
    """Derived to challenge or test parent's assumptions."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid derivation kinds."""
        return (
            cls.INSIGHT,
            cls.PROPOSAL,
            cls.UNRESOLVED,
            cls.DECOMPOSITION,
            cls.SUBTASK,
            cls.VALIDATION,
            cls.CHALLENGE,
        )