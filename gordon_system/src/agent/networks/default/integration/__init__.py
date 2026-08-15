# Default Network Integration Contracts Package
# ===============================================

"""
Canonical DefaultNetwork Integration Contracts for Phase 4.3.13.

This package provides the complete integration contract layer for the Default Network,
establishing typed, directionally-correct, authority-safe boundaries between the
Default Network and all external systems.
"""

from __future__ import annotations

from .__meta__ import (
    VERSION,
    __version__,
)

# =============================================================================
# SUBMODULES (Phase 4.3.13)
# =============================================================================

from .direction import (
    PortDirection,
    INBOUND,
    OUTBOUND,
    BIDIRECTIONAL,
)

from .types import (
    IntegrationId,
    RequestId,
    ResultId,
    ProposalId,
    DecisionId,
    CorrelationId,
    CausationId,
    SemanticTime,
    SemanticTimeReference,
    AuthorityKind,
    AuthorityReference,
    FactualityClassification,
    PRIMITIVE_OBSERVED,
    RECORDED,
    REPORTED,
    INFERRED,
    INTERPRETED,
    PREDICTED,
    SIMULATED,
    COUNTERFACTUAL,
    HYPOTHETICAL,
    PROPOSED,
    DISPUTED,
    SUPERSEDED,
    RECONSTRUCTED,
    UNKNOWN_FACTUALITY,
    PrivacyClassification,
    PUBLIC_PRIVACY,
    INTERNAL_PRIVACY,
    INTERNAL_RESTRICTED_PRIVACY,
    PARTICIPANT_SCOPED_PRIVACY,
    USER_PRIVATE_PRIVACY,
    IDENTITY_SENSITIVE_PRIVACY,
    MEMORY_SENSITIVE_PRIVACY,
    SECURITY_SENSITIVE_PRIVACY,
    POLICY_SENSITIVE_PRIVACY,
    CONFIDENTIAL_PRIVACY,
    NON_DISCLOSABLE_PRIVACY,
    UNKNOWN_PRIVACY,
    DisclosureClassification,
    INTERNAL_PROCESSABLE,
    WORKSPACE_ADMISSIBLE,
    CONSUMER_ACCESSIBLE,
    EXTERNALLY_RENDERABLE,
    EXTERNALLY_DELIVERABLE,
)

from .correlation import (
    IntegrationCorrelationChain,
    IntegrationCausationChain,
)

__all__ = [
    # Metadata
    "VERSION",
    "__version__",
    
    # Direction
    "PortDirection",
    "INBOUND",
    "OUTBOUND",
    "BIDIRECTIONAL",
    
    # Types
    "IntegrationId",
    "RequestId",
    "ResultId",
    "ProposalId",
    "DecisionId",
    "CorrelationId",
    "CausationId",
    "SemanticTime",
    "SemanticTimeReference",
    "AuthorityKind",
    "AuthorityReference",
    "FactualityClassification",
    "PRIMITIVE_OBSERVED",
    "RECORDED",
    "REPORTED",
    "INFERRED",
    "INTERPRETED",
    "PREDICTED",
    "SIMULATED",
    "COUNTERFACTUAL",
    "HYPOTHETICAL",
    "PROPOSED",
    "DISPUTED",
    "SUPERSEDED",
    "RECONSTRUCTED",
    "UNKNOWN_FACTUALITY",
    "PrivacyClassification",
    "PUBLIC_PRIVACY",
    "INTERNAL_PRIVACY",
    "INTERNAL_RESTRICTED_PRIVACY",
    "PARTICIPANT_SCOPED_PRIVACY",
    "USER_PRIVATE_PRIVACY",
    "IDENTITY_SENSITIVE_PRIVACY",
    "MEMORY_SENSITIVE_PRIVACY",
    "SECURITY_SENSITIVE_PRIVACY",
    "POLICY_SENSITIVE_PRIVACY",
    "CONFIDENTIAL_PRIVACY",
    "NON_DISCLOSABLE_PRIVACY",
    "UNKNOWN_PRIVACY",
    "DisclosureClassification",
    "INTERNAL_PROCESSABLE",
    "WORKSPACE_ADMISSIBLE",
    "CONSUMER_ACCESSIBLE",
    "EXTERNALLY_RENDERABLE",
    "EXTERNALLY_DELIVERABLE",
    
    # Correlation and Causation
    "IntegrationCorrelationChain",
    "IntegrationCausationChain",
]