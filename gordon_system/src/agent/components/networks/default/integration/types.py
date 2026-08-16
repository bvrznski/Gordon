# Default Network Integration Types (Phase 4.3.13)
# =================================================

"""
Type definitions for integration contracts.

All types are immutable and designed to be used in dataclass fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NewType, Literal, Union


# =============================================================================
# IDENTITY TYPES (Phase 4.3.13)
# =============================================================================

IntegrationId = NewType("IntegrationId", str)
"""Stable identifier for integration operations."""

RequestId = NewType("RequestId", str)
"""Identifier for an integration request instance."""

ResultId = NewType("ResultId", str)
"""Identifier for a result instance."""

ProposalId = NewType("ProposalId", str)
"""Identifier for a proposal instance."""

DecisionId = NewType("DecisionId", str)
"""Identifier for an authority decision instance."""


# =============================================================================
# CORRELATION AND CAUSATION (Phase 4.3.13)
# =============================================================================

CorrelationId = NewType("CorrelationId", str)
"""
Identifier for distributed tracing correlation.
Groups semantically related operations across system boundaries.
"""

CausationId = Union[None, str]
"""
Identifier for causation chain (optional).
Identifies the direct semantic predecessor.
"""


# =============================================================================
# SEMANTIC TIME (Phase 4.3.13)
# =============================================================================

from datetime import datetime

SemanticTime = datetime
"""Canonical time reference for semantic operations."""

SemanticTimeReference = NewType("SemanticTimeReference", str)
"""
Stable reference to a SemanticTime without embedding the full timestamp.
Used for replay and checkpointing.
"""


# =============================================================================
# AUTHORITY KINDS (Phase 4.3.13)
# =============================================================================

class AuthorityKind:
    """Authority classification enum."""
    
    DEFAULT_NETWORK = "DEFAULT_NETWORK"
    EXECUTION = "EXECUTION"
    CORE_RUNTIME = "CORE_RUNTIME"
    MEMORY = "MEMORY"
    IDENTITY = "IDENTITY"
    NARRATIVE = "NARRATIVE"
    PREDICTIVE = "PREDICTIVE"
    WORKSPACE = "WORKSPACE"
    EXECUTIVE = "EXECUTIVE"
    ATTENTION = "ATTENTION"
    SECURITY = "SECURITY"
    POLICY = "POLICY"
    USER = "USER"
    DEVELOPER = "DEVELOPER"
    EXTERNAL_SYSTEM = "EXTERNAL_SYSTEM"
    NONE = "NONE"


# =============================================================================
# AUTHORITY REFERENCE (Phase 4.3.13)
# =============================================================================

@dataclass(frozen=True, slots=True)
class AuthorityReference:
    """
    Immutable reference to an authority without embedding live objects.
    
    Used for traceability and validation - no runtime access.
    """
    
    kind: str  # AuthorityKind.*
    """The kind of authority."""
    
    owner_id: str
    """Stable identifier for the owner."""
    
    scope: str = "default"
    """Authority scope (e.g., 'user-123', 'system-wide')."""
    
    revision: int = 0
    """Authority configuration revision at time of reference."""
    
    decision_scope: str = "read"
    """Scope of decisions this reference can make."""
    
    @classmethod
    def new(
        cls,
        kind: str,
        owner_id: str,
        scope: str = "default",
        revision: int = 0,
        decision_scope: str = "read",
    ) -> AuthorityReference:
        """Create a new authority reference."""
        return cls(
            kind=kind,
            owner_id=owner_id,
            scope=scope,
            revision=revision,
            decision_scope=decision_scope,
        )


# =============================================================================
# FACTUALITY CLASSIFICATIONS (Phase 4.3.13)
# =============================================================================

class FactualityClassification:
    """Factuality classification enum."""
    
    PRIMITIVE_OBSERVED = "OBSERVED"
    RECORDED = "RECORDED"
    REPORTED = "REPORTED"
    INFERRED = "INFERRED"
    INTERPRETED = "INTERPRETED"
    PREDICTED = "PREDICTED"
    SIMULATED = "SIMULATED"
    COUNTERFACTUAL = "COUNTERFACTUAL"
    HYPOTHETICAL = "HYPOTHETICAL"
    PROPOSED = "PROPOSED"
    DISPUTED = "DISPUTED"
    SUPERSEDED = "SUPERSEDED"
    RECONSTRUCTED = "RECONSTRUCTED"
    UNKNOWN_FACTUALITY = "UNKNOWN"


PRIMITIVE_OBSERVED = FactualityClassification.PRIMITIVE_OBSERVED
RECORDED = FactualityClassification.RECORDED
REPORTED = FactualityClassification.REPORTED
INFERRED = FactualityClassification.INFERRED
INTERPRETED = FactualityClassification.INTERPRETED
PREDICTED = FactualityClassification.PREDICTED
SIMULATED = FactualityClassification.SIMULATED
COUNTERFACTUAL = FactualityClassification.COUNTERFACTUAL
HYPOTHETICAL = FactualityClassification.HYPOTHETICAL
PROPOSED = FactualityClassification.PROPOSED
DISPUTED = FactualityClassification.DISPUTED
SUPERSEDED = FactualityClassification.SUPERSEDED
RECONSTRUCTED = FactualityClassification.RECONSTRUCTED
UNKNOWN_FACTUALITY = FactualityClassification.UNKNOWN_FACTUALITY


# =============================================================================
# PRIVACY CLASSIFICATIONS (Phase 4.3.13)
# =============================================================================

class PrivacyClassification:
    """Privacy classification enum."""
    
    PUBLIC_PRIVACY = "PUBLIC"
    INTERNAL_PRIVACY = "INTERNAL"
    INTERNAL_RESTRICTED_PRIVACY = "INTERNAL_RESTRICTED"
    PARTICIPANT_SCOPED_PRIVACY = "PARTICIPANT_SCOPED"
    USER_PRIVATE_PRIVACY = "USER_PRIVATE"
    IDENTITY_SENSITIVE_PRIVACY = "IDENTITY_SENSITIVE"
    MEMORY_SENSITIVE_PRIVACY = "MEMORY_SENSITIVE"
    SECURITY_SENSITIVE_PRIVACY = "SECURITY_SENSITIVE"
    POLICY_SENSITIVE_PRIVACY = "POLICY_SENSITIVE"
    CONFIDENTIAL_PRIVACY = "CONFIDENTIAL"
    NON_DISCLOSABLE_PRIVACY = "NON_DISCLOSABLE"
    UNKNOWN_PRIVACY = "UNKNOWN"


PUBLIC_PRIVACY = PrivacyClassification.PUBLIC_PRIVACY
INTERNAL_PRIVACY = PrivacyClassification.INTERNAL_PRIVACY
INTERNAL_RESTRICTED_PRIVACY = PrivacyClassification.INTERNAL_RESTRICTED_PRIVACY
PARTICIPANT_SCOPED_PRIVACY = PrivacyClassification.PARTICIPANT_SCOPED_PRIVACY
USER_PRIVATE_PRIVACY = PrivacyClassification.USER_PRIVATE_PRIVACY
IDENTITY_SENSITIVE_PRIVACY = PrivacyClassification.IDENTITY_SENSITIVE_PRIVACY
MEMORY_SENSITIVE_PRIVACY = PrivacyClassification.MEMORY_SENSITIVE_PRIVACY
SECURITY_SENSITIVE_PRIVACY = PrivacyClassification.SECURITY_SENSITIVE_PRIVACY
POLICY_SENSITIVE_PRIVACY = PrivacyClassification.POLICY_SENSITIVE_PRIVACY
CONFIDENTIAL_PRIVACY = PrivacyClassification.CONFIDENTIAL_PRIVACY
NON_DISCLOSABLE_PRIVACY = PrivacyClassification.NON_DISCLOSABLE_PRIVACY
UNKNOWN_PRIVACY = PrivacyClassification.UNKNOWN_PRIVACY


# =============================================================================
# DISCLOSURE CLASSIFICATIONS (Phase 4.3.13)
# =============================================================================

class DisclosureClassification:
    """Disclosure classification enum."""
    
    INTERNAL_PROCESSABLE = "INTERNAL_PROCESSABLE"
    WORKSPACE_ADMISSIBLE = "WORKSPACE_ADMISSIBLE"
    CONSUMER_ACCESSIBLE = "CONSUMER_ACCESSIBLE"
    EXTERNALLY_RENDERABLE = "EXTERNALLY_RENDERABLE"
    EXTERNALLY_DELIVERABLE = "EXTERNALLY_DELIVERABLE"


INTERNAL_PROCESSABLE = DisclosureClassification.INTERNAL_PROCESSABLE
WORKSPACE_ADMISSIBLE = DisclosureClassification.WORKSPACE_ADMISSIBLE
CONSUMER_ACCESSIBLE = DisclosureClassification.CONSUMER_ACCESSIBLE
EXTERNALLY_RENDERABLE = DisclosureClassification.EXTERNALLY_RENDERABLE
EXTERNALLY_DELIVERABLE = DisclosureClassification.EXTERNALLY_DELIVERABLE


# =============================================================================
# CONTRACT KIND ENUM (Phase 4.3.13)
# =============================================================================

class ContractKind:
    """Contract kind enum."""
    
    # Inbound invocation
    DEFAULT_NETWORK_INVOCATION = "DEFAULT_NETWORK_INVOCATION"
    
    # Inbound projections
    INTERNAL_CONTEXT_PROJECTION = "INTERNAL_CONTEXT_PROJECTION"
    MEMORY_PROJECTION = "MEMORY_PROJECTION"
    IDENTITY_PROJECTION = "IDENTITY_PROJECTION"
    OBSERVATION_PROJECTION = "OBSERVATION_PROJECTION"
    WORKSPACE_FEEDBACK_PROJECTION = "WORKSPACE_FEEDBACK_PROJECTION"
    
    # Inbound results
    CAPABILITY_RESULT = "CAPABILITY_RESULT"
    AUTHORITY_DECISION = "AUTHORITY_DECISION"
    
    # Outbound requests
    REFLECTION_CAPABILITY_REQUEST = "REFLECTION_CAPABILITY_REQUEST"
    SIMULATION_CAPABILITY_REQUEST = "SIMULATION_CAPABILITY_REQUEST"
    NARRATIVE_CAPABILITY_REQUEST = "NARRATIVE_CAPABILITY_REQUEST"
    MEMORY_PROJECTION_REQUEST = "MEMORY_PROJECTION_REQUEST"
    PREDICTIVE_CAPABILITY_REQUEST = "PREDICTIVE_CAPABILITY_REQUEST"
    
    # Outbound proposals
    MEMORY_UPDATE_PROPOSAL = "MEMORY_UPDATE_PROPOSAL"
    IDENTITY_REVISION_PROPOSAL = "IDENTITY_REVISION_PROPOSAL"
    WORKSPACE_SUBMISSION_PROPOSAL = "WORKSPACE_SUBMISSION_PROPOSAL"
    EXECUTIVE_REVIEW_PROPOSAL = "EXECUTIVE_REVIEW_PROPOSAL"
    MONITORING_PROPOSAL = "MONITORING_PROPOSAL"
    ATTENTION_REVIEW_PROPOSAL = "ATTENTION_REVIEW_PROPOSAL"


__all__ = [
    # Identity types
    "IntegrationId",
    "RequestId",
    "ResultId",
    "ProposalId",
    "DecisionId",
    
    # Correlation and causation
    "CorrelationId",
    "CausationId",
    
    # Time
    "SemanticTime",
    "SemanticTimeReference",
    
    # Authority
    "AuthorityKind",
    "AuthorityReference",
    
    # Factuality
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
    
    # Privacy
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
    
    # Disclosure
    "DisclosureClassification",
    "INTERNAL_PROCESSABLE",
    "WORKSPACE_ADMISSIBLE",
    "CONSUMER_ACCESSIBLE",
    "EXTERNALLY_RENDERABLE",
    "EXTERNALLY_DELIVERABLE",
    
    # Contract kinds
    "ContractKind",
]