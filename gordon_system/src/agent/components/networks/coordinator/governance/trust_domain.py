# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) - Trust Domain Model
============================================================

Trust domains that constrain permissions and delegation.
Trust determines what architectural authority is granted.

Following:
* TRUST-LAW-001 through TRUST-LAW-008
"""

from __future__ import annotations

from dataclasses import dataclass, field


# =============================================================================
# TRUST DOMAIN DEFINITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class TrustDomain:
    """
    Immutable trust domain definition.
    
    Trust domains constrain permissions and delegation.
    
    TRUST-LAW-001: Every trust domain possesses one explicit trust level
    TRUST-LAW-002: Trust shall constrain permissions
    TRUST-LAW-003: Trust shall constrain delegation
    TRUST-LAW-004: Trust boundaries shall remain explicit
    TRUST-LAW-005: Trust provenance shall remain complete
    TRUST-LAW-006: Trust revisions shall preserve lineage
    TRUST-LAW-007: Historical trust domains shall remain inspectable
    TRUST-LAW-008: Trust evaluation shall remain deterministic
    
    CCG-TRUST-INV-001: Trust domain is immutable (deeply frozen)
    CCG-TRUST-INV-002: Trust domain has no runtime references
    """
    domain_identity: str
    """Unique identifier for this trust domain."""
    
    domain_scope: str
    """Scope of this trust domain."""
    
    trust_level: str
    """Trust level (from TrustLevel enum)."""
    
    permitted_operations: tuple[str, ...] = field(default_factory=tuple)
    """Operations permitted within this domain."""
    
    prohibited_operations: tuple[str, ...] = field(default_factory=tuple)
    """Operations prohibited within this domain."""
    
    revision: int = 1
    """Revision number of this trust domain definition."""
    
    provenance_ref: str | None = None
    """Reference to trust domain provenance record."""
    
    @classmethod
    def create(
        cls,
        identity: str,
        scope: str,
        trust_level: str,
        permitted_ops: tuple[str, ...] | None = None,
        prohibited_ops: tuple[str, ...] | None = None,
    ) -> TrustDomain:
        """
        Create a new trust domain.
        
        Args:
            identity: Unique identifier
            scope: Domain scope
            trust_level: Trust level string
            permitted_ops: Permitted operations
            prohibited_ops: Prohibited operations
            
        Returns:
            A new TrustDomain instance
        """
        return cls(
            domain_identity=identity,
            domain_scope=scope,
            trust_level=trust_level,
            permitted_operations=permitted_ops or (),
            prohibited_operations=prohibited_ops or (),
            revision=1,
            provenance_ref=None,
        )
    
    def can_perform(self, operation: str) -> bool:
        """
        Check if an operation is permitted in this domain.
        
        Args:
            operation: The operation to check
            
        Returns:
            True if the operation is permitted
        """
        return (
            operation not in self.prohibited_operations and
            (operation in self.permitted_operations or not self.permitted_operations)
        )
    
    def can_delegate(self) -> bool:
        """Check if delegation is allowed within this trust domain."""
        return "delegate" in self.permitted_operations
    
    def is_high_trust(self) -> bool:
        """
        Check if this domain has high or root trust level.
        
        Returns:
            True for HIGH or ROOT trust levels
        """
        return self.trust_level in ("root", "trusted")


# =============================================================================
# CANONICAL TRUST DOMAINS
# =============================================================================

class CanonicalTrustDomains:
    """
    Canonical trust domains for Gordon.
    
    Trust hierarchy determines architectural authority granted.
    """
    
    CORE = TrustDomain.create(
        identity="trust:core",
        scope="core:architectural",
        trust_level="root",
        permitted_ops=(
            "define_constitution",
            "define_principles",
            "audit_all",
            "declare_violations",
            "override_policies",
        ),
    )
    
    COORDINATION = TrustDomain.create(
        identity="trust:coordination",
        scope="coordination:protocol",
        trust_level="trusted",
        permitted_ops=(
            "schedule_coordination",
            "publish_events",
            "manage_synchronization",
            "resolve_dependencies",
        ),
    )
    
    MEMORY = TrustDomain.create(
        identity="trust:memory",
        scope="memory:storage",
        trust_level="trusted",
        permitted_ops=(
            "read_history",
            "write_memory",
            "consolidate_memories",
            "retrieve_context",
        ),
    )
    
    PLANNING = TrustDomain.create(
        identity="trust:planning",
        scope="planning:strategy",
        trust_level="trusted",
        permitted_ops=(
            "generate_plans",
            "evaluate_options",
            "allocate_resources",
            "set_priorities",
        ),
    )
    
    EXTERNAL_INTERFACES = TrustDomain.create(
        identity="trust:external",
        scope="external:interfaces",
        trust_level="controlled",
        permitted_ops=(
            "read_external_data",
            "send_messages",
            "receive_responses",
        ),
        prohibited_ops=(
            "modify_internal_state",
            "override_authority",
            "bypass_validation",
        ),
    )
    
    EXPERIMENTAL = TrustDomain.create(
        identity="trust:experimental",
        scope="experimental:test",
        trust_level="sandbox",
        permitted_ops=(
            "test_new_features",
            "run_experiments",
            "collect_metrics",
        ),
        prohibited_ops=(
            "modify_production_state",
            "override_constitution",
            "access_sensitive_data",
        ),
    )
    
    SANDBOX = TrustDomain.create(
        identity="trust:sandbox",
        scope="sandbox:isolated",
        trust_level="sandbox",
        permitted_ops=(
            "execute_untrusted_code",
            "collect_diagnostics",
            "report_errors",
        ),
        prohibited_ops=(
            "modify_shared_state",
            "access_memory",
            "network_communication",
        ),
    )
    
    @classmethod
    def all_domains(cls) -> tuple[TrustDomain, ...]:
        """Return all canonical trust domains."""
        return (
            cls.CORE,
            cls.COORDINATION,
            cls.MEMORY,
            cls.PLANNING,
            cls.EXTERNAL_INTERFACES,
            cls.EXPERIMENTAL,
            cls.SANDBOX,
        )
    
    @classmethod
    def get_by_scope(cls, scope: str) -> TrustDomain | None:
        """
        Get trust domain by its scope.
        
        Args:
            scope: The domain scope
            
        Returns:
            The trust domain or None if not found
        """
        for d in cls.all_domains():
            if d.domain_scope == scope:
                return d
        return None
    
    @classmethod
    def get_by_identity(cls, identity: str) -> TrustDomain | None:
        """
        Get trust domain by its identity.
        
        Args:
            identity: The domain identity
            
        Returns:
            The trust domain or None if not found
        """
        for d in cls.all_domains():
            if d.domain_identity == identity:
                return d
        return None


# =============================================================================
# TRUST VERIFICATION RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class TrustVerificationResult:
    """
    Immutable result of trust verification.
    
    CCG-TRUST-VER-INV-001: Result is immutable
    CCG-TRUST-VER-INV-002: Result has no runtime references
    
    CCG-TRUST-VER-LAW-001: Verification results preserve evidence
    CCG-TRUST-VER-LAW-002: Verification results are deterministic
    """
    domain_identity: str
    """Identity of the verified trust domain."""
    
    verification_passed: bool
    """Whether the trust level is valid."""
    
    trust_level_valid: bool = True
    """Whether the assigned trust level is recognized."""
    
    permissions_consistent: bool = True
    """Whether permitted and prohibited operations are consistent."""
    
    boundaries_defined: bool = True
    """Whether domain boundaries are explicitly defined."""
    
    evidence: tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting the verification result."""
    
    @classmethod
    def of_valid(cls, domain_id: str) -> TrustVerificationResult:
        """
        Create a valid trust verification result.
        
        Args:
            domain_id: The verified domain identity
            
        Returns:
            A new TrustVerificationResult instance
        """
        return cls(
            domain_identity=domain_id,
            verification_passed=True,
            trust_level_valid=True,
            permissions_consistent=True,
            boundaries_defined=True,
        )
    
    @classmethod
    def of_invalid(cls, domain_id: str) -> TrustVerificationResult:
        """
        Create an invalid trust verification result.
        
        Args:
            domain_id: The verified domain identity
            
        Returns:
            A new TrustVerificationResult instance
        """
        return cls(
            domain_identity=domain_id,
            verification_passed=False,
        )
    
    def is_valid(self) -> bool:
        """Check if the trust verification passed."""
        return self.verification_passed
    
    def has_issues(self) -> tuple[str, ...]:
        """Get list of issues found during verification."""
        issues = []
        if not self.trust_level_valid:
            issues.append("invalid_trust_level")
        if not self.permissions_consistent:
            issues.append("inconsistent_permissions")
        if not self.boundaries_defined:
            issues.append("undefined_boundaries")
        return tuple(issues)