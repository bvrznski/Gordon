# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) - Authority Model
=========================================================

Explicit authority definitions and hierarchy.
Authority flows downward; responsibility flows upward.

Following:
* AUTHORITY-LAW-001 through AUTHORITY-LAW-008
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from .enums import AuthorityLevel


# =============================================================================
# AUTHORITY BOUNDARY
# =============================================================================

@dataclass(frozen=True, slots=True)
class AuthorityBoundary:
    """
    Immutable authority boundary definition.
    
    AUTHORITY-BND-INV-001: Boundary is immutable
    AUTHORITY-BND-INV-002: Boundary has no runtime references
    
    AUTHORITY-LAW-003: Authority boundaries shall remain explicit
    """
    source_authority_ref: str
    """Reference to the authority defining this boundary."""
    
    target_scope: str
    """Scope that is outside this authority's boundary."""
    
    cross_boundary_requires: str = "explicit_approval"
    """What is required to cross this boundary."""


# =============================================================================
# AUTHORITY DEFINITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class AuthorityDefinition:
    """
    Immutable authority definition with explicit jurisdiction.
    
    AUTHORITY-LAW-001: Every authority shall possess explicit jurisdiction
    AUTHORITY-LAW-002: Authority shall never be inferred
    AUTHORITY-LAW-003: Authority boundaries shall remain explicit
    AUTHORITY-LAW-004: Authority inheritance shall remain explicit
    AUTHORITY-LAW-005: Authority shall preserve provenance
    AUTHORITY-LAW-006: Authority revisions shall preserve lineage
    AUTHORITY-LAW-007: Historical authority definitions shall remain inspectable
    AUTHORITY-LAW-008: Authority evaluation shall remain deterministic
    
    CCG-AUTH-INV-001: Authority is immutable (deeply frozen)
    CCG-AUTH-INV-002: Authority has no runtime references
    """
    authority_identity: str
    """Unique identifier for this authority."""
    
    authority_scope: str
    """Scope of this authority's jurisdiction."""
    
    jurisdiction: tuple[str, ...]
    """Explicit jurisdiction boundaries."""
    
    permissions: tuple[str, ...] = field(default_factory=tuple)
    """Permissions granted to this authority."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this authority's power."""
    
    authority_level: AuthorityLevel = AuthorityLevel.COMPONENT
    """Hierarchical level of this authority."""
    
    parent_authority_ref: str | None = None
    """Reference to parent authority (if any)."""
    
    revision: int = 1
    """Revision number of this authority definition."""
    
    provenance_ref: str | None = None
    """Reference to authority provenance record."""
    
    @classmethod
    def create(
        cls,
        identity: str,
        scope: str,
        jurisdiction: tuple[str, ...],
        permissions: tuple[str, ...] | None = None,
        limitations: tuple[str, ...] | None = None,
        level: AuthorityLevel = AuthorityLevel.COMPONENT,
        parent_ref: str | None = None,
    ) -> AuthorityDefinition:
        """
        Create a new authority definition.
        
        Args:
            identity: Unique identifier
            scope: Scope of jurisdiction
            jurisdiction: Explicit jurisdiction boundaries
            permissions: Granted permissions
            limitations: Power limitations
            level: Hierarchical level
            parent_ref: Parent authority reference
            
        Returns:
            A new AuthorityDefinition instance
        """
        return cls(
            authority_identity=identity,
            authority_scope=scope,
            jurisdiction=jurisdiction,
            permissions=permissions or (),
            limitations=limitations or (),
            authority_level=level,
            parent_authority_ref=parent_ref,
            revision=1,
            provenance_ref=None,
        )
    
    def can_cross_boundary(self, target_scope: str) -> bool:
        """
        Check if this authority can cross to a target scope.
        
        Args:
            target_scope: The target scope to check
            
        Returns:
            True if the authority can access the target scope
        """
        return target_scope in self.jurisdiction


# =============================================================================
# CANONICAL AUTHORITY DEFINITIONS
# =============================================================================

class CanonicalAuthorities:
    """
    Canonical authority definitions for Gordon.
    
    Authority hierarchy:
        CONSTITUTIONAL (defines immutable principles)
            ↓
        ARCHITECTURAL (governs system structure)
            ↓
        COORDINATION (manages coordination protocols)
            ↓
        NETWORK (governs network behavior)
            ↓
        SUBSYSTEM (manages subsystem operations)
            ↓
        COMPONENT (govern component execution)
    """
    
    CONSTITUTIONAL = AuthorityDefinition.create(
        identity="authority:constitutional",
        scope="constitution",
        jurisdiction=("principles", "revisions", "history"),
        permissions=(
            "define_principles",
            "approve_revisions",
            "audit_system",
            "declare_violations",
        ),
        limitations=(
            "cannot_perform_cognition",
            "cannot_perform_orchestration",
            "cannot_modify_history",
        ),
        level=AuthorityLevel.CONSTITUTIONAL,
    )
    
    ARCHITECTURAL = AuthorityDefinition.create(
        identity="authority:architectural",
        scope="architecture",
        jurisdiction=("structure", "modules", "interfaces"),
        permissions=(
            "define_modules",
            "establish_interfaces",
            "audit_topology",
        ),
        limitations=(
            "cannot_define_principles",
            "cannot_modify_constitution",
        ),
        level=AuthorityLevel.ARCHITECTURAL,
    )
    
    COORDINATION = AuthorityDefinition.create(
        identity="authority:coordination",
        scope="coordination",
        jurisdiction=("protocols", "events", "synchronization"),
        permissions=(
            "define_protocols",
            "schedule_events",
            "manage_synchronization",
        ),
        limitations=(
            "cannot_define_principles",
            "cannot_modify_constitution",
            "cannot_override_authority_boundaries",
        ),
        level=AuthorityLevel.COORDINATION,
    )
    
    NETWORK = AuthorityDefinition.create(
        identity="authority:network",
        scope="networks",
        jurisdiction=("network_behavior", "projections", "readiness"),
        permissions=(
            "publish_projections",
            "declare_readiness",
            "request_resources",
        ),
        limitations=(
            "cannot_define_principles",
            "cannot_modify_constitution",
            "cannot_override_coordination_protocol",
        ),
        level=AuthorityLevel.NETWORK,
    )
    
    SUBSYSTEM = AuthorityDefinition.create(
        identity="authority:subsystem",
        scope="subsystems",
        jurisdiction=("operations", "state", "transitions"),
        permissions=(
            "manage_state",
            "perform_transitions",
            "request_orchestration",
        ),
        limitations=(
            "cannot_define_principles",
            "cannot_modify_constitution",
            "cannot_bypass_validation",
        ),
        level=AuthorityLevel.SUBSYSTEM,
    )
    
    COMPONENT = AuthorityDefinition.create(
        identity="authority:component",
        scope="components",
        jurisdiction=("execution", "results", "outputs"),
        permissions=(
            "execute_tasks",
            "produce_results",
            "report_status",
        ),
        limitations=(
            "cannot_define_principles",
            "cannot_modify_constitution",
            "cannot_bypass_validation",
            "cannot_override_authority_boundaries",
        ),
        level=AuthorityLevel.COMPONENT,
    )
    
    @classmethod
    def all_authities(cls) -> tuple[AuthorityDefinition, ...]:
        """Return all canonical authorities in hierarchical order."""
        return (
            cls.CONSTITUTIONAL,
            cls.ARCHITECTURAL,
            cls.COORDINATION,
            cls.NETWORK,
            cls.SUBSYSTEM,
            cls.COMPONENT,
        )
    
    @classmethod
    def get_by_level(cls, level: AuthorityLevel) -> AuthorityDefinition | None:
        """
        Get authority by its hierarchical level.
        
        Args:
            level: The authority level
            
        Returns:
            The authority definition or None if not found
        """
        for a in cls.all_authities():
            if a.authority_level == level:
                return a
        return None
    
    @classmethod
    def get_by_scope(cls, scope: str) -> AuthorityDefinition | None:
        """
        Get authority by its scope.
        
        Args:
            scope: The authority scope
            
        Returns:
            The authority definition or None if not found
        """
        for a in cls.all_authities():
            if a.authority_scope == scope:
                return a
        return None


# =============================================================================
# AUTHORITY VALIDATION RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class AuthorityValidationResult:
    """
    Immutable result of authority validation.
    
    AUTH-VALID-INV-001: Result is immutable
    AUTH-VALID-INV-002: Result has no runtime references
    
    CCG-AUTH-VAL-LAW-001: Validation results preserve evidence
    CCG-AUTH-VAL-LAW-002: Validation results are deterministic
    """
    authority_identity: str
    """Identity of the validated authority."""
    
    validation_passed: bool
    """Whether the authority is valid."""
    
    jurisdiction_valid: bool = True
    """Whether jurisdiction boundaries are consistent."""
    
    permissions_valid: bool = True
    """Whether permission definitions are consistent."""
    
    limitations_valid: bool = True
    """Whether limitation definitions are consistent."""
    
    parent_authority_ref_valid: bool = True
    """Whether parent authority reference is valid."""
    
    evidence: tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting the validation result."""
    
    @classmethod
    def of_valid(cls, authority_id: str) -> AuthorityValidationResult:
        """
        Create a valid authority validation result.
        
        Args:
            authority_id: The validated authority identity
            
        Returns:
            A new AuthorityValidationResult instance
        """
        return cls(
            authority_identity=authority_id,
            validation_passed=True,
            jurisdiction_valid=True,
            permissions_valid=True,
            limitations_valid=True,
            parent_authority_ref_valid=True,
        )
    
    @classmethod
    def of_invalid(cls, authority_id: str) -> AuthorityValidationResult:
        """
        Create an invalid authority validation result.
        
        Args:
            authority_id: The validated authority identity
            
        Returns:
            A new AuthorityValidationResult instance
        """
        return cls(
            authority_identity=authority_id,
            validation_passed=False,
        )
    
    def is_valid(self) -> bool:
        """Check if the authority validation passed."""
        return self.validation_passed
    
    def has_issues(self) -> tuple[str, ...]:
        """Get list of issues found during validation."""
        issues = []
        if not self.jurisdiction_valid:
            issues.append("invalid_jurisdiction")
        if not self.permissions_valid:
            issues.append("invalid_permissions")
        if not self.limitations_valid:
            issues.append("invalid_limitations")
        if not self.parent_authority_ref_valid:
            issues.append("invalid_parent_reference")
        return tuple(issues)