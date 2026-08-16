# Oriented Network Policy Model - Phase 4.7.11
# ============================================

"""
Policy Framework for Oriented Network Governance

This module establishes the policy hierarchy that governs semantic admissibility
within the Oriented Network.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Deterministic operations
    - Repository-independent

POLICY HIERARCHY:

    Constitution
        ↓
    Policy
        ↓
    OrientationPolicy → SemanticPolicy → LifecyclePolicy
        ↓                                  ↓                  ↓
    IntegrationPolicy ←────────────── EvaluationPolicy ←── IntegrationPolicy
        ↓                                                           ↓
    CompliancePolicy ←─────────────────────────────────────────────┘

POLICY TYPES:

    OrientationPolicy   - Governs orientation admissibility
    SemanticPolicy      - Governs semantic validity
    LifecyclePolicy     - Governs lifecycle transitions
    IntegrationPolicy   - Governs integration rules
    EvaluationPolicy    - Governs evaluation criteria
    CompliancePolicy    - Governs compliance requirements
    GovernancePolicy    - Governs governance model structure

POLICY LAWS (ORIENTED-POLICY-LAW-XXX):

    ORIENTED-POLICY-LAW-001: Policies represent semantic governance
    ORIENTED-POLICY-LAW-002: Policies never execute enforcement
    ORIENTED-POLICY-LAW-003: Policies never modify Orientation
    ORIENTED-POLICY-LAW-004: Policies never override subsystem ownership
    ORIENTED-POLICY-LAW-005: Policies remain deterministic
    ORIENTED-POLICY-LAW-006: Policies remain immutable
    ORIENTED-POLICY-LAW-007: Policy inheritance shall remain explicit
    ORIENTED-POLICY-LAW-008: Conflicting policies shall be detectable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# POLICY CONSTANTS
# =============================================================================

POLICY_VERSION: int = 1
"""Policy model version"""


# =============================================================================
# Base Policy Model
# =============================================================================

@dataclass(frozen=True)
class OrientationPolicy:
    """
    Policy governing orientation admissibility.
    
    SEMANTIC ROLE:
        - Defines what orientations are semantically admissible
        - Establishes orientation hierarchy rules
        - Preserves orientation integrity
    
    INVARIANTS:
        OP-INV-001: Policy is immutable
        OP-INV-002: Policy never executes runtime logic
        OP-INV-003: Orientation remains deterministically verifiable
    """
    
    policy_id: str = "orientation-policy"
    """Unique policy identifier"""
    
    version: int = POLICY_VERSION
    """Policy version"""
    
    authority: Optional[str] = None
    """Source of authority (Constitution or higher policy)"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of policy application"""
    
    @property
    def is_valid(self) -> bool:
        """Check if policy is semantically valid."""
        return len(self.scope) >= 0
    
    @property
    def authority_chain(self) -> Tuple[str, ...]:
        """
        Get the full authority chain from Constitution to this policy.
        
        Returns:
            Tuple of authority references
        """
        chain = [self.policy_id]
        if self.authority:
            chain.append(self.authority)
        return tuple(chain)


@dataclass(frozen=True)
class SemanticPolicy:
    """
    Policy governing semantic validity.
    
    SEMANTIC ROLE:
        - Defines what constitutes semantically valid expressions
        - Establishes semantic relationships
        - Preserves semantic integrity
    
    INVARIANTS:
        SP-INV-001: Policy is immutable
        SP-INV-002: Policy never executes runtime logic
        SP-INV-003: Semantics remain deterministically verifiable
    """
    
    policy_id: str = "semantic-policy"
    """Unique policy identifier"""
    
    version: int = POLICY_VERSION
    """Policy version"""
    
    authority: Optional[str] = None
    """Source of authority (Constitution or higher policy)"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of policy application"""
    
    @property
    def is_valid(self) -> bool:
        """Check if policy is semantically valid."""
        return len(self.scope) >= 0
    
    @property
    def authority_chain(self) -> Tuple[str, ...]:
        """
        Get the full authority chain from Constitution to this policy.
        
        Returns:
            Tuple of authority references
        """
        chain = [self.policy_id]
        if self.authority:
            chain.append(self.authority)
        return tuple(chain)


@dataclass(frozen=True)
class LifecyclePolicy:
    """
    Policy governing lifecycle transitions.
    
    SEMANTIC ROLE:
        - Defines valid lifecycle state transitions
        - Establishes lifecycle constraints
        - Preserves lifecycle integrity
    
    INVARIANTS:
        LP-INV-001: Policy is immutable
        LP-INV-002: Policy never executes runtime logic
        LP-INV-003: Lifecycle remains deterministically verifiable
    """
    
    policy_id: str = "lifecycle-policy"
    """Unique policy identifier"""
    
    version: int = POLICY_VERSION
    """Policy version"""
    
    authority: Optional[str] = None
    """Source of authority (Constitution or higher policy)"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of policy application"""
    
    @property
    def is_valid(self) -> bool:
        """Check if policy is semantically valid."""
        return len(self.scope) >= 0
    
    @property
    def authority_chain(self) -> Tuple[str, ...]:
        """
        Get the full authority chain from Constitution to this policy.
        
        Returns:
            Tuple of authority references
        """
        chain = [self.policy_id]
        if self.authority:
            chain.append(self.authority)
        return tuple(chain)


@dataclass(frozen=True)
class IntegrationPolicy:
    """
    Policy governing integration rules.
    
    SEMANTIC ROLE:
        - Defines valid integration patterns
        - Establishes integration constraints
        - Preserves integration integrity
    
    INVARIANTS:
        IP-INV-001: Policy is immutable
        IP-INV-002: Policy never executes runtime logic
        IP-INV-003: Integration remains deterministically verifiable
    """
    
    policy_id: str = "integration-policy"
    """Unique policy identifier"""
    
    version: int = POLICY_VERSION
    """Policy version"""
    
    authority: Optional[str] = None
    """Source of authority (Constitution or higher policy)"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of policy application"""
    
    @property
    def is_valid(self) -> bool:
        """Check if policy is semantically valid."""
        return len(self.scope) >= 0
    
    @property
    def authority_chain(self) -> Tuple[str, ...]:
        """
        Get the full authority chain from Constitution to this policy.
        
        Returns:
            Tuple of authority references
        """
        chain = [self.policy_id]
        if self.authority:
            chain.append(self.authority)
        return tuple(chain)


@dataclass(frozen=True)
class EvaluationPolicy:
    """
    Policy governing evaluation criteria.
    
    SEMANTIC ROLE:
        - Defines evaluation criteria and standards
        - Establishes evaluation constraints
        - Preserves evaluation integrity
    
    INVARIANTS:
        EP-INV-001: Policy is immutable
        EP-INV-002: Policy never executes runtime logic
        EP-INV-003: Evaluation remains deterministically verifiable
    """
    
    policy_id: str = "evaluation-policy"
    """Unique policy identifier"""
    
    version: int = POLICY_VERSION
    """Policy version"""
    
    authority: Optional[str] = None
    """Source of authority (Constitution or higher policy)"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of policy application"""
    
    @property
    def is_valid(self) -> bool:
        """Check if policy is semantically valid."""
        return len(self.scope) >= 0
    
    @property
    def authority_chain(self) -> Tuple[str, ...]:
        """
        Get the full authority chain from Constitution to this policy.
        
        Returns:
            Tuple of authority references
        """
        chain = [self.policy_id]
        if self.authority:
            chain.append(self.authority)
        return tuple(chain)


@dataclass(frozen=True)
class CompliancePolicy:
    """
    Policy governing compliance requirements.
    
    SEMANTIC ROLE:
        - Defines what constitutes compliance
        - Establishes compliance constraints
        - Preserves compliance integrity
    
    INVARIANTS:
        CP-INV-001: Policy is immutable
        CP-INV-002: Policy never executes runtime logic
        CP-INV-003: Compliance remains deterministically verifiable
    """
    
    policy_id: str = "compliance-policy"
    """Unique policy identifier"""
    
    version: int = POLICY_VERSION
    """Policy version"""
    
    authority: Optional[str] = None
    """Source of authority (Constitution or higher policy)"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of policy application"""
    
    @property
    def is_valid(self) -> bool:
        """Check if policy is semantically valid."""
        return len(self.scope) >= 0
    
    @property
    def authority_chain(self) -> Tuple[str, ...]:
        """
        Get the full authority chain from Constitution to this policy.
        
        Returns:
            Tuple of authority references
        """
        chain = [self.policy_id]
        if self.authority:
            chain.append(self.authority)
        return tuple(chain)


@dataclass(frozen=True)
class GovernancePolicy:
    """
    Policy governing governance model structure.
    
    SEMANTIC ROLE:
        - Defines governance model architecture
        - Establishes governance constraints
        - Preserves governance integrity
    
    INVARIANTS:
        GP-INV-001: Policy is immutable
        GP-INV-002: Policy never executes runtime logic
        GP-INV-003: Governance remains deterministically verifiable
    """
    
    policy_id: str = "governance-policy"
    """Unique policy identifier"""
    
    version: int = POLICY_VERSION
    """Policy version"""
    
    authority: Optional[str] = None
    """Source of authority (Constitution or higher policy)"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of policy application"""
    
    @property
    def is_valid(self) -> bool:
        """Check if policy is semantically valid."""
        return len(self.scope) >= 0
    
    @property
    def authority_chain(self) -> Tuple[str, ...]:
        """
        Get the full authority chain from Constitution to this policy.
        
        Returns:
            Tuple of authority references
        """
        chain = [self.policy_id]
        if self.authority:
            chain.append(self.authority)
        return tuple(chain)


# =============================================================================
# POLICY HIERARCHY
# =============================================================================

@dataclass(frozen=True)
class PolicyHierarchy:
    """
    Represents the policy hierarchy.
    
    The hierarchy shows how policies derive from and relate to each other.
    
    HIERARCHY:
        Constitution
            ↓
        OrientationPolicy → SemanticPolicy → LifecyclePolicy
            ↓                                  ↓                  ↓
        IntegrationPolicy ←────────────── EvaluationPolicy ←── IntegrationPolicy
            ↓                                                           ↓
        CompliancePolicy ←─────────────────────────────────────────────┘
            ↓
        GovernancePolicy
        
    INVARIANTS:
        PH-INV-001: Hierarchy is acyclic
        PH-INV-002: Each policy has exactly one source of authority
        PH-INV-003: Hierarchy preserves semantic integrity
    """
    
    hierarchy_id: str = "policy-hierarchy"
    """Unique hierarchy identifier"""
    
    policies: Tuple[
        OrientationPolicy,
        SemanticPolicy,
        LifecyclePolicy,
        IntegrationPolicy,
        EvaluationPolicy,
        CompliancePolicy,
        GovernancePolicy,
    ] = field(
        default=(
            OrientationPolicy(),
            SemanticPolicy(),
            LifecyclePolicy(),
            IntegrationPolicy(),
            EvaluationPolicy(),
            CompliancePolicy(),
            GovernancePolicy(),
        )
    )
    
    @property
    def is_valid(self) -> bool:
        """Check if hierarchy is semantically valid."""
        return all(p.is_valid for p in self.policies)
    
    @property
    def highest_authority(self) -> str:
        """Get the highest authority in the policy hierarchy."""
        return "ORIENTED-POLICY-LAW-001"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "POLICY_VERSION",
    
    # Policy models
    "OrientationPolicy",
    "SemanticPolicy",
    "LifecyclePolicy",
    "IntegrationPolicy",
    "EvaluationPolicy",
    "CompliancePolicy",
    "GovernancePolicy",
    
    # Hierarchy
    "PolicyHierarchy",
]