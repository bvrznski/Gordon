# Gordon Executive Decision Identity - Phase 4.4.10A
# =====================================================

"""
Decision Identity and Revision System.

This module defines the immutable identity architecture governing Executive
Decisions. An Executive Decision is not a transient runtime object; it is
a persistent semantic entity whose identity survives revisions, reevaluations,
and changing operational contexts.


IDENTITY ARCHITECTURE OVERVIEW
==============================

    DecisionIdentity (permanent)
           |
           +--- DecisionRevision 1 (immutable snapshot)
           +--- DecisionRevision 2 (immutable snapshot)
           +--- DecisionRevision 3 (immutable snapshot)

Identity survives. Instances do not.


ARCHITECTURAL PRINCIPLES
========================

Principle 1: Identity is Permanent
----------------------------------
Identity never changes. It survives revisions, context changes, evidence
updates, and even complete deletion of all revision instances.

Principle 2: Revisions are Snapshots
------------------------------------
Each revision is an immutable record of semantic understanding at a point
in time. Revisions never modify history; they extend it.

Principle 3: Continuity is Preserved
------------------------------------
A revision preserves conceptual continuity with its parent. It updates
understanding while maintaining the original decision's intent.


ARCHITECTURAL LAWS
==================

E-001: Every Executive Decision shall possess exactly one immutable Identity.
E-007: Identity survives revisions.
E-008: Revisions never overwrite history.
E-012: Every decision shall possess immutable lineage.
E-015: Every Executive Decision shall be completely reconstructable from
       serialized semantic artifacts.

SEMANTIC GUARANTEES
===================

Every Executive DecisionIdentity guarantees:

    1. Global uniqueness (UUID-based)
    2. Immutable creation timestamp
    3. Immutable creator reference
    4. Immutable semantic namespace
    5. Immutable lineage root
    6. Complete revision history traceability
"""

from dataclasses import dataclass, field
from typing import NewType, Optional
from uuid import uuid4


# =============================================================================
# DECISION IDENTITY - The permanent semantic identifier
# =============================================================================

@dataclass(frozen=True)
class DecisionIdentity:
    """
    Immutable semantic identity for an Executive Decision.
    
    This is the canonical identifier that persists across all revisions.
    It represents the "conceptual existence" of a decision.
    
    Runtime-neutral: Yes
    Executable: No
    
    Examples:
        >>> identity = DecisionIdentity.generate()
        >>> revision1 = DecisionRevision.create(parent_identity=identity)
        >>> revision2 = DecisionRevision.create(parent_identity=identity)
        >>> assert revision1.identity_id == revision2.identity_id
    """
    
    identity_id: str = field(default_factory=lambda: f"decision_{uuid4().hex[:32]}")
    """Globally unique identifier for this decision concept."""
    
    namespace: str = "executive"
    """Semantic namespace for the decision (e.g., 'executive', 'planning')."""
    
    created_at_utc: float = field(default_factory=lambda: 0.0)
    """Immutable creation timestamp (seconds since epoch UTC)."""
    
    creator_id: Optional[str] = None
    """Reference to the subsystem or agent that initiated this decision."""
    
    lineage_root: str = field(default="")
    """The root identity in a lineage tree, if applicable."""
    
    # Runtime-neutral property
    @property
    def is_identity(self) -> bool:
        """Return True for all identities."""
        return True
    
    # Serialization anchor
    @property
    def serialization_key(self) -> str:
        """
        Return the serialization key for this identity.
        
        This key is used as the anchor point for all serialized decision
        artifacts derived from this identity.
        """
        return f"decision:{self.identity_id}"
    
    @classmethod
    def generate(cls) -> "DecisionIdentity":
        """Generate a new DecisionIdentity with current timestamp."""
        import time
        return cls(
            identity_id=f"decision_{uuid4().hex[:32]}",
            created_at_utc=time.time(),
        )
    
    @classmethod
    def from_serialization_key(cls, key: str) -> "DecisionIdentity":
        """Reconstruct an identity from its serialization key."""
        parts = key.split(":")
        if len(parts) >= 2 and parts[0] == "decision":
            return cls(identity_id=parts[1])
        raise ValueError(f"Invalid serialization key: {key}")


# =============================================================================
# REVISION REFERENCE - Reference to a specific revision
# =============================================================================

@dataclass(frozen=True)
class RevisionReference:
    """
    Immutable reference to a DecisionRevision.
    
    This is used when we need to refer to a specific revision without
    owning it, maintaining loose coupling between components.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    identity_id: str
    """The decision identity this revision belongs to."""
    
    revision_number: int = 1
    """The sequential revision number within this identity's history."""
    
    @property
    def is_revision_reference(self) -> bool:
        """Return True for all revision references."""
        return True
    
    @classmethod
    def initial(cls, identity_id: str) -> "RevisionReference":
        """Create a reference to the first revision of an identity."""
        return cls(identity_id=identity_id, revision_number=1)


# =============================================================================
# REVISION METADATA - Metadata about a revision
# =============================================================================

@dataclass(frozen=True)
class RevisionMetadata:
    """
    Metadata about a DecisionRevision.
    
    This contains administrative information about the revision itself,
    not the semantic content of the decision.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    revision_number: int = 1
    """Sequential revision number within this identity's history."""
    
    parent_revision_id: Optional[str] = None
    """The revision that this one updates (if any)."""
    
    created_at_utc: float = field(default_factory=lambda: 0.0)
    """Timestamp when this revision was created."""
    
    author_id: Optional[str] = None
    """Reference to the agent or subsystem that authored this revision."""
    
    @property
    def is_revision_metadata(self) -> bool:
        """Return True for all revision metadata."""
        return True


# =============================================================================
# IDENTITY VALIDATION - Validation rules for identities
# =============================================================================

class IdentityValidation:
    """
    Static validation utilities for DecisionIdentity.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    @staticmethod
    def is_valid_identity_id(identity_id: str) -> bool:
        """Validate that an identity ID follows the expected format."""
        if not isinstance(identity_id, str):
            return False
        if len(identity_id) < 10:
            return False
        if not identity_id.startswith(("decision_", "id_")):
            return False
        return True
    
    @staticmethod
    def is_valid_namespace(namespace: str) -> bool:
        """Validate that a namespace follows the expected format."""
        if not isinstance(namespace, str):
            return False
        if len(namespace) < 1:
            return False
        # Only alphanumeric and underscores allowed
        return all(c.isalnum() or c == "_" for c in namespace)