# Gordon Executive Decision Ownership - Phase 4.4.10A
# =====================================================

"""
Decision Ownership Model.

This module defines the ownership system for Executive Decisions.
Ownership identifies the subsystem responsible for maintaining semantic
correctness, independent from runtime execution responsibility.


OWNERSHIP OVERVIEW
==================

    Ownership answers:
        Who maintains semantic correctness?

    Ownership does NOT answer:
        Who executes this?
        Who runs this at runtime?

These are independent questions. A subsystem may own a decision without
executing it.

Example:
    - Planning Network owns planning decisions
    - Executive Network owns executive commitments
    - Policy System owns policy definitions

ARCHITECTURAL LAWS
==================

E-009: Authority shall never imply ownership.
E-010: Ownership shall never imply authority.
"""

from dataclasses import dataclass, field
from typing import Tuple
from enum import Enum, auto


# =============================================================================
# OWNERSHIP KINDS - Types of ownership relationships
# =============================================================================

class OwnershipKind(Enum):
    """
    Kinds of ownership for Executive Decisions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Primary ownership (semantic correctness)
    SEMANTIC_OWNER = "semantic_owner"
    """Responsible for semantic correctness of the decision."""
    
    # Runtime ownership (execution context)
    EXECUTION_CONTEXT = "execution_context"
    """Provides runtime context but not semantic ownership."""
    
    # Domain ownership
    DOMAIN_OWNER = "domain_owner"
    """Domain expert responsible for domain-specific validity."""
    
    # Audit ownership
    AUDIT_OWNER = "audit_owner"
    """Responsible for audit trail and verification."""


# =============================================================================
# DECISION OWNERSHIP - Ownership configuration for a decision
# =============================================================================

@dataclass(frozen=True)
class DecisionOwnership:
    """
    Semantic ownership configuration for an Executive Decision.
    
    Ownership identifies the subsystem responsible for maintaining semantic
    correctness. Ownership is independent from runtime execution and
    authority.
    
    Runtime-neutral: Yes
    Executable: No
    
    Key properties:
        - owner_id: Subsystem responsible for semantic correctness
        - owner_kind: Type of ownership relationship
        - audit_trail_ids: Entities that may access the audit trail
        
    Example:
        >>> ownership = DecisionOwnership(
        ...     owner_id="executive_network",
        ...     owner_kind=OwnershipKind.SEMANTIC_OWNER,
        ... )
    """
    
    owner_id: str = field(default="executive_network")
    """The subsystem responsible for semantic correctness."""
    
    owner_kind: OwnershipKind = OwnershipKind.SEMANTIC_OWNER
    """Type of ownership relationship."""
    
    audit_trail_ids: frozenset = field(default_factory=frozenset)
    """IDs of entities that may access the audit trail."""
    
    @property
    def is_ownership(self) -> bool:
        """Return True for all ownership configurations."""
        return True
    
    def can_audit(self, executing_as: str) -> bool:
        """
        Check if the executor may access the audit trail.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return (
            len(self.audit_trail_ids) == 0 or
            executing_as in self.audit_trail_ids
        )
    
    def is_valid(self) -> bool:
        """
        Validate that the ownership configuration is semantically sound.
        
        An ownership configuration is valid if it has a non-empty owner_id.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return len(self.owner_id) > 0
    
    @classmethod
    def for_semantic_owner(cls, owner_id: str) -> "DecisionOwnership":
        """Create ownership configuration with semantic ownership."""
        return cls(
            owner_id=owner_id,
            owner_kind=OwnershipKind.SEMANTIC_OWNER,
        )


# =============================================================================
# OWNERSHIP TRACEABILITY - Track ownership across revisions
# =============================================================================

@dataclass(frozen=True)
class OwnershipTraceability:
    """
    Complete trace of ownership for a decision through its lifecycle.
    
    This records the complete sequence of ownership assignments and changes.
    It is part of the provenance trail.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    decision_id: str = field(default="")
    """The identity of the decision."""
    
    ownership_history: Tuple[str, ...] = field(default_factory=tuple)
    """Ordered sequence of owner IDs in chronological order."""
    
    @property
    def is_ownership_traceability(self) -> bool:
        """Return True for all ownership traceabilities."""
        return True
    
    @property
    def current_owner(self) -> str:
        """Return the most recent owner ID, or empty string if no history."""
        if self.ownership_history:
            return self.ownership_history[-1]
        return ""
    
    @classmethod
    def initial(cls, decision_id: str, initial_owner: str) -> "OwnershipTraceability":
        """
        Create an ownership traceability with initial owner.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return cls(
            decision_id=decision_id,
            ownership_history=(initial_owner,),
        )


# =============================================================================
# OWNERSHIP VALIDATION - Validation utilities
# =============================================================================

class OwnershipValidation:
    """
    Static validation utilities for DecisionOwnership.
    
    Runtime-neutral: Yes
    Executable: No
    
    All methods are pure and deterministic.
    """
    
    @staticmethod
    def is_valid_owner_id(owner_id: str) -> bool:
        """Validate that an owner ID follows the expected format."""
        if not isinstance(owner_id, str):
            return False
        if len(owner_id) < 1:
            return False
        # Only alphanumeric and underscores allowed
        return all(c.isalnum() or c == "_" for c in owner_id)
    
    @staticmethod
    def is_valid_kind(kind: OwnershipKind) -> bool:
        """Validate that an ownership kind is valid."""
        return isinstance(kind, OwnershipKind)