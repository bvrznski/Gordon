# Default Network Integration Contracts - Package Metadata (Phase 4.3.13)
# ========================================================================

"""
Package metadata for the Default Network Integration Contracts.

This module defines versioning and documentation for Phase 4.3.13.
"""

from __future__ import annotations

# =============================================================================
# PACKAGE VERSION
# =============================================================================

VERSION = "0.1.0"
"""Package semantic version following PEP 440."""

__version__ = VERSION
"""Alias for VERSION."""

# =============================================================================
# PHASE IDENTIFIER
# =============================================================================

PHASE_ID = "Phase 4.3.13"
"""Canonical phase identifier."""

PHASE_TITLE = "Default Network Integration Contracts"
"""Human-readable title for this phase."""

# =============================================================================
# PACKAGE SUMMARY
# =============================================================================

SUMMARY = """\
Canonical DefaultNetwork integration contract layer for Phase 4.3.13.

This package provides typed, directionally-correct, authority-safe boundaries
between the Default Network and all external systems.
"""

# =============================================================================
# ARCHITECTURAL INVARIANTS
# =============================================================================

ARCHITECTURAL_INVARIANTS = [
    "DEFAULT-INT-INV-001: Every integration occurs through an explicit typed port",
    "DEFAULT-INT-INV-002: Every port has one explicit semantic owner and direction",
    "DEFAULT-INT-INV-003: Ports define semantics; adapters define delivery",
    "DEFAULT-INT-INV-004: No contract contains a live external implementation object",
    "DEFAULT-INT-INV-005: Every inbound result references a known outbound request",
    "DEFAULT-INT-INV-006: Every authority decision references a known proposal and target revision",
    "DEFAULT-INT-INV-007: Correlation and causation remain distinct",
    "DEFAULT-INT-INV-008: Every externally deliverable request has an idempotency key",
    "DEFAULT-INT-INV-009: Duplicate delivery does not cause duplicate semantic effects",
    "DEFAULT-INT-INV-010: Arrival order is not used unless the contract declares ordering semantics",
]

# =============================================================================
# EXPORTED COMPONENTS
# =============================================================================

EXPORTED_COMPONENTS = [
    # Core types
    "PortDirection",
    "IntegrationId",
    "RequestId",
    "ResultId",
    "ProposalId",
    "DecisionId",
    "CorrelationId",
    "CausationId",
    "SemanticTime",
    "AuthorityKind",
    "AuthorityReference",
    
    # Classifications
    "FactualityClassification",
    "PrivacyClassification",
    "DisclosureClassification",
    
    # Provenance
    "IntegrationProvenance",
    "InvocationProvenance",
    "ResultProvenance",
    "ProposalProvenance",
    "DecisionProvenance",
    
    # Ports
    "DefaultNetworkPortId",
    "DefaultNetworkPortKind",
    "DefaultNetworkPortDirection",
    "DefaultNetworkPortRegistry",
    
    # Contracts (inbound invocation)
    "DefaultNetworkInvocationPort",
    
    # Contracts (inbound projection)
    "InternalContextProjectionPort",
    "MemoryProjectionPort",
    "IdentityProjectionPort",
    "ObservationProjectionPort",
    "WorkspaceFeedbackProjectionPort",
    
    # Contracts (inbound result)
    "CapabilityResultPort",
    "AuthorityDecisionPort",
    
    # Contracts (outbound request)
    "ReflectionCapabilityRequestPort",
    "SimulationCapabilityRequestPort",
    "NarrativeCapabilityRequestPort",
    "MemoryProjectionRequestPort",
    "PredictiveCapabilityRequestPort",
    
    # Contracts (outbound proposal)
    "MemoryUpdateProposalPort",
    "IdentityRevisionProposalPort",
    "WorkspaceSubmissionProposalPort",
    "ExecutiveReviewProposalPort",
    "MonitoringProposalPort",
    "AttentionReviewProposalPort",
    
    # Semantics
    "IntegrationCorrelationChain",
    "IntegrationCausationChain",
    "IdempotencyKey",
    "OrderingSemantics",
    "DeliverySemantics",
    
    # Versioning
    "SchemaVersion",
    "ContractVersion",
    "EntityRevision",
    "StateRevision",
    "CompatibilityStatus",
    
    # Validation
    "ValidationResult",
    "ValidationFailureReason",
    "validate_envelope",
    
    # Exceptions
    "IntegrationError",
    "ContractValidationError",
    "SchemaVersionError",
    "CompatibilityError",
    "AuthorityError",
    "CorrelationError",
    
    # State and transitions
    "DefaultNetworkIntegrationState",
    "IntegrationTransition",
]

# =============================================================================
# DEPENDENCIES
# =============================================================================

DEPENDENCIES = [
    "gordon_system.src.agent.networks.default (Phase 4.3.12)",
    "gordon_system.src.agent.core.interfaces (Phase 3.8.12)",
]

# =============================================================================
# EXCLUSION CRITERIA
# =============================================================================

FORBIDDEN_IMPORTS = [
    "asyncio.create_task",
    "asyncio.run",
    "threading.Thread",
    "multiprocessing",
    "time.sleep",
    "datetime.now",
    "uuid.uuid4",
    "random",
    "socket",
    "subprocess",
    "requests",
    "httpx",
    "aiohttp",
]

# =============================================================================
# DOCUMENTATION URLS
# =============================================================================

DOCUMENTATION_URLS = {
    "readme": "../../../docs/agent/architecture/networks/default/integration/README.md",
    "port_taxonomy": "../../../docs/agent/architecture/networks/default/integration/port-taxonomy.md",
    "contract_types": "../../../docs/agent/architecture/networks/default/integration/contract-types.md",
}