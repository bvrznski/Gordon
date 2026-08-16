# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) Subsystem
==================================================

Canonical governance framework for the Gordon cognitive architecture.

This package implements:

* Constitutional governance - immutable architectural principles
* Authority model - explicit jurisdiction and delegation  
* Policy system - hierarchical governance policies
* Trust domains - trust-based permission control
* Compliance evaluation - constitutional compliance checking
* Audit framework - architectural compliance audits

Governance defines what is permitted. It never performs cognition,
coordination, or orchestration.

Following the normative specification in Part 3 of Phase 4.11.9.
"""

from __future__ import annotations

# Core models
from gordon_system.src.agent.components.networks.coordinator.governance.principle import (
    ConstitutionalPrinciple,
    CanonicalPrinciples,
)

from gordon_system.src.agent.components.networks.coordinator.governance.constitution import (
    ConstitutionIdentity,
    Constitution,
    ConstitutionalEvolutionProposal,
)

# Authority
from gordon_system.src.agent.components.networks.coordinator.governance.authority import (
    AuthorityBoundary,
    AuthorityDefinition,
    CanonicalAuthorities,
    AuthorityValidationResult,
)

# Delegation
from gordon_system.src.agent.components.networks.coordinator.governance.delegation import (
    Delegation,
    DelegationHierarchy,
    DelegationValidationResult,
)

# Trust Domains
from gordon_system.src.agent.components.networks.coordinator.governance.trust_domain import (
    TrustDomain,
    CanonicalTrustDomains,
    TrustVerificationResult,
)

# Engine
from gordon_system.src.agent.components.networks.coordinator.governance.engine import (
    CognitiveGovernanceEngine,
    GovernanceRequest,
    GovernanceResult,
)

# Permissions
from gordon_system.src.agent.components.networks.coordinator.governance.permissions import (
    Permission,
    Prohibition,
    CanonicalPermissions,
    CanonicalProhibitions,
    PermissionProtocol,
)

# Policy
from gordon_system.src.agent.components.networks.coordinator.governance.policy import (
    GovernancePolicy,
    PolicyHierarchy,
    PolicyValidationResult,
    PolicyConflictResolution,
)

# Compliance
from gordon_system.src.agent.components.networks.coordinator.governance.compliance import (
    ComplianceEvaluation,
    ConstitutionalViolation,
    ComplianceReport,
)

# Audit
from gordon_system.src.agent.components.networks.coordinator.governance.audit import (
    GovernanceAudit,
    AuditReport,
    AuditHistory,
    AuditTypeRegistry,
)

# Enums
from gordon_system.src.agent.components.networks.coordinator.governance.enums import (
    AuthorityLevel,
    TrustLevel,
    ComplianceStatus,
    AuditType,
    GovernanceQueryType,
    GovernanceFinding,
    GovernanceLimitation,
    ViolationSeverity,
    GovernanceTraceStep,
    GovernanceRequestStatus,
    ConstitutionalEvolutionStatus,
    PrincipleEnforcement,
)

# Exceptions
from gordon_system.src.agent.components.networks.coordinator.governance.exceptions import (
    GovernanceError,
    ConstitutionError,
    AuthorityError,
    DelegationError,
    PolicyError,
    PermissionError,
    ProhibitionError,
    ComplianceError,
    AuditError,
    ValidationError,
    EvolutionError,
)

# Export all public names
__all__: tuple[str, ...] = (
    # Principles
    "ConstitutionalPrinciple",
    "CanonicalPrinciples",
    # Constitution
    "ConstitutionIdentity",
    "Constitution",
    "ConstitutionalEvolutionProposal",
    # Authority
    "AuthorityBoundary",
    "AuthorityDefinition",
    "CanonicalAuthorities",
    "AuthorityValidationResult",
    # Delegation
    "Delegation",
    "DelegationHierarchy",
    "DelegationValidationResult",
    # Trust Domains
    "TrustDomain",
    "CanonicalTrustDomains",
    "TrustVerificationResult",
    # Engine
    "CognitiveGovernanceEngine",
    "GovernanceRequest",
    "GovernanceResult",
    # Permissions
    "Permission",
    "Prohibition",
    "CanonicalPermissions",
    "CanonicalProhibitions",
    "PermissionProtocol",
    # Policy
    "GovernancePolicy",
    "PolicyHierarchy",
    "PolicyValidationResult",
    "PolicyConflictResolution",
    # Compliance
    "ComplianceEvaluation",
    "ConstitutionalViolation",
    "ComplianceReport",
    # Audit
    "GovernanceAudit",
    "AuditReport",
    "AuditHistory",
    "AuditTypeRegistry",
    # Enums
    "AuthorityLevel",
    "TrustLevel",
    "ComplianceStatus",
    "AuditType",
    "GovernanceQueryType",
    "GovernanceFinding",
    "GovernanceLimitation",
    "ViolationSeverity",
    "GovernanceTraceStep",
    "GovernanceRequestStatus",
    "ConstitutionalEvolutionStatus",
    "PrincipleEnforcement",
    # Exceptions
    "GovernanceError",
    "ConstitutionError",
    "AuthorityError",
    "DelegationError",
    "PolicyError",
    "PermissionError",
    "ProhibitionError",
    "ComplianceError",
    "AuditError",
    "ValidationError",
    "EvolutionError",
)