# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) Enums and Type Definitions
=================================================================

Canonical enumerations for the Cognitive Coordination Governance subsystem.
All enums are deeply immutable to ensure deterministic behavior.

This module implements:

* Authority Levels (CONSTITUTIONAL, ARCHITECTURAL, COORDINATION, etc.)
* Trust Levels (ROOT, TRUSTED, CONTROLLED, RESTRICTED, SANDBOX, EXPERIMENTAL, UNTRUSTED)
* Compliance Statuses (COMPLIANT, CONDITIONALLY_COMPLIANT, NON_COMPLIANT, CRITICAL_VIOLATION, UNKNOWN)
* Audit Types
* Governance Query Types
* Findings and Limitations

All enums follow the governance laws specified in Part 3.
"""

from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass


# =============================================================================
# AUTHORITY LEVELS
# =============================================================================

class AuthorityLevel(Enum):
    """
    Hierarchical authority levels in the governance structure.
    
    Higher authority constrains lower authority.
    Authority flows downward from constitutional level.
    
    GOVERNANCE-LAW-001: Every authority possesses explicit jurisdiction
    GOVERNANCE-LAW-002: Authority shall never be inferred
    GOVERNANCE-LAW-003: Authority boundaries shall remain explicit
    
    CCG-AUTH-LAW-001: Authority levels are canonical and immutable
    CCG-AUTH-LAW-002: Higher authority constrains lower authority
    """
    CONSTITUTIONAL = "constitutional"
    """Constitutional authority - defines immutable principles."""
    
    ARCHITECTURAL = "architectural"
    """Architectural authority - governs system structure."""
    
    COORDINATION = "coordination"
    """Coordination authority - manages coordination protocols."""
    
    NETWORK = "network"
    """Network authority - governs network behavior."""
    
    SUBSYSTEM = "subsystem"
    """Subsystem authority - manages subsystem operations."""
    
    COMPONENT = "component"
    """Component authority - governs component execution."""
    
    @classmethod
    def all_levels(cls) -> tuple[AuthorityLevel, ...]:
        """Return all authority levels in hierarchical order."""
        return tuple(cls)
    
    @classmethod
    def from_string(cls, value: str) -> AuthorityLevel:
        """
        Parse a string into an authority level.
        
        Args:
            value: The string representation of the authority level
            
        Returns:
            The corresponding AuthorityLevel instance
            
        Raises:
            ValueError: If the string doesn't match any known authority level
        """
        try:
            return cls[value.upper().replace("-", "_")]
        except KeyError:
            raise ValueError(f"Unknown authority level: {value}")


# =============================================================================
# TRUST LEVELS
# =============================================================================

class TrustLevel(Enum):
    """
    Trust levels that constrain permissions and operations.
    
    Trust determines what architectural authority is granted.
    
    GOVERNANCE-TRUST-LAW-001: Every trust domain possesses one explicit trust level
    GOVERNANCE-TRUST-LAW-002: Trust shall constrain permissions
    GOVERNANCE-TRUST-LAW-003: Trust shall constrain delegation
    
    CCG-TRUST-LAW-001: Trust levels are canonical and immutable
    CCG-TRUST-LAW-002: Trust determines architectural authority
    """
    ROOT = "root"
    """Root trust level - highest privilege, typically system-critical."""
    
    TRUSTED = "trusted"
    """Trusted level - full access within defined scope."""
    
    CONTROLLED = "controlled"
    """Controlled level - access with monitoring and restrictions."""
    
    RESTRICTED = "restricted"
    """Restricted level - limited access to essential operations only."""
    
    SANDBOX = "sandbox"
    """Sandbox level - isolated execution with minimal permissions."""
    
    EXPERIMENTAL = "experimental"
    """Experimental level - temporary access for evaluation."""
    
    UNTRUSTED = "untrusted"
    """Untrusted level - minimal or no direct access."""
    
    @classmethod
    def all_levels(cls) -> tuple[TrustLevel, ...]:
        """Return all trust levels in ascending order of privilege."""
        return tuple(cls)
    
    @classmethod
    def from_string(cls, value: str) -> TrustLevel:
        """
        Parse a string into a trust level.
        
        Args:
            value: The string representation of the trust level
            
        Returns:
            The corresponding TrustLevel instance
            
        Raises:
            ValueError: If the string doesn't match any known trust level
        """
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Unknown trust level: {value}")


# =============================================================================
# COMPLIANCE STATUSES
# =============================================================================

class ComplianceStatus(Enum):
    """
    Status of a compliance evaluation.
    
    GOVERNANCE-COMP-LAW-001: Every evaluated artifact references governing principles
    GOVERNANCE-COMP-LAW-002: Compliance preserves supporting evidence
    
    CCG-COMP-LAW-001: Compliance statuses are canonical and immutable
    CCG-COMP-LAW-002: Non-compliant takes precedence over conditionally compliant
    """
    COMPLIANT = "compliant"
    """Artifact fully complies with governing principles."""
    
    CONDITIONALLY_COMPLIANT = "conditionally_compliant"
    """Artifact complies but with conditions or limitations."""
    
    NON_COMPLIANT = "non_compliant"
    """Artifact violates governing principles."""
    
    CRITICAL_VIOLATION = "critical_violation"
    """Artifact violates constitutional principles or causes critical harm."""
    
    UNKNOWN = "unknown"
    """Compliance status cannot be determined at this time."""
    
    @classmethod
    def all_statuses(cls) -> tuple[ComplianceStatus, ...]:
        """Return all compliance statuses in canonical order."""
        return tuple(cls)
    
    def is_compliant(self) -> bool:
        """Check if the status indicates compliance."""
        return self in (self.COMPLIANT, self.CONDITIONALLY_COMPLIANT)
    
    def is_violation(self) -> bool:
        """Check if the status indicates a violation."""
        return self in (self.NON_COMPLIANT, self.CRITICAL_VIOLATION)


# =============================================================================
# AUDIT TYPES
# =============================================================================

class AuditType(Enum):
    """
    Types of governance audits.
    
    GOVERNANCE-AUDIT-LAW-001: Audits shall remain observational
    GOVERNANCE-AUDIT-LAW-002: Audits shall preserve evidence
    
    CCG-AUDIT-LAW-001: Audit types are canonical and immutable
    """
    CONSTITUTION = "constitution"
    """Audit constitutional compliance."""
    
    AUTHORITY = "authority"
    """Audit authority definitions and boundaries."""
    
    POLICY = "policy"
    """Audit policy compliance and inheritance."""
    
    TRUST = "trust"
    """Audit trust domain enforcement."""
    
    COORDINATION = "coordination"
    """Audit coordination protocol compliance."""
    
    ARCHITECTURE = "architecture"
    """Audit architectural topology and boundaries."""
    
    SECURITY = "security"
    """Audit security-related governance rules."""
    
    COMPLIANCE = "compliance"
    """Audit general compliance with all governance rules."""
    
    @classmethod
    def all_types(cls) -> tuple[AuditType, ...]:
        """Return all audit types in canonical order."""
        return tuple(cls)


# =============================================================================
# GOVERNANCE QUERY TYPES
# =============================================================================

class GovernanceQueryType(Enum):
    """
    Types of governance queries.
    
    GOVERNANCE-QUERY-LAW-001: Queries shall remain read-only
    GOVERNANCE-QUERY-LAW-002: Query results preserve provenance
    
    CCG-QUERY-LAW-001: Query types are canonical and immutable
    """
    CONSTITUTION = "constitution"
    """Query the active constitution."""
    
    ACTIVE_POLICIES = "active_policies"
    """Query currently active policies for a scope."""
    
    AUTHORITY = "authority"
    """Query authority definitions and boundaries."""
    
    TRUST_DOMAIN = "trust_domain"
    """Query trust domain configurations."""
    
    COMPLIANCE_HISTORY = "compliance_history"
    """Query historical compliance evaluations."""
    
    ACTIVE_VIOLATIONS = "active_violations"
    """Query currently active violations."""
    
    AUDIT_HISTORY = "audit_history"
    """Query historical audit results."""
    
    DELEGATION_HISTORY = "delegation_history"
    """Query historical delegation records."""
    
    @classmethod
    def all_types(cls) -> tuple[GovernanceQueryType, ...]:
        """Return all query types in canonical order."""
        return tuple(cls)


# =============================================================================
# GOVERNANCE FINDINGS
# =============================================================================

class GovernanceFinding(Enum):
    """
    Types of findings that can result from governance evaluation.
    
    GOVERNANCE-FINDING-LAW-001: Findings shall be explicit and typed
    GOVERNANCE-FINDING-LAW-002: Findings preserve provenance
    
    CCG-FINDING-LAW-001: Finding types are canonical and immutable
    """
    POLICY_CONFLICT = "policy_conflict"
    """Conflicting policies detected."""
    
    AUTHORITY_CONFLICT = "authority_conflict"
    """Conflicting authority definitions."""
    
    TRUST_VIOLATION = "trust_violation"
    """Trust boundary violated."""
    
    CONSTITUTIONAL_CONFLICT = "constitutional_conflict"
    """Violation of constitutional principles."""
    
    INVALID_DELEGATION = "invalid_delegation"
    """Delegation is invalid or expired."""
    
    PERMISSION_DENIED = "permission_denied"
    """Attempted operation exceeds permissions."""
    
    PROHIBITION_VIOLATED = "prohibition_violated"
    """Operation is explicitly prohibited."""
    
    UNKNOWN = "unknown"
    """Finding type cannot be determined."""
    
    @classmethod
    def all_findings(cls) -> tuple[GovernanceFinding, ...]:
        """Return all finding types in canonical order."""
        return tuple(cls)


# =============================================================================
# GOVERNANCE LIMITATIONS
# =============================================================================

class GovernanceLimitation(Enum):
    """
    Limitations that can affect governance decisions.
    
    GOVERNANCE-LIMITATION-LAW-001: Limitations shall remain explicit
    GOVERNANCE-LIMITATION-LAW-002: Limitations preserve recoverability
    
    CCG-LIMITATION-LAW-001: Limitation types are canonical and immutable
    """
    PARTIAL_INFORMATION = "partial_information"
    """Incomplete information available."""
    
    MISSING_EVIDENCE = "missing_evidence"
    """Evidence required for evaluation is missing."""
    
    UNKNOWN_AUTHORITY = "unknown_authority"
    """Authority cannot be determined."""
    
    INCOMPLETE_POLICY = "incomplete_policy"
    """Policy definitions are incomplete."""
    
    LIMITED_AUDIT_SCOPE = "limited_audit_scope"
    """Audit scope is restricted."""
    
    PARTIAL_DETERMINISM = "partial_determinism"
    """Deterministic ordering cannot be guaranteed."""
    
    @classmethod
    def all_limitations(cls) -> tuple[GovernanceLimitation, ...]:
        """Return all limitation types in canonical order."""
        return tuple(cls)


# =============================================================================
# VIOLATION SEVERITY
# =============================================================================

class ViolationSeverity(Enum):
    """
    Severity levels for constitutional violations.
    
    GOVERNANCE-VIOL-LAW-001: Violations shall preserve justification
    GOVERNANCE-VIOL-LAW-002: Severity shall remain explicit
    
    CCG-VIOL-LAW-001: Severity levels are canonical and immutable
    """
    MINOR = "minor"
    """Minor deviation with limited impact."""
    
    MODERATE = "moderate"
    """Moderate deviation affecting some operations."""
    
    MAJOR = "major"
    """Major deviation affecting significant functionality."""
    
    CRITICAL = "critical"
    """Critical violation of constitutional principles."""
    
    @classmethod
    def all_severities(cls) -> tuple[ViolationSeverity, ...]:
        """Return all severity levels in ascending order."""
        return tuple(cls)
    
    def is_critical(self) -> bool:
        """Check if the severity is critical or worse."""
        return self in (self.MAJOR, self.CRITICAL)


# =============================================================================
# GOVERNANCE TRACE STEPS
# =============================================================================

class GovernanceTraceStep(Enum):
    """
    Steps in the governance processing trace.
    
    GOVERNANCE-TRACE-LAW-001: Trace steps shall be deterministic
    GOVERNANCE-TRACE-LAW-002: Trace preserves processing history
    
    CCG-TRACE-LAW-001: Trace step types are canonical and immutable
    """
    REQUEST_VALIDATED = "request_validated"
    """Governance request passed validation."""
    
    AUTHORITY_EVALUATED = "authority_evaluated"
    """Authority has been evaluated."""
    
    POLICY_RESOLVED = "policy_resolved"
    """Policies have been resolved for the context."""
    
    PERMISSIONS_EVALUATED = "permissions_evaluated"
    """Permissions have been evaluated."""
    
    PROHIBITIONS_EVALUATED = "prohibitions_evaluated"
    """Prohibitions have been evaluated."""
    
    COMPLIANCE_EVALUATED = "compliance_evaluated"
    """Compliance has been evaluated."""
    
    REPORT_GENERATED = "report_generated"
    """Governance report has been generated."""
    
    @classmethod
    def all_steps(cls) -> tuple[GovernanceTraceStep, ...]:
        """Return all trace steps in canonical processing order."""
        return tuple(cls)


# =============================================================================
# GOVERNANCE REQUEST STATUS
# =============================================================================

class GovernanceRequestStatus(Enum):
    """
    Status of a governance request.
    
    GOVERNANCE-REQ-LAW-001: Request status shall be explicit
    GOVERNANCE-REQ-LAW-002: Status preserves decision history
    
    CCG-REQ-LAW-001: Request statuses are canonical and immutable
    """
    PENDING = "pending"
    """Request is pending evaluation."""
    
    VALIDATING = "validating"
    """Request is being validated."""
    
    AUTHORITY_CHECKING = "authority_checking"
    """Authority verification in progress."""
    
    COMPLIANCE_CHECKING = "compliance_checking"
    """Compliance evaluation in progress."""
    
    APPROVED = "approved"
    """Request has been approved."""
    
    REJECTED = "rejected"
    """Request has been rejected."""
    
    CONDITIONALLY_APPROVED = "conditionally_approved"
    """Request approved with conditions."""
    
    EXPIRED = "expired"
    """Request has expired."""
    
    @classmethod
    def all_statuses(cls) -> tuple[GovernanceRequestStatus, ...]:
        """Return all request statuses in canonical order."""
        return tuple(cls)
    
    def is_final(self) -> bool:
        """Check if the status is a final decision."""
        return self in (self.APPROVED, self.REJECTED, self.CONDITIONALLY_APPROVED, self.EXPIRED)


# =============================================================================
# CONSTITUTIONAL EVOLUTION STATUS
# =============================================================================

class ConstitutionalEvolutionStatus(Enum):
    """
    Status of constitutional evolution proposals.
    
    GOVERNANCE-EVOL-LAW-001: Evolution shall remain explicit
    GOVERNANCE-EVOL-LAW-002: History shall be preserved
    
    CCG-EVOL-LAW-001: Evolution statuses are canonical and immutable
    """
    PROPOSED = "proposed"
    """Constitutional change has been proposed."""
    
    REVIEWING = "reviewing"
    """Constitutional change is under review."""
    
    VALIDATING = "validating"
    """Validation in progress for the constitutional change."""
    
    APPROVED = "approved"
    """Constitutional change approved."""
    
    REJECTED = "rejected"
    """Constitutional change rejected."""
    
    IMPLEMENTED = "implemented"
    """Constitutional change has been implemented (creates new constitution)."""
    
    ABORTED = "aborted"
    """Evolution process was aborted."""
    
    @classmethod
    def all_statuses(cls) -> tuple[ConstitutionalEvolutionStatus, ...]:
        """Return all evolution statuses in canonical order."""
        return tuple(cls)


# =============================================================================
# CONSTITUTIONAL PRINCIPLE ENFORCEMENT
# =============================================================================

class PrincipleEnforcement(Enum):
    """
    Modes of constitutional principle enforcement.
    
    GOVERNANCE-PRINC-LAW-001: Principles shall define architectural constraints
    GOVERNANCE-PRINC-LAW-002: Principles shall remain implementation-independent
    
    CCG-PRINC-LAW-001: Enforcement modes are canonical and immutable
    """
    STRICT = "strict"
    """Principle must be fully satisfied."""
    
    MONITORING = "monitoring"
    """Principle violations are monitored but not blocked."""
    
    NOT_APPLICABLE = "not_applicable"
    """Principle does not apply in this context."""
    
    @classmethod
    def all_modes(cls) -> tuple[PrincipleEnforcement, ...]:
        """Return all enforcement modes in canonical order."""
        return tuple(cls)