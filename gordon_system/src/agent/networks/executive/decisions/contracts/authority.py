# Gordon Executive Decision Authority - Phase 4.4.10A
# ======================================================

"""
Decision Authority Model.

This module defines the semantic authority system governing who or what
is permitted to create, approve, revise, suspend, restore, and terminate
Executive Decisions.


AUTHORITY OVERVIEW
==================

Authority is hierarchical and context-dependent:

    Recommendation
           |
           v
    Executive Approval
           |
           v
    Executive Commitment
           |
           v
    Execution Request

Only the Executive Network may produce Executive Commitments.
Other systems may recommend.

ARCHITECTURAL LAWS
==================

E-004: Authority separation - creating, approving, committing are distinct.
E-009: Authority shall never imply ownership.
E-010: Ownership shall never imply authority.
E-036: Authority shall always be verifiable.
"""

from dataclasses import dataclass, field
from typing import Optional, FrozenSet, Tuple
from enum import Enum, auto


# =============================================================================
# AUTHORITY LEVELS - Hierarchical authority tiers
# =============================================================================

class AuthorityLevel(Enum):
    """
    Hierarchical levels of decision authority.
    
    Authority is hierarchical. Higher levels may override lower levels,
    but not vice versa.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Recommendation levels (non-binding)
    INITIAL_RECOMMENDATION = "initial_recommendation"
    """First-level recommendation from any subsystem."""
    
    SECOND_OPINION = "second_opinion"
    """Secondary review of a recommendation."""
    
    EXPERT_REVIEW = "expert_review"
    """Expert domain review of a recommendation."""
    
    # Approval levels (pre-commitment)
    APPROVAL_REQUESTED = "approval_requested"
    """Authority has been notified but not yet approved."""
    
    APPROVED = "approved"
    """Recommendation approved by proper authority."""
    
    # Commitment level (authoritative)
    COMMITMENT_AUTHORITY = "commitment_authority"
    """Full authority to commit decisions to Executive State."""
    
    EXECUTIVE_COMMITMENT = "executive_commitment"
    """
    Executive-level commitment authority.
    This is the highest semantic authority level for decisions.
    """


# =============================================================================
# AUTHORITY ROLES - Semantic roles with decision-making authority
# =============================================================================

class AuthorityRole(Enum):
    """
    Semantic roles that may possess authority over decisions.
    
    Roles are independent from runtime entities. They describe the
    semantic function, not the implementation.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # System roles
    INITIATOR = "initiator"
    """The subsystem or agent that initiated the decision."""
    
    REVIEWER = "reviewer"
    """Entity responsible for reviewing recommendations."""
    
    APPROVER = "approver"
    """Entity with authority to approve recommendations."""
    
    COMMITTER = "committer"
    """Entity with authority to commit decisions."""
    
    SUPERVISOR = "supervisor"
    """Higher-level authority that may override lower authorities."""
    
    AUDITOR = "auditor"
    """Entity responsible for audit and verification."""
    
    # Domain-specific roles
    POLICY_AUTHORITY = "policy_authority"
    """Authority over policy-related decisions."""
    
    SECURITY_AUTHORITY = "security_authority"
    """Authority over security-related decisions."""
    
    OPERATIONAL_AUTHORITY = "operational_authority"
    """Authority over operational decisions."""
    
    STRATEGIC_AUTHORITY = "strategic_authority"
    """Authority over strategic decisions."""


# =============================================================================
# DECISION AUTHORITY - Authority constraints for a decision
# =============================================================================

@dataclass(frozen=True)
class DecisionAuthority:
    """
    Semantic authority configuration for an Executive Decision.
    
    This defines who may perform which actions on the decision, and under
    what conditions. Authority is independent from ownership.
    
    Runtime-neutral: Yes
    Executable: No
    
    Key properties:
        - owner_id: Subsystem responsible for semantic correctness
        - creator_ids: Who may create this type of decision
        - approver_ids: Who may approve recommendations
        - committer_ids: Who may commit decisions to Executive State
        - revoker_ids: Who may revoke or terminate the decision
        
    Example:
        >>> authority = DecisionAuthority(
        ...     owner_id="executive_network",
        ...     creator_ids={"planning_system"},
        ...     approver_ids={"executive_network"},
        ...     committer_ids={"executive_network"},
        ... )
        >>> assert authority.can_commit(executing_as="executive_network")
    """
    
    owner_id: str = field(default="executive_network")
    """The subsystem responsible for semantic correctness of this decision."""
    
    creator_ids: FrozenSet[str] = field(default_factory=frozenset)
    """IDs of entities authorized to create decisions of this type."""
    
    approver_ids: FrozenSet[str] = field(default_factory=frozenset)
    """IDs of entities authorized to approve recommendations."""
    
    committer_ids: FrozenSet[str] = field(default_factory=frozenset)
    """IDs of entities authorized to commit decisions."""
    
    revoker_ids: FrozenSet[str] = field(default_factory=frozenset)
    """IDs of entities authorized to revoke or terminate decisions."""
    
    supervisor_id: Optional[str] = None
    """ID of a higher-level authority that may override."""
    
    level: AuthorityLevel = AuthorityLevel.COMMITMENT_AUTHORITY
    """The minimum authority level required for this decision."""
    
    @property
    def is_authority(self) -> bool:
        """Return True for all authority configurations."""
        return True
    
    def can_create(self, executing_as: str) -> bool:
        """
        Check if the executor may create this decision.
        
        Returns True if:
            - creator_ids is empty (anyone may create), OR
            - executing_as is in creator_ids
        
        Runtime-neutral: Yes
        Executable: No
        """
        return (
            len(self.creator_ids) == 0 or
            executing_as in self.creator_ids
        )
    
    def can_approve(self, executing_as: str) -> bool:
        """
        Check if the executor may approve a recommendation.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return (
            len(self.approver_ids) == 0 or
            executing_as in self.approver_ids
        )
    
    def can_commit(self, executing_as: str) -> bool:
        """
        Check if the executor may commit this decision.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return (
            len(self.committer_ids) == 0 or
            executing_as in self.committer_ids
        )
    
    def can_revoke(self, executing_as: str) -> bool:
        """
        Check if the executor may revoke this decision.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return (
            len(self.revoker_ids) == 0 or
            executing_as in self.revoker_ids or
            self.supervisor_id == executing_as
        )
    
    def can_override(self, executing_as: str) -> bool:
        """
        Check if the executor may override authority constraints.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return self.supervisor_id == executing_as
    
    def is_valid(self) -> bool:
        """
        Validate that the authority configuration is semantically sound.
        
        An authority is valid if it has at least one commit path defined
        (either committer_ids or supervisor_id).
        
        Runtime-neutral: Yes
        Executable: No
        """
        return (
            len(self.committer_ids) > 0 or
            self.supervisor_id is not None
        )


# =============================================================================
# AUTHORITY CHAIN - Authorization sequence for a decision
# =============================================================================

@dataclass(frozen=True)
class AuthorityChain:
    """
    Complete authorization chain for an Executive Decision.
    
    This records the complete sequence of authority decisions that led
    to a commitment. It is part of the provenance trail.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    decision_id: str = field(default="")
    """The identity of the decision being authorized."""
    
    chain: Tuple[str, ...] = field(default_factory=tuple)
    """Ordered sequence of authority actions."""
    
    @property
    def is_authority_chain(self) -> bool:
        """Return True for all authority chains."""
        return True
    
    @property
    def length(self) -> int:
        """Return the number of authority steps in the chain."""
        return len(self.chain)
    
    @classmethod
    def from_actions(cls, decision_id: str, actions: Tuple[str, ...]) -> "AuthorityChain":
        """
        Create an authority chain from a sequence of actions.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return cls(decision_id=decision_id, chain=actions)


# =============================================================================
# AUTHORITY VALIDATION - Validation utilities
# =============================================================================

class AuthorityValidation:
    """
    Static validation utilities for DecisionAuthority.
    
    Runtime-neutral: Yes
    Executable: No
    
    All methods are pure and deterministic.
    """
    
    @staticmethod
    def is_valid_authority_id(authority_id: str) -> bool:
        """Validate that an authority ID follows the expected format."""
        if not isinstance(authority_id, str):
            return False
        if len(authority_id) < 1:
            return False
        # Only alphanumeric and underscores allowed
        return all(c.isalnum() or c == "_" for c in authority_id)
    
    @staticmethod
    def is_valid_level(level: AuthorityLevel) -> bool:
        """Validate that an authority level is valid."""
        return isinstance(level, AuthorityLevel)
    
    @staticmethod
    def is_valid_role(role: AuthorityRole) -> bool:
        """Validate that an authority role is valid."""
        return isinstance(role, AuthorityRole)