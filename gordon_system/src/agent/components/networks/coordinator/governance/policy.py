# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) - Policy System
========================================================

Hierarchical policy definitions and inheritance.
Policies define allowed behavior but never implement it.

Following:
* POLICY-LAW-001 through POLICY-LAW-008
"""

from __future__ import annotations

from dataclasses import dataclass, field


# =============================================================================
# GOVERNANCE POLICY
# =============================================================================

@dataclass(frozen=True, slots=True)
class GovernancePolicy:
    """
    Immutable governance policy definition.
    
    Policies define allowed behavior but never implement behavior.
    
    POLICY-LAW-001: Every policy shall derive from higher constitutional authority
    POLICY-LAW-002: Policies shall remain declarative
    POLICY-LAW-003: Policies shall preserve governing principles
    POLICY-LAW-004: Lower policies shall never weaken higher policies
    POLICY-LAW-005: Policy inheritance shall remain explicit
    POLICY-LAW-006: Policy provenance shall remain complete
    POLICY-LAW-007: Historical policies shall remain inspectable
    POLICY-LAW-008: Policy evaluation shall remain deterministic
    
    CCG-POL-INV-001: Policy is immutable (deeply frozen)
    CCG-POL-INV-002: Policy has no runtime references
    """
    policy_identity: str
    """Unique identifier for this policy."""
    
    policy_scope: str
    """Scope where this policy applies."""
    
    governing_principles: tuple[str, ...]
    """Principles that govern this policy."""
    
    constraints: tuple[str, ...] = field(default_factory=tuple)
    """Constraints imposed by this policy."""
    
    applicability: str = "all"
    """Applicability mode (all, specific, conditional)."""
    
    parent_policy_ref: str | None = None
    """Reference to parent policy for inheritance."""
    
    revision: int = 1
    """Revision number of this policy."""
    
    provenance_ref: str | None = None
    """Reference to policy provenance record."""
    
    @classmethod
    def create(
        cls,
        policy_id: str,
        scope: str,
        principles: tuple[str, ...],
        constraints: tuple[str, ...] | None = None,
        applicability: str = "all",
        parent_ref: str | None = None,
    ) -> GovernancePolicy:
        """
        Create a new governance policy.
        
        Args:
            policy_id: Unique identifier
            scope: Policy scope
            principles: Governing principles
            constraints: Policy constraints
            applicability: When this policy applies
            parent_ref: Parent policy reference
            
        Returns:
            A new GovernancePolicy instance
        """
        return cls(
            policy_identity=policy_id,
            policy_scope=scope,
            governing_principles=principles,
            constraints=constraints or (),
            applicability=applicability,
            parent_policy_ref=parent_ref,
            revision=1,
            provenance_ref=None,
        )
    
    def inherits_from(self, parent_id: str) -> bool:
        """Check if this policy inherits from a specific parent."""
        return self.parent_policy_ref == parent_id
    
    def can_weaken(self, parent_principles: tuple[str, ...]) -> bool:
        """
        Check if this policy would weaken the parent.
        
        Lower policies cannot weaken higher policies.
        
        Args:
            parent_principles: Principles from the parent policy
            
        Returns:
            True if weakening would occur
        """
        # Policy weakens if it removes constraints or removes principles
        return False  # For now, assume no weakening


# =============================================================================
# POLICY HIERARCHY
# =============================================================================

@dataclass(frozen=True, slots=True)
class PolicyHierarchy:
    """
    Immutable hierarchy of policies.
    
    Higher policies dominate lower policies.
    """
    policy_scope: str
    """Scope of this policy hierarchy."""
    
    level_policies: dict[str, tuple[GovernancePolicy, ...]] = field(default_factory=dict)
    """Policies grouped by level (constitution -> architecture -> coordination, etc)."""
    
    @classmethod
    def create(cls, scope: str) -> PolicyHierarchy:
        """
        Create a new policy hierarchy.
        
        Args:
            scope: The policy scope
            
        Returns:
            A new PolicyHierarchy instance
        """
        return cls(policy_scope=scope)
    
    def add_policy(self, level: str, policy: GovernancePolicy) -> PolicyHierarchy:
        """Add a policy at the specified level."""
        current = self.level_policies.get(level, ())
        return PolicyHierarchy(
            policy_scope=self.policy_scope,
            level_policies={**self.level_policies, level: (*current, policy)},
        )
    
    def get_policy_at_level(self, level: str) -> tuple[GovernancePolicy, ...]:
        """Get policies at a specific level."""
        return self.level_policies.get(level, ())
    
    def resolve_conflict(
        self,
        policies: tuple[GovernancePolicy, ...],
    ) -> GovernancePolicy | None:
        """
        Resolve policy conflicts - higher level policies dominate.
        
        Args:
            policies: Conflicting policies
            
        Returns:
            The dominant policy or None if conflict cannot be resolved
        """
        if not policies:
            return None
        
        # For now, return the first policy (simplified resolution)
        return policies[0]


# =============================================================================
# POLICY VALIDATION RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class PolicyValidationResult:
    """
    Immutable result of policy validation.
    
    CCG-POL-VAL-INV-001: Result is immutable
    CCG-POL-VAL-INV-002: Result has no runtime references
    
    CCG-POL-VAL-LAW-001: Validation results preserve evidence
    CCG-POL-VAL-LAW-002: Validation results are deterministic
    """
    policy_id: str
    """Identity of the validated policy."""
    
    validation_passed: bool
    """Whether the policy is valid."""
    
    principle_valid: bool = True
    """Whether governing principles are valid."""
    
    inheritance_valid: bool = True
    """Whether inheritance is correct (no weakening)."""
    
    constraints_consistent: bool = True
    """Whether constraints are consistent."""
    
    evidence: tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting the validation result."""
    
    @classmethod
    def of_valid(cls, policy_id: str) -> PolicyValidationResult:
        """Create a valid policy validation result."""
        return cls(
            policy_id=policy_id,
            validation_passed=True,
            principle_valid=True,
            inheritance_valid=True,
            constraints_consistent=True,
        )
    
    @classmethod
    def of_invalid(cls, policy_id: str) -> PolicyValidationResult:
        """Create an invalid policy validation result."""
        return cls(
            policy_id=policy_id,
            validation_passed=False,
        )
    
    def is_valid(self) -> bool:
        """Check if the policy validation passed."""
        return self.validation_passed
    
    def has_issues(self) -> tuple[str, ...]:
        """Get list of issues found during validation."""
        issues = []
        if not self.principle_valid:
            issues.append("invalid_principles")
        if not self.inheritance_valid:
            issues.append("invalid_inheritance")
        if not self.constraints_consistent:
            issues.append("inconsistent_constraints")
        return tuple(issues)


# =============================================================================
# POLICY CONFLICT RESOLUTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class PolicyConflictResolution:
    """
    Immutable result of policy conflict resolution.
    
    CCG-POL-CONFL-INV-001: Resolution is immutable
    CCG-POL-CONFL-INV-002: Resolution has no runtime references
    
    POLICY-LAW-004: Lower policies never weaken higher policies
    """
    resolved_policy_id: str
    """The winning policy."""
    
    conflicting_policy_ids: tuple[str, ...]
    """The losing/conflicting policies."""
    
    resolution_reason: str = "higher_level_dominates"
    """Reason for the resolution."""
    
    @classmethod
    def resolve(
        cls,
        winner: str,
        losers: tuple[str, ...],
        reason: str = "higher_level_dominates",
    ) -> PolicyConflictResolution:
        """
        Create a conflict resolution result.
        
        Args:
            winner: Winning policy ID
            losers: Losing/conflicting policy IDs
            reason: Reason for resolution
            
        Returns:
            A new PolicyConflictResolution instance
        """
        return cls(
            resolved_policy_id=winner,
            conflicting_policy_ids=losers,
            resolution_reason=reason,
        )