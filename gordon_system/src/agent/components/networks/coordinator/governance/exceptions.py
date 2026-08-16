# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) Exceptions and Error Types
==================================================================

Canonical exception hierarchy for the Governance subsystem.
All exceptions are deeply immutable to ensure deterministic error handling.

This module implements governance-specific errors following:

* CONSTITUTION-LAW-008: Constitution publication shall remain immutable
* COMPLIANCE-LAW-003: Violations shall remain explicit
* VALIDATION-LAW-007: Validation shall remain side-effect free
"""

from __future__ import annotations

from dataclasses import dataclass


# =============================================================================
# BASE GOVERNANCE EXCEPTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class GovernanceError(Exception):
    """
    Base exception for all governance errors.
    
    GOVERNANCE-EXC-INV-001: Errors are immutable
    GOVERNANCE-EXC-INV-002: Errors have no runtime references
    
    CCG-EXC-LAW-001: All governance errors preserve structure
    """
    message: str
    """Human-readable error message."""
    
    finding_code: str = "unknown"
    """Canonical finding code for structured handling."""
    
    affected_references: tuple[str, ...] = ()
    """References to artifacts affected by this error."""
    
    @classmethod
    def of(cls, message: str, finding_code: str = "unknown") -> GovernanceError:
        """
        Create a governance error with a finding code.
        
        Args:
            message: Human-readable description of the error
            finding_code: Canonical code for structured handling
            
        Returns:
            A new GovernanceError instance
        """
        return cls(
            message=message,
            finding_code=finding_code,
            affected_references=(),
        )
    
    def with_reference(self, ref: str) -> GovernanceError:
        """Add an affected reference and return a new error."""
        return GovernanceError(
            message=self.message,
            finding_code=self.finding_code,
            affected_references=(*self.affected_references, ref),
        )


# =============================================================================
# CONSTITUTION ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConstitutionError(GovernanceError):
    """Exception raised for constitution-related errors."""
    
    @classmethod
    def unknown_principle(cls, principle_name: str) -> ConstitutionError:
        """
        Create an error for an unknown constitutional principle.
        
        Args:
            principle_name: The unrecognized principle name
            
        Returns:
            A new ConstitutionError instance
        """
        return cls(
            message=f"Unknown constitutional principle: {principle_name}",
            finding_code="unknown_principle",
            affected_references=(f"principle:{principle_name}",),
        )
    
    @classmethod
    def invalid_revision(cls, current_version: str) -> ConstitutionError:
        """
        Create an error for an invalid constitution revision.
        
        Args:
            current_version: The expected version
            
        Returns:
            A new ConstitutionError instance
        """
        return cls(
            message=f"Invalid constitution revision: {current_version}",
            finding_code="invalid_revision",
            affected_references=(f"constitution:{current_version}",),
        )


# =============================================================================
# AUTHORITY ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class AuthorityError(GovernanceError):
    """Exception raised for authority-related errors."""
    
    @classmethod
    def undefined_authority(cls, authority_scope: str) -> AuthorityError:
        """
        Create an error for an undefined authority.
        
        Args:
            authority_scope: The undefined authority scope
            
        Returns:
            A new AuthorityError instance
        """
        return cls(
            message=f"Undefined authority: {authority_scope}",
            finding_code="undefined_authority",
            affected_references=(f"authority:{authority_scope}",),
        )
    
    @classmethod
    def boundary_violation(cls, source: str, target: str) -> AuthorityError:
        """
        Create an error for crossing an authority boundary.
        
        Args:
            source: The source authority attempting the operation
            target: The target authority being accessed
            
        Returns:
            A new AuthorityError instance
        """
        return cls(
            message=f"Authority boundary violation: {source} -> {target}",
            finding_code="boundary_violation",
            affected_references=(f"authority:{source}", f"authority:{target}"),
        )
    
    @classmethod
    def invalid_jurisdiction(cls, authority_scope: str) -> AuthorityError:
        """
        Create an error for operating outside jurisdiction.
        
        Args:
            authority_scope: The authority scope
            
        Returns:
            A new AuthorityError instance
        """
        return cls(
            message=f"Operation outside jurisdiction: {authority_scope}",
            finding_code="invalid_jurisdiction",
            affected_references=(f"authority:{authority_scope}",),
        )


# =============================================================================
# DELEGATION ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class DelegationError(GovernanceError):
    """Exception raised for delegation-related errors."""
    
    @classmethod
    def invalid_delegation(cls, delegator: str, delegate: str) -> DelegationError:
        """
        Create an error for an invalid delegation.
        
        Args:
            delegator: The delegating authority
            delegate: The receiving authority
            
        Returns:
            A new DelegationError instance
        """
        return cls(
            message=f"Invalid delegation: {delegator} -> {delegate}",
            finding_code="invalid_delegation",
            affected_references=(f"delegation:{delegator}->{delegate}",),
        )
    
    @classmethod
    def expired_delegation(cls, delegation_id: str) -> DelegationError:
        """
        Create an error for an expired delegation.
        
        Args:
            delegation_id: The identifier of the expired delegation
            
        Returns:
            A new DelegationError instance
        """
        return cls(
            message=f"Expired delegation: {delegation_id}",
            finding_code="expired_delegation",
            affected_references=(f"delegation:{delegation_id}",),
        )
    
    @classmethod
    def revocation_error(cls, delegation_id: str) -> DelegationError:
        """
        Create an error for a revocation failure.
        
        Args:
            delegation_id: The identifier of the delegation to revoke
            
        Returns:
            A new DelegationError instance
        """
        return cls(
            message=f"Failed to revoke delegation: {delegation_id}",
            finding_code="revocation_failed",
            affected_references=(f"delegation:{delegation_id}",),
        )


# =============================================================================
# POLICY ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class PolicyError(GovernanceError):
    """Exception raised for policy-related errors."""
    
    @classmethod
    def undefined_policy(cls, policy_name: str) -> PolicyError:
        """
        Create an error for an undefined policy.
        
        Args:
            policy_name: The undefined policy name
            
        Returns:
            A new PolicyError instance
        """
        return cls(
            message=f"Undefined policy: {policy_name}",
            finding_code="undefined_policy",
            affected_references=(f"policy:{policy_name}",),
        )
    
    @classmethod
    def conflicting_policies(cls, policies: tuple[str, ...]) -> PolicyError:
        """
        Create an error for conflicting policies.
        
        Args:
            policies: The conflicting policy names
            
        Returns:
            A new PolicyError instance
        """
        return cls(
            message=f"Conflicting policies: {' and '.join(policies)}",
            finding_code="conflicting_policies",
            affected_references=policies,
        )
    
    @classmethod
    def inheritance_violation(cls, child_policy: str, parent_policy: str) -> PolicyError:
        """
        Create an error for policy inheritance violation.
        
        Args:
            child_policy: The child policy name
            parent_policy: The parent policy that was violated
            
        Returns:
            A new PolicyError instance
        """
        return cls(
            message=f"Policy inheritance violation: {child_policy} weakens {parent_policy}",
            finding_code="inheritance_violation",
            affected_references=(f"policy:{parent_policy}", f"policy:{child_policy}"),
        )


# =============================================================================
# PERMISSION ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class PermissionError(GovernanceError):
    """Exception raised for permission-related errors."""
    
    @classmethod
    def insufficient_permission(cls, operation: str) -> PermissionError:
        """
        Create an error for insufficient permissions.
        
        Args:
            operation: The attempted operation
            
        Returns:
            A new PermissionError instance
        """
        return cls(
            message=f"Insufficient permission for operation: {operation}",
            finding_code="insufficient_permission",
            affected_references=(f"operation:{operation}",),
        )
    
    @classmethod
    def unauthorized_operation(cls, authority: str, operation: str) -> PermissionError:
        """
        Create an error for an unauthorized operation.
        
        Args:
            authority: The authority attempting the operation
            operation: The attempted operation
            
        Returns:
            A new PermissionError instance
        """
        return cls(
            message=f"Unauthorized operation by {authority}: {operation}",
            finding_code="unauthorized_operation",
            affected_references=(f"authority:{authority}", f"operation:{operation}"),
        )


# =============================================================================
# PROHIBITION ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ProhibitionError(GovernanceError):
    """Exception raised for prohibition-related errors."""
    
    @classmethod
    def violated_prohibition(cls, operation: str, reason: str) -> ProhibitionError:
        """
        Create an error for a violated prohibition.
        
        Args:
            operation: The prohibited operation
            reason: The reason for the prohibition
            
        Returns:
            A new ProhibitionError instance
        """
        return cls(
            message=f"Prohibited operation: {operation} ({reason})",
            finding_code="prohibition_violated",
            affected_references=(f"operation:{operation}",),
        )
    
    @classmethod
    def constitutional_prohibition(cls, violation: str) -> ProhibitionError:
        """
        Create an error for a constitutional prohibition violation.
        
        Args:
            violation: The violated constitutional principle
            
        Returns:
            A new ProhibitionError instance
        """
        return cls(
            message=f"Constitutional prohibition violated: {violation}",
            finding_code="constitutional_prohibition",
            affected_references=(f"principle:{violation}",),
        )


# =============================================================================
# COMPLIANCE ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ComplianceError(GovernanceError):
    """Exception raised for compliance-related errors."""
    
    @classmethod
    def non_compliant(cls, artifact: str) -> ComplianceError:
        """
        Create an error for a non-compliant artifact.
        
        Args:
            artifact: The non-compliant artifact
            
        Returns:
            A new ComplianceError instance
        """
        return cls(
            message=f"Artifact is not compliant: {artifact}",
            finding_code="non_compliant",
            affected_references=(f"artifact:{artifact}",),
        )
    
    @classmethod
    def critical_violation(cls, principle: str) -> ComplianceError:
        """
        Create an error for a critical constitutional violation.
        
        Args:
            principle: The violated constitutional principle
            
        Returns:
            A new ComplianceError instance
        """
        return cls(
            message=f"Critical constitutional violation: {principle}",
            finding_code="critical_violation",
            affected_references=(f"principle:{principle}",),
        )


# =============================================================================
# AUDIT ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class AuditError(GovernanceError):
    """Exception raised for audit-related errors."""
    
    @classmethod
    def insufficient_scope(cls, scope: str) -> AuditError:
        """
        Create an error for an audit with insufficient scope.
        
        Args:
            scope: The audit scope
            
        Returns:
            A new AuditError instance
        """
        return cls(
            message=f"Audit scope is insufficient: {scope}",
            finding_code="insufficient_scope",
            affected_references=(f"audit:{scope}",),
        )
    
    @classmethod
    def evidence_missing(cls, required_evidence: str) -> AuditError:
        """
        Create an error for missing audit evidence.
        
        Args:
            required_evidence: The missing evidence reference
            
        Returns:
            A new AuditError instance
        """
        return cls(
            message=f"Audit evidence is missing: {required_evidence}",
            finding_code="evidence_missing",
            affected_references=(f"evidence:{required_evidence}",),
        )


# =============================================================================
# VALIDATION ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ValidationError(GovernanceError):
    """Exception raised when validation fails."""
    
    @classmethod
    def missing_required_field(cls, field_name: str) -> ValidationError:
        """
        Create an error for a missing required field.
        
        Args:
            field_name: The name of the missing field
            
        Returns:
            A new ValidationError instance
        """
        return cls(
            message=f"Missing required field: {field_name}",
            finding_code="missing_required_field",
            affected_references=(),
        )
    
    @classmethod
    def invalid_value(cls, field_name: str, value: str) -> ValidationError:
        """
        Create an error for an invalid field value.
        
        Args:
            field_name: The name of the field
            value: The invalid value
            
        Returns:
            A new ValidationError instance
        """
        return cls(
            message=f"Invalid value for {field_name}: {value}",
            finding_code="invalid_value",
            affected_references=(field_name,),
        )
    
    @classmethod
    def invalid_type(cls, field_name: str, expected_type: str) -> ValidationError:
        """
        Create an error for a field with invalid type.
        
        Args:
            field_name: The name of the field
            expected_type: The expected type
            
        Returns:
            A new ValidationError instance
        """
        return cls(
            message=f"Invalid type for {field_name}: expected {expected_type}",
            finding_code="invalid_type",
            affected_references=(field_name,),
        )


# =============================================================================
# EVOLUTION ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvolutionError(GovernanceError):
    """Exception raised for constitutional evolution errors."""
    
    @classmethod
    def invalid_proposal(cls, proposal_id: str) -> EvolutionError:
        """
        Create an error for an invalid evolution proposal.
        
        Args:
            proposal_id: The identifier of the invalid proposal
            
        Returns:
            A new EvolutionError instance
        """
        return cls(
            message=f"Invalid constitutional evolution proposal: {proposal_id}",
            finding_code="invalid_proposal",
            affected_references=(f"proposal:{proposal_id}",),
        )
    
    @classmethod
    def circular_evolution(cls, history: tuple[str, ...]) -> EvolutionError:
        """
        Create an error for circular constitution evolution.
        
        Args:
            history: The history of constitutional versions
            
        Returns:
            A new EvolutionError instance
        """
        return cls(
            message=f"Circular constitutional evolution detected: {' -> '.join(history)}",
            finding_code="circular_evolution",
            affected_references=history,
        )