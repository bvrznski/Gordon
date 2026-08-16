# Oriented Network Governance Models - Phase 4.7.11
# ================================================

"""
Governance Models Package - Phase 4.7.11

This package contains the canonical governance model implementations for the
Oriented Network.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Deterministic operations
    - Repository-independent

MODEL CATEGORIES:

    constraints   - Architectural limitations
    permissions     - Semantic permissions
    prohibitions    - Semantic prohibitions
    obligations     - Mandatory requirements
    exceptions      - Explicit deviations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# CONSTRAINT MODEL
# =============================================================================

@dataclass(frozen=True)
class ArchitecturalConstraint:
    """Architectural constraint defining limitations."""
    
    constraint_id: str = "architectural-constraint"
    """Unique constraint identifier"""
    
    type: str = "architecture"
    """Constraint category"""
    
    restriction: Optional[str] = None
    """Description of architectural limitation"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of constraint application"""
    
    @property
    def is_valid(self) -> bool:
        return len(self.scope) >= 0
    
    def check_constraint(self, entity_id: str) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not entity_id:
            errors.append("entity_id is required")
        return len(errors) == 0, tuple(errors)


@dataclass(frozen=True)
class SemanticConstraint:
    """Semantic constraint defining semantic limitations."""
    
    constraint_id: str = "semantic-constraint"
    """Unique constraint identifier"""
    
    type: str = "semantics"
    """Constraint category"""
    
    restriction: Optional[str] = None
    """Description of semantic limitation"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of constraint application"""
    
    @property
    def is_valid(self) -> bool:
        return len(self.scope) >= 0


@dataclass(frozen=True)
class LifecycleConstraint:
    """Lifecycle constraint defining lifecycle limitations."""
    
    constraint_id: str = "lifecycle-constraint"
    """Unique constraint identifier"""
    
    type: str = "lifecycle"
    """Constraint category"""
    
    restriction: Optional[str] = None
    """Description of lifecycle limitation"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of constraint application"""
    
    @property
    def is_valid(self) -> bool:
        return len(self.scope) >= 0


@dataclass(frozen=True)
class EvaluationConstraint:
    """Evaluation constraint defining evaluation limitations."""
    
    constraint_id: str = "evaluation-constraint"
    """Unique constraint identifier"""
    
    type: str = "evaluation"
    """Constraint category"""
    
    restriction: Optional[str] = None
    """Description of evaluation limitation"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of constraint application"""
    
    @property
    def is_valid(self) -> bool:
        return len(self.scope) >= 0


@dataclass(frozen=True)
class IntegrationConstraint:
    """Integration constraint defining integration limitations."""
    
    constraint_id: str = "integration-constraint"
    """Unique constraint identifier"""
    
    type: str = "integration"
    """Constraint category"""
    
    restriction: Optional[str] = None
    """Description of integration limitation"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of constraint application"""
    
    @property
    def is_valid(self) -> bool:
        return len(self.scope) >= 0


@dataclass(frozen=True)
class GovernanceConstraint:
    """Governance constraint defining governance model limitations."""
    
    constraint_id: str = "governance-constraint"
    """Unique constraint identifier"""
    
    type: str = "governance"
    """Constraint category"""
    
    restriction: Optional[str] = None
    """Description of governance limitation"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of constraint application"""
    
    @property
    def is_valid(self) -> bool:
        return len(self.scope) >= 0


# =============================================================================
# PERMISSION MODEL
# =============================================================================

@dataclass(frozen=True)
class AllowedOperation:
    """Allowed operation within governance scope."""
    
    permission_id: str = "allowed-operation"
    """Unique permission identifier"""
    
    operation: str = "read"
    """Allowed operation type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of permission application"""
    
    @property
    def is_admissible(self) -> bool:
        return True
    
    def check_permission(self, entity_id: str, operation: str) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not entity_id:
            errors.append("entity_id is required")
        return len(errors) == 0, tuple(errors)


@dataclass(frozen=True)
class ConditionallyAllowedOperation(AllowedOperation):
    """Conditionally allowed operation."""
    
    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be satisfied"""
    
    @property
    def is_admissible(self) -> bool:
        return len(self.conditions) == 0
    
    @property
    def condition_count(self) -> int:
        return len(self.conditions)


@dataclass(frozen=True)
class ForbiddenOperation:
    """Forbidden operation - cannot be executed."""
    
    permission_id: str = "forbidden-operation"
    """Unique permission identifier"""
    
    operation: str = "execute"
    """Forbidden operation type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of prohibition application"""
    
    @property
    def is_admissible(self) -> bool:
        return False
    
    def check_permission(self, entity_id: str, operation: str) -> Tuple[bool, Tuple[str, ...]]:
        errors = ["operation is forbidden"]
        return False, tuple(errors)


@dataclass(frozen=True)
class RequiredOperation:
    """Required operation - must be performed."""
    
    permission_id: str = "required-operation"
    """Unique permission identifier"""
    
    operation: str = "validate"
    """Required operation type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of requirement application"""
    
    @property
    def is_mandatory(self) -> bool:
        return True


@dataclass(frozen=True)
class OptionalOperation:
    """Optional operation - may be performed."""
    
    permission_id: str = "optional-operation"
    """Unique permission identifier"""
    
    operation: str = "read"
    """Optional operation type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of option application"""
    
    @property
    def is_mandatory(self) -> bool:
        return False


# =============================================================================
# PROHIBITION MODEL
# =============================================================================

@dataclass(frozen=True)
class ForbiddenRelationship:
    """Forbidden relationship type."""
    
    prohibition_id: str = "forbidden-relationship"
    """Unique prohibition identifier"""
    
    relationship_type: str = "inheritance"
    """Forbidden relationship type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of prohibition application"""
    
    @property
    def is_forbidden(self) -> bool:
        return True


@dataclass(frozen=True)
class ForbiddenOwnership:
    """Forbidden ownership pattern."""
    
    prohibition_id: str = "forbidden-ownership"
    """Unique prohibition identifier"""
    
    ownership_type: str = "cross-subsystem"
    """Forbidden ownership type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of prohibition application"""
    
    @property
    def is_forbidden(self) -> bool:
        return True


@dataclass(frozen=True)
class ForbiddenDependency:
    """Forbidden dependency pattern."""
    
    prohibition_id: str = "forbidden-dependency"
    """Unique prohibition identifier"""
    
    dependency_type: str = "runtime"
    """Forbidden dependency type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of prohibition application"""
    
    @property
    def is_forbidden(self) -> bool:
        return True


@dataclass(frozen=True)
class ForbiddenTransition:
    """Forbidden state transition."""
    
    prohibition_id: str = "forbidden-transition"
    """Unique prohibition identifier"""
    
    from_state: Optional[str] = None
    """Source state"""
    
    to_state: Optional[str] = None
    """Target state"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of prohibition application"""
    
    @property
    def is_forbidden(self) -> bool:
        return True


@dataclass(frozen=True)
class ForbiddenIntegration:
    """Forbidden integration pattern."""
    
    prohibition_id: str = "forbidden-integration"
    """Unique prohibition identifier"""
    
    integration_type: str = "runtime-binding"
    """Forbidden integration type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of prohibition application"""
    
    @property
    def is_forbidden(self) -> bool:
        return True


# =============================================================================
# OBLIGATION MODEL
# =============================================================================

@dataclass(frozen=True)
class RequiredRelationship:
    """Required relationship between entities."""
    
    obligation_id: str = "required-relationship"
    """Unique obligation identifier"""
    
    relationship_type: str = "inheritance"
    """Required relationship type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of requirement application"""
    
    @property
    def is_mandatory(self) -> bool:
        return True


@dataclass(frozen=True)
class RequiredOwnership:
    """Required ownership pattern."""
    
    obligation_id: str = "required-ownership"
    """Unique obligation identifier"""
    
    ownership_type: str = "subsystem-boundary"
    """Required ownership type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of requirement application"""
    
    @property
    def is_mandatory(self) -> bool:
        return True


@dataclass(frozen=True)
class RequiredValidation:
    """Required validation step."""
    
    obligation_id: str = "required-validation"
    """Unique obligation identifier"""
    
    validation_type: str = "structure"
    """Required validation type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of requirement application"""
    
    @property
    def is_mandatory(self) -> bool:
        return True


@dataclass(frozen=True)
class RequiredDocumentation:
    """Required documentation."""
    
    obligation_id: str = "required-documentation"
    """Unique obligation identifier"""
    
    documentation_type: str = "architecture"
    """Required documentation type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of requirement application"""
    
    @property
    def is_mandatory(self) -> bool:
        return True


@dataclass(frozen=True)
class RequiredSerialization:
    """Required serialization format."""
    
    obligation_id: str = "required-serialization"
    """Unique obligation identifier"""
    
    serialization_type: str = "json"
    """Required serialization type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of requirement application"""
    
    @property
    def is_mandatory(self) -> bool:
        return True


# =============================================================================
# EXCEPTION MODEL
# =============================================================================

@dataclass(frozen=True)
class PolicyException:
    """Exception to a policy rule."""
    
    exception_id: str = "policy-exception"
    """Unique exception identifier"""
    
    type: str = "policy"
    """Exception category"""
    
    justification: Optional[str] = None
    """Architectural justification for exception"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of exception application"""
    
    @property
    def is_explicit(self) -> bool:
        return True
    
    @property
    def scope_count(self) -> int:
        return len(self.scope)


@dataclass(frozen=True)
class TemporaryException(PolicyException):
    """Temporary exception with bounded scope."""
    
    expiry: Optional[int] = None
    """Optional revision count at which exception expires"""
    
    @property
    def is_expired(self) -> bool:
        if self.expiry is None:
            return False
        return False


@dataclass(frozen=True)
class ArchitecturalException(PolicyException):
    """Exception to architectural rules."""
    
    type: str = "architecture"
    """Exception category"""
    
    @property
    def is_explicit(self) -> bool:
        return True


@dataclass(frozen=True)
class CompatibilityException(PolicyException):
    """Exception for compatibility purposes."""
    
    type: str = "compatibility"
    """Exception category"""
    
    @property
    def is_explicit(self) -> bool:
        return True


@dataclass(frozen=True)
class LegacyException(PolicyException):
    """Exception for legacy system support."""
    
    type: str = "legacy"
    """Exception category"""
    
    @property
    def is_explicit(self) -> bool:
        return True


# =============================================================================
# GOVERNANCE CONTEXT
# =============================================================================

@dataclass(frozen=True)
class GovernanceContext:
    """Immutable governance context."""
    
    context_id: str = "governance-context"
    """Unique context identifier"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of governance application"""
    
    authority: Optional[str] = None
    """Source of governing authority"""
    
    @property
    def is_valid(self) -> bool:
        return len(self.scope) >= 0
    
    def validate_boundary(self, entity_id: str) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not entity_id:
            errors.append("entity_id is required")
        return len(errors) == 0, tuple(errors)


@dataclass(frozen=True)
class PolicyContext(GovernanceContext):
    """Policy governance context."""
    
    policy_id: Optional[str] = None
    """Active policy identifier"""
    
    @property
    def is_valid(self) -> bool:
        return len(self.scope) >= 0


@dataclass(frozen=True)
class ComplianceContext(GovernanceContext):
    """Compliance governance context."""
    
    compliance_status: str = "unknown"
    """Current compliance status"""
    
    @property
    def is_compliant(self) -> bool:
        return self.compliance_status == "compliant"


@dataclass(frozen=True)
class ValidationContext(GovernanceContext):
    """Validation governance context."""
    
    validation_status: str = "pending"
    """Current validation status"""
    
    @property
    def is_validated(self) -> bool:
        return self.validation_status == "valid"


@dataclass(frozen=True)
class LifecycleContext(GovernanceContext):
    """Lifecycle governance context."""
    
    lifecycle_state: str = "active"
    """Current lifecycle state"""
    
    @property
    def is_valid(self) -> bool:
        return True


@dataclass(frozen=True)
class IntegrationContext(GovernanceContext):
    """Integration governance context."""
    
    integration_status: str = "pending"
    """Current integration status"""
    
    @property
    def is_integrated(self) -> bool:
        return self.integration_status == "integrated"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constraints
    "ArchitecturalConstraint",
    "SemanticConstraint",
    "LifecycleConstraint",
    "EvaluationConstraint",
    "IntegrationConstraint",
    "GovernanceConstraint",
    
    # Permissions
    "AllowedOperation",
    "ConditionallyAllowedOperation",
    "ForbiddenOperation",
    "RequiredOperation",
    "OptionalOperation",
    
    # Prohibitions
    "ForbiddenRelationship",
    "ForbiddenOwnership",
    "ForbiddenDependency",
    "ForbiddenTransition",
    "ForbiddenIntegration",
    
    # Obligations
    "RequiredRelationship",
    "RequiredOwnership",
    "RequiredValidation",
    "RequiredDocumentation",
    "RequiredSerialization",
    
    # Exceptions
    "PolicyException",
    "TemporaryException",
    "ArchitecturalException",
    "CompatibilityException",
    "LegacyException",
    
    # Contexts
    "GovernanceContext",
    "PolicyContext",
    "ComplianceContext",
    "ValidationContext",
    "LifecycleContext",
    "IntegrationContext",
]