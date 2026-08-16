# Gordon Cognitive Architecture - Phase 4.11.1
# ===========================================

"""
Coordination Network Exceptions and Error Types
==============================================

Canonical exception hierarchy for the Coordination Network.
All exceptions are deeply immutable to ensure deterministic error handling.
"""

from __future__ import annotations

from dataclasses import dataclass


# =============================================================================
# BASE COORDINATION EXCEPTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationError(Exception):
    """
    Base exception for all coordination errors.
    
    COORD-EXC-INV-001: Errors are immutable
    COORD-EXC-INV-002: Errors have no runtime references
    
    COORD-LAW-035: All coordination errors preserve structure
    """
    message: str
    """Human-readable error message."""
    
    finding_code: str = "unknown"
    """Canonical finding code for structured handling."""
    
    affected_references: tuple[str, ...] = ()
    """References to artifacts affected by this error."""
    
    @classmethod
    def of(cls, message: str, finding_code: str = "unknown") -> CoordinationError:
        """
        Create a coordination error with a finding code.
        
        Args:
            message: Human-readable description of the error
            finding_code: Canonical code for structured handling
            
        Returns:
            A new CoordinationError instance
        """
        return cls(
            message=message,
            finding_code=finding_code,
            affected_references=(),
        )

    def with_reference(self, ref: str) -> CoordinationError:
        """Add an affected reference and return a new error."""
        return CoordinationError(
            message=self.message,
            finding_code=self.finding_code,
            affected_references=(*self.affected_references, ref),
        )


# =============================================================================
# MEMBERSHIP ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class MembershipError(CoordinationError):
    """Exception raised for membership-related errors."""
    
    @classmethod
    def unknown_network(cls, network_kind: str) -> MembershipError:
        """
        Create an error for an unknown network kind.
        
        Args:
            network_kind: The unrecognized network kind
            
        Returns:
            A new MembershipError instance
        """
        return cls(
            message=f"Unknown coordinated network kind: {network_kind}",
            finding_code="unknown_network",
            affected_references=(f"network:{network_kind}",),
        )

    @classmethod
    def duplicate_member(cls, network_id: str) -> MembershipError:
        """
        Create an error for a duplicate network member.
        
        Args:
            network_id: The duplicate network identity
            
        Returns:
            A new MembershipError instance
        """
        return cls(
            message=f"Duplicate network member: {network_id}",
            finding_code="duplicate_member",
            affected_references=(f"member:{network_id}",),
        )

    @classmethod
    def missing_required(cls, required_kind: str) -> MembershipError:
        """
        Create an error for a missing required network.
        
        Args:
            required_kind: The kind of the missing required network
            
        Returns:
            A new MembershipError instance
        """
        return cls(
            message=f"Required network kind not available: {required_kind}",
            finding_code="missing_required_network",
            affected_references=(f"kind:{required_kind}",),
        )


# =============================================================================
# PROJECTION ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ProjectionError(CoordinationError):
    """Exception raised for projection-related errors."""
    
    @classmethod
    def missing_projection(cls, network_id: str) -> ProjectionError:
        """
        Create an error for a missing network projection.
        
        Args:
            network_id: The identity of the missing projection's network
            
        Returns:
            A new ProjectionError instance
        """
        return cls(
            message=f"Missing projection for network: {network_id}",
            finding_code="missing_network_projection",
            affected_references=(f"projection:{network_id}",),
        )

    @classmethod
    def invalid_contract(cls, network_id: str, expected_version: str) -> ProjectionError:
        """
        Create an error for a projection with an incompatible contract.
        
        Args:
            network_id: The identity of the network
            expected_version: The required contract version
            
        Returns:
            A new ProjectionError instance
        """
        return cls(
            message=f"Projection contract version mismatch for {network_id}: "
                    f"expected={expected_version}",
            finding_code="contract_version_mismatch",
            affected_references=(f"projection:{network_id}",),
        )

    @classmethod
    def stale_projection(cls, network_id: str, current_revision: int) -> ProjectionError:
        """
        Create an error for a stale projection.
        
        Args:
            network_id: The identity of the network
            current_revision: The expected revision number
            
        Returns:
            A new ProjectionError instance
        """
        return cls(
            message=f"Stale projection for {network_id}: "
                    f"expected_revision={current_revision}",
            finding_code="stale_network_projection",
            affected_references=(f"projection:{network_id}",),
        )


# =============================================================================
# CONSTRAINT ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConstraintError(CoordinationError):
    """Exception raised for constraint-related errors."""
    
    @classmethod
    def conflicting(cls, constraint_a: str, constraint_b: str) -> ConstraintError:
        """
        Create an error for conflicting constraints.
        
        Args:
            constraint_a: First conflicting constraint
            constraint_b: Second conflicting constraint
            
        Returns:
            A new ConstraintError instance
        """
        return cls(
            message=f"Conflicting constraints: {constraint_a} vs {constraint_b}",
            finding_code="constraint_conflict",
            affected_references=(constraint_a, constraint_b),
        )

    @classmethod
    def blocking(cls, network_id: str, constraint_kind: str) -> ConstraintError:
        """
        Create an error for a blocking constraint.
        
        Args:
            network_id: The identity of the blocked network
            constraint_kind: Kind of the blocking constraint
            
        Returns:
            A new ConstraintError instance
        """
        return cls(
            message=f"Blocking constraint on {network_id}: {constraint_kind}",
            finding_code="participant_blocked",
            affected_references=(f"network:{network_id}", f"constraint:{constraint_kind}"),
        )


# =============================================================================
# DEPENDENCY ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class DependencyError(CoordinationError):
    """Exception raised for dependency-related errors."""
    
    @classmethod
    def unresolved(cls, dependent: str, prerequisite: str) -> DependencyError:
        """
        Create an error for an unresolved dependency.
        
        Args:
            dependent: The component with the dependency
            prerequisite: The required component
            
        Returns:
            A new DependencyError instance
        """
        return cls(
            message=f"Unresolved dependency: {dependent} requires {prerequisite}",
            finding_code="unresolved_dependency",
            affected_references=(f"dependency:{dependent}->{prerequisite}",),
        )

    @classmethod
    def cyclic(cls, cycle_members: tuple[str, ...]) -> DependencyError:
        """
        Create an error for a circular dependency.
        
        Args:
            cycle_members: The members involved in the cycle
            
        Returns:
            A new DependencyError instance
        """
        return cls(
            message=f"Circular dependency detected: {' -> '.join(cycle_members)}",
            finding_code="dependency_cycle",
            affected_references=cycle_members,
        )


# =============================================================================
# VALIDATION FAILURE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ValidationFailure(CoordinationError):
    """
    Exception raised when validation fails.
    
    Unlike other errors, ValidationFailure indicates that the input
    was invalid and coordination cannot proceed.
    """
    
    @classmethod
    def missing_required_field(cls, field_name: str) -> ValidationFailure:
        """
        Create an error for a missing required field.
        
        Args:
            field_name: The name of the missing field
            
        Returns:
            A new ValidationFailure instance
        """
        return cls(
            message=f"Missing required field: {field_name}",
            finding_code="missing_required_field",
            affected_references=(),
        )

    @classmethod
    def invalid_value(cls, field_name: str, value: str) -> ValidationFailure:
        """
        Create an error for an invalid field value.
        
        Args:
            field_name: The name of the field
            value: The invalid value
            
        Returns:
            A new ValidationFailure instance
        """
        return cls(
            message=f"Invalid value for {field_name}: {value}",
            finding_code="invalid_value",
            affected_references=(field_name,),
        )