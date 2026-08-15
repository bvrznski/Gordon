# Gordon Executive Decision Metadata - Phase 4.4.10A
# ====================================================

"""
Decision Metadata System.

This module defines the metadata system for Executive Decisions, providing
immutable metadata about each decision.


METADATA OVERVIEW
=================

Every Executive Decision shall expose immutable metadata including:

    - identity
    - revision
    - creation time
    - creator
    - ownership
    - authority
    - horizon
    - stability
    - priority
    - urgency
    - state
    - scope
    - subject
    - purpose

ARCHITECTURAL LAWS
==================

E-039: Semantic artifacts shall never contain executable behavior.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum


# =============================================================================
# DECISION METADATA - Immutable metadata record
# =============================================================================

@dataclass(frozen=True)
class DecisionMetadata:
    """
    Record of immutable metadata for an Executive Decision.
    
    Metadata provides administrative and organizational information about
    the decision without affecting its semantic content.
    
    Runtime-neutral: Yes
    Executable: No
    
    Example:
        >>> metadata = DecisionMetadata(
        ...     revision_number=1,
        ...     created_at_utc=1234567890.0,
        ... )
    """
    
    identity_id: str = field(default="")
    """The decision identity this metadata describes."""
    
    revision_number: int = 1
    """Revision number within the identity's history."""
    
    created_at_utc: float = 0.0
    """Timestamp when this revision was created."""
    
    creator_id: Optional[str] = None
    """ID of the subsystem or agent that created this decision."""
    
    ownership_id: str = field(default="")
    """ID of the semantic owner."""
    
    authority_id: str = field(default="")
    """ID of the authority configuration."""
    
    horizon: str = "medium"
    """Expected temporal validity period."""
    
    stability: str = "provisional"
    """Expected volatility level."""
    
    priority: int = 0
    """Executive importance (higher = more important)."""
    
    urgency: int = 0
    """Temporal pressure (higher = more urgent)."""
    
    state: str = "draft"
    """Current semantic status."""
    
    scope: str = "local"
    """Scope dimension governed by the decision."""
    
    subject: str = ""
    """Primary semantic object governed by the decision."""
    
    purpose: str = ""
    """Purpose of the decision."""
    
    @property
    def is_metadata(self) -> bool:
        """Return True for all metadata records."""
        return True
    
    def is_current_revision(self, revision_number: int) -> bool:
        """
        Check if this metadata describes the current revision.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return self.revision_number == revision_number


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
    
    reference_kind: str = "artifact"
    """Type of reference (dependency, parent, child, etc.)."""
    
    @property
    def is_reference(self) -> bool:
        """Return True for all references."""
        return True


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


# No additional imports needed here
