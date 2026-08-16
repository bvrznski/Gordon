# Gordon Cognitive Architecture - Phase 4.11.5
# ===========================================

"""
Cognitive Coordination Protocol (CCP) Core Models
=================================================

This module defines the canonical immutable data models for CCP:
- Message identity and revision management
- Publisher and consumer references
- Message envelope structure
- Publication, subscription, and acknowledgement contracts

All models are deeply frozen to ensure deterministic behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


# =============================================================================
# CCP PROTOCOL IDENTITY - Immutable protocol specification identity
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPProtocolIdentity:
    """
    Immutable semantic identity for a CCP specification.
    
    PROTOCOL-LAW-001: Protocol has one stable semantic identity
    PROTOCOL-LAW-002: Identity is independent from protocol revisions
    PROTOCOL-LAW-003: Identity preserves schema version
    PROTOCOL-LAW-004: Identity preserves compatibility profile
    """
    semantic_name: str = "CognitiveCoordinationProtocol"
    """Canonical semantic name."""
    
    protocol_family: str = "gordon_ccp"
    """Protocol family identifier."""
    
    major_version: int = 1
    """Major version number (incompatible changes)."""
    
    minor_version: int = 0
    """Minor version number (backward-compatible additions)."""
    
    schema_revision: int = 1
    """Schema revision for serialization evolution."""
    
    compatibility_profile: str = "strict"
    """Compatibility profile (strict, flexible, etc.)."""
    
    provenance: str = "gordon_cognitive_architecture"
    """Source of this protocol specification."""
    
    @property
    def version_string(self) -> str:
        """Return full version string."""
        return f"{self.major_version}.{self.minor_version}"
    
    @classmethod
    def v1_0(cls) -> CCPProtocolIdentity:
        """Return CCP v1.0 identity."""
        return cls(
            semantic_name="CognitiveCoordinationProtocol",
            protocol_family="gordon_ccp",
            major_version=1,
            minor_version=0,
            schema_revision=1,
            compatibility_profile="strict",
            provenance="gordon_cognitive_architecture",
        )


# =============================================================================
# CCP VERSION - Protocol version model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPVersion:
    """
    Immutable protocol version model.
    
    VERSION-LAW-001: Every published protocol declares its version explicitly
    VERSION-LAW-002: Major versions represent incompatible changes
    VERSION-LAW-003: Minor versions are backward compatible
    VERSION-LAW-004: Patch revisions do not change semantics
    """
    major: int = 1
    """Major version (incompatible changes)."""
    
    minor: int = 0
    """Minor version (backward-compatible additions)."""
    
    patch: int = 0
    """Patch revision (compatible corrections)."""
    
    schema_revision: int = 1
    """Schema evolution revision."""
    
    feature_set: tuple[str, ...] = field(default_factory=tuple)
    """Supported features in this version."""
    
    deprecated_features: tuple[str, ...] = field(default_factory=tuple)
    """Deprecated features still supported."""
    
    compatibility_range: str = "strict"
    """Compatibility policy range."""
    
    provenance: str = ""
    """Version provenance reference."""
    
    @property
    def full_version(self) -> str:
        """Return full version string (major.minor.patch)."""
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @classmethod
    def v1_0_0(cls) -> CCPVersion:
        """Return CCP v1.0.0."""
        return cls(
            major=1,
            minor=0,
            patch=0,
            schema_revision=1,
            feature_set=("all",),
            compatibility_range="strict",
        )


# =============================================================================
# CCP MESSAGE ENVELOPE - The canonical immutable message envelope
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPMessage:
    """
    Immutable envelope for all CCP messages.
    
    ENVELOPE-LAW-001: All common metadata belongs to the envelope
    ENVELOPE-LAW-002: Payload-specific semantics belong to payload contracts
    ENVELOPE-LAW-003: Envelope metadata is immutable
    ENVELOPE-LAW-004: Envelope revisions preserve lineage
    ENVELOPE-LAW-005: Correlation remains explicit
    ENVELOPE-LAW-006: Causation remains explicit
    ENVELOPE-LAW-007: Visibility remains explicit
    """
    # Identity fields
    identity: str = ""
    """Unique semantic identity derived from content."""
    
    message_kind: str = ""  # CCPMessageKind value as string
    """Canonical kind of this message."""
    
    payload_kind: str = ""  # CCPPayloadKind value as string
    """Semantic payload kind."""
    
    publisher: str = ""
    """Publisher network identity reference."""
    
    # Version and protocol fields
    protocol_version: str = "1.0.0"
    """Protocol version this message conforms to."""
    
    revision: int = 1
    """Message revision number."""
    
    # Timing and ordering
    semantic_time: Optional[str] = None
    """Semantic time reference (not wall-clock)."""
    
    creation_epoch: str = ""
    """Epoch identity when created."""
    
    cycle_identity: str = ""
    """Coordination cycle identity."""
    
    # Correlation fields
    correlation_id: str = ""
    """Correlation identity for related messages."""
    
    causation_id: Optional[str] = None
    """Explicit causation source reference."""
    
    # Payload reference (payload itself is external)
    payload_reference: str = ""
    """Reference to semantic payload (not embedded)."""
    
    payload_revision: int = 1
    """Payload revision number."""
    
    message_revision: int = 1
    """Message revision in lineage."""
    
    # Publication state
    publication_intention: str = "publish"
    """Intended publication status (from CCPPublicationStatus)."""
    
    visibility: str = ""  # CCPMessageVisibility value as string
    """Semantic visibility scope."""
    
    # Quality fields
    confidence: float = 0.5
    """Confidence in message accuracy (0.0 to 1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about the message content."""
    
    provenance: str = ""
    """Provenance reference for this message."""
    
    @property
    def is_revision(self) -> bool:
        """Check if this is a revision (not initial)."""
        return self.revision > 1
    
    @property
    def is_initial(self) -> bool:
        """Check if this is the initial version."""
        return self.revision == 1


# =============================================================================
# CCP PUBLISHER REFERENCE - Publisher authority and capabilities
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPPublisherReference:
    """
    Immutable publisher model with authority and capabilities.
    
    PUBLISHER-LAW-001: Every message has exactly one publisher
    PUBLISHER-LAW-002: Publishers declare supported protocol versions
    PUBLISHER-LAW-003: Publishers publish only authorized artifacts
    PUBLISHER-LAW-004: Publisher authority is explicit
    """
    network_identity: str = ""
    """Canonical network identity."""
    
    network_kind: str = ""  # CoordinatedNetworkKind value
    """Network kind (e.g., reward, prediction)."""
    
    protocol_version: str = "1.0.0"
    """Supported protocol version."""
    
    projection_contract_version: str = "1.0.0"
    """Projection contract version supported."""
    
    authority_scope: str = "peer"
    """Authority scope (peer, supervisor, etc.)."""
    
    advertised_capabilities: tuple[str, ...] = field(default_factory=tuple)
    """Capabilities this publisher can advertise."""
    
    provenance: str = ""
    """Publisher reference provenance."""
    
    @classmethod
    def for_network(cls, network_id: str, kind: str) -> CCPPublisherReference:
        """Create a basic publisher reference for a network."""
        return cls(
            network_identity=network_id,
            network_kind=kind,
            protocol_version="1.0.0",
            projection_contract_version="1.0.0",
            authority_scope="peer",
            provenance=f"network:{kind}:{network_id}",
        )


# =============================================================================
# CCP CONSUMER REFERENCE - Consumer subscriptions and compatibility
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPConsumerReference:
    """
    Immutable consumer model with subscriptions.
    
    CONSUMER-LAW-001: Consumers declare supported protocol versions
    CONSUMER-LAW-002: Consumers declare accepted payload contracts
    CONSUMER-LAW-003: Consumers declare subscription profiles
    CONSUMER-LAW-004: Consumer authority is explicit
    """
    network_identity: str = ""
    """Consumer network identity."""
    
    network_kind: str = ""  # CoordinatedNetworkKind value
    """Network kind."""
    
    supported_protocol_versions: tuple[str, ...] = field(default_factory=tuple)
    """Supported CCP protocol versions."""
    
    subscription_profile_reference: Optional[str] = None
    """Reference to subscription profile."""
    
    accepted_payload_contracts: tuple[str, ...] = field(default_factory=tuple)
    """Accepted payload contract kinds."""
    
    authority_scope: str = "peer"
    """Authority scope."""
    
    provenance: str = ""
    """Consumer reference provenance."""
    
    @classmethod
    def for_network(cls, network_id: str, kind: str) -> CCPConsumerReference:
        """Create a basic consumer reference for a network."""
        return cls(
            network_identity=network_id,
            network_kind=kind,
            supported_protocol_versions=("1.0.0",),
            accepted_payload_contracts=(
                "network_projection",
                "coordination_state",
                "capability_advertisement",
            ),
            authority_scope="peer",
            provenance=f"consumer:{kind}:{network_id}",
        )


# =============================================================================
# CCP VISIBILITY - Message visibility scope model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPMessageVisibility:
    """
    Immutable visibility scope configuration.
    
    VISIBILITY-LAW-001: Visibility controls semantic eligibility
    VISIBILITY-LAW-002: Visibility does not implement access control
    """
    visibility_scope: str = ""  # CCPMessageVisibility value
    """Semantic visibility scope."""
    
    target_networks: tuple[str, ...] = field(default_factory=tuple)
    """Target networks for TARGETED_NETWORKS visibility."""
    
    domain_scoped_to: Optional[str] = None
    """Domain scope identifier if domain_scoped."""
    
    can_be_observed: bool = False
    """Whether observers can receive this message."""
    
    is_archival: bool = False
    """Whether message is for archival purposes only."""
    
    provenance: str = ""
    """Visibility configuration provenance."""


# =============================================================================
# CCP PUBLICATION - Publication contract record
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPPublication:
    """
    Immutable publication record.
    
    PUBLICATION-LAW-001: Publication makes semantic information available
    PUBLICATION-LAW-002: Publication does not imply acceptance
    PUBLICATION-LAW-003: Publications are immutable
    PUBLICATION-LAW-004: Publication revisions preserve lineage
    """
    identity: str = ""
    """Unique publication identity."""
    
    message: Optional[CCPMessage] = None  # CCPMessage type reference
    """The message being published (or reference)."""
    
    publisher_reference: Optional[CCPPublisherReference] = None
    """Publisher authority reference."""
    
    publication_status: str = ""  # CCPPublicationStatus value
    """Publication status."""
    
    intended_visibility: Optional[CCPMessageVisibility] = None
    """Intended visibility scope."""
    
    eligible_consumers: tuple[str, ...] = field(default_factory=tuple)
    """Consumers eligible to receive this publication."""
    
    publication_revision: int = 1
    """Publication revision number."""
    
    replaces_publication_reference: Optional[str] = None
    """Reference to replaced publication (if any)."""
    
    publication_findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during publication processing."""
    
    publication_limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this publication."""
    
    semantic_time: Optional[str] = None
    """Semantic time of publication."""
    
    provenance: str = ""
    """Publication provenance reference."""
    
    @classmethod
    def create_initial(
        cls,
        message: CCPMessage,
        publisher: CCPPublisherReference,
        visibility: CCPMessageVisibility,
    ) -> CCPPublication:
        """Create an initial (new) publication."""
        return cls(
            identity=f"pub:{message.identity}",
            message=message,
            publisher_reference=publisher,
            publication_status="created",
            intended_visibility=visibility,
            eligible_consumers=(),
            publication_revision=1,
            semantic_time=message.semantic_time,
            provenance=f"publication:{message.identity}",
        )


# =============================================================================
# CCP SUBSCRIPTION - Subscription contract model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPSubscription:
    """
    Immutable subscription model.
    
    SUBSCRIPTION-LAW-001: Subscriptions remain declarative
    SUBSCRIPTION-LAW-002: Subscriptions do not contain executable predicates
    SUBSCRIPTION-LAW-003: Subscription filters are explicit
    SUBSCRIPTION-LAW-004: Subscription revisions preserve lineage
    """
    identity: str = ""
    """Unique subscription identity."""
    
    subscriber_reference: Optional[CCPConsumerReference] = None
    """Subscriber reference."""
    
    subscribed_message_kinds: tuple[str, ...] = field(default_factory=tuple)
    """Message kinds this subscription matches."""
    
    subscribed_payload_kinds: tuple[str, ...] = field(default_factory=tuple)
    """Payload kinds this subscription matches."""
    
    publisher_constraints: tuple[str, ...] = field(default_factory=tuple)
    """Constraints on matching publishers."""
    
    domain_scope: Optional[str] = None
    """Coordination domain scope."""
    
    epoch_scope: Optional[str] = None
    """Epoch identity scope."""
    
    cycle_scope: Optional[str] = None
    """Cycle identity scope."""
    
    semantic_filters: tuple[str, ...] = field(default_factory=tuple)
    """Semantic filter expressions."""
    
    accepted_versions: tuple[str, ...] = field(default_factory=tuple)
    """Accepted protocol versions."""
    
    minimum_confidence: float = 0.5
    """Minimum confidence threshold."""
    
    accepted_uncertainty: float = 0.5
    """Maximum accepted uncertainty."""
    
    accepted_limitations: tuple[str, ...] = field(default_factory=tuple)
    """Accepted limitation kinds."""
    
    visibility_requirements: Optional[CCPMessageVisibility] = None
    """Required visibility for matches."""
    
    policy_reference: Optional[str] = None
    """Policy reference for this subscription."""
    
    provenance: str = ""
    """Subscription provenance."""
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active (not withdrawn)."""
        # In this model, subscriptions are immutable; they're "withdrawn" by
        # creating a new revision with withdrawal status in external state.
        return True
    
    @classmethod
    def for_consumer(
        cls,
        consumer: CCPConsumerReference,
        kinds: tuple[str, ...],
        payloads: tuple[str, ...] = (),
    ) -> CCPSubscription:
        """Create a subscription for a consumer."""
        return cls(
            identity=f"sub:{consumer.network_identity}",
            subscriber_reference=consumer,
            subscribed_message_kinds=kinds,
            subscribed_payload_kinds=payloads if payloads else kinds,
            minimum_confidence=0.5,
            accepted_uncertainty=0.5,
            provenance=f"subscription:{consumer.network_identity}",
        )


# =============================================================================
# CCP ACKNOWLEDGEMENT - Acknowledgement contract model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPAcknowledgement:
    """
    Immutable acknowledgement model.
    
    ACK-LAW-001: Acknowledgement is distinct from acceptance
    ACK-LAW-002: Acknowledgement preserves consumer identity
    ACK-LAW-003: Acknowledgement preserves publication reference
    ACK-LAW-004: Acknowledgement revisions preserve lineage
    """
    identity: str = ""
    """Unique acknowledgement identity."""
    
    acknowledging_consumer: Optional[CCPConsumerReference] = None
    """Consumer making the acknowledgement."""
    
    publication_reference: Optional[str] = None
    """Reference to published message."""
    
    message_reference: Optional[str] = None
    """Reference to acknowledged message."""
    
    acknowledgement_kind: str = ""  # CCPAcknowledgementKind value
    """Kind of acknowledgement."""
    
    acknowledgement_status: str = ""  # CCPMessageAcceptanceStatus value
    """Semantic status of this acknowledgement."""
    
    consumer_cycle_reference: Optional[str] = None
    """Consumer cycle reference at time of acknowledgement."""
    
    acknowledgement_findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during acknowledgement processing."""
    
    confidence: float = 0.5
    """Confidence in this acknowledgement."""
    
    uncertainty: float = 0.5
    """Uncertainty about this acknowledgement."""
    
    semantic_time: Optional[str] = None
    """Semantic time of acknowledgement."""
    
    provenance: str = ""
    """Acknowledgement provenance."""
    
    @classmethod
    def for_received(
        cls,
        publication_ref: str,
        consumer: CCPConsumerReference,
    ) -> CCPAcknowledgement:
        """Create a 'received' acknowledgement."""
        return cls(
            identity=f"ack:{publication_ref}:{consumer.network_identity}",
            acknowledging_consumer=consumer,
            publication_reference=publication_ref,
            message_reference=publication_ref,
            acknowledgement_kind="received",
            acknowledgement_status="accepted",
            confidence=1.0,
            uncertainty=0.0,
            provenance=f"acknowledgement:{publication_ref}",
        )


# =============================================================================
# CCP MESSAGE ACCEPTANCE - Semantic acceptance record
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPMessageAcceptance:
    """
    Immutable semantic acceptance record.
    
    ACCEPTANCE-LAW-001: Acceptance represents semantic incorporation
    ACCEPTANCE-LAW-002: Rejection preserves explicit reasons
    ACCEPTANCE-LAW-003: Deferral is distinct from rejection
    ACCEPTANCE-LAW-004: Conditional acceptance is explicit
    """
    publication_reference: Optional[str] = None
    """Reference to accepted publication."""
    
    consumer: Optional[CCPConsumerReference] = None
    """Consumer accepting the message."""
    
    status: str = ""  # CCPMessageAcceptanceStatus value
    """Acceptance status."""
    
    accepted_payload_reference: Optional[str] = None
    """Reference to accepted payload (may differ from original)."""
    
    consumer_context_revision: Optional[str] = None
    """Consumer context revision at acceptance time."""
    
    compatibility: str = ""  # CCPCompatibilityStatus value
    """Compatibility status at acceptance."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this acceptance."""
    
    confidence: float = 0.5
    """Confidence in acceptance correctness."""
    
    uncertainty: float = 0.5
    """Uncertainty about acceptance correctness."""
    
    provenance: str = ""
    """Acceptance provenance."""
    
    @classmethod
    def accepted(
        cls,
        publication_ref: str,
        consumer: CCPConsumerReference,
    ) -> CCPMessageAcceptance:
        """Create an accepted record."""
        return cls(
            publication_reference=publication_ref,
            consumer=consumer,
            status="accepted",
            compatibility="fully_compatible",
            confidence=1.0,
            uncertainty=0.0,
            provenance=f"acceptance:{publication_ref}",
        )
    
    @classmethod
    def rejected(
        cls,
        publication_ref: str,
        consumer: CCPConsumerReference,
        reasons: tuple[str, ...],
    ) -> CCPMessageAcceptance:
        """Create a rejection record."""
        return cls(
            publication_reference=publication_ref,
            consumer=consumer,
            status="rejected",
            compatibility="incompatible",
            limitations=reasons,
            confidence=0.5,
            uncertainty=0.5,
            provenance=f"rejection:{publication_ref}",
        )
    
    @classmethod
    def deferred(
        cls,
        publication_ref: str,
        consumer: CCPConsumerReference,
        resume_condition: Optional[str] = None,
    ) -> CCPMessageAcceptance:
        """Create a deferred record."""
        return cls(
            publication_reference=publication_ref,
            consumer=consumer,
            status="deferred",
            compatibility="compatible_with_adapter",
            limitations=(resume_condition,) if resume_condition else (),
            confidence=0.5,
            uncertainty=0.5,
            provenance=f"deferral:{publication_ref}",
        )


# =============================================================================
# CCP REJECTION - Rejection record with reasons
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPMessageRejection:
    """
    Immutable rejection model with explicit reasons.
    
    REJECTION-LAW-001: Rejection preserves explicit reasons
    REJECTION-LAW-002: Rejected messages have recoverability info
    """
    publication_reference: Optional[str] = None
    """Reference to rejected publication."""
    
    rejecting_consumer: Optional[CCPConsumerReference] = None
    """Consumer rejecting the message."""
    
    rejection_kind: str = ""  # CCPRejectionKind value
    """Kind of rejection with explicit reason."""
    
    reasons: tuple[str, ...] = field(default_factory=tuple)
    """Explicit rejection reasons."""
    
    recovery_authority: Optional[str] = None
    """Authority that can recover this rejection."""
    
    recoverability: str = "unknown"
    """Whether this rejection is recoverable."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during rejection processing."""
    
    provenance: str = ""
    """Rejection provenance."""


# =============================================================================
# CCP DEFERRAL - Deferral record with resume conditions
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPMessageDeferral:
    """
    Immutable deferral model.
    
    DEFERRAL-LAW-001: Deferral is distinct from rejection
    DEFERRAL-LAW-002: Missing requirements are explicit
    DEFERRAL-LAW-003: Resume conditions are explicit
    """
    publication_reference: Optional[str] = None
    """Reference to deferred publication."""
    
    deferring_consumer: Optional[CCPConsumerReference] = None
    """Consumer deferring acceptance."""
    
    deferral_reason: str = ""  # CCPDeferralReason value
    """Reason for deferral."""
    
    missing_requirements: tuple[str, ...] = field(default_factory=tuple)
    """Missing requirements blocking acceptance."""
    
    blocking_dependencies: tuple[str, ...] = field(default_factory=tuple)
    """Blocking dependencies."""
    
    resume_condition: Optional[str] = None
    """Condition under which deferral may be resumed."""
    
    semantic_deadline: Optional[str] = None
    """Semantic deadline for this deferral."""
    
    provenance: str = ""
    """Deferral provenance."""


# =============================================================================
# CCP CAPABILITY ADVERTISEMENT - Capability declaration
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPCapabilityAdvertisement:
    """
    Immutable capability advertisement model.
    
    CAPABILITY-LAW-001: Capability advertisement is declarative
    CAPABILITY-LAW-002: Capabilities preserve semantic scope
    CAPABILITY-LAW-003: Activation conditions are explicit
    """
    capability: str = ""
    """Capability identifier."""
    
    provider_network: Optional[str] = None
    """Provider network identity."""
    
    contract_version: str = "1.0.0"
    """Contract version for this capability."""
    
    semantic_scope: Optional[str] = None
    """Semantic scope of this capability."""
    
    availability_declaration: str = "available"
    """Availability state declaration."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this capability."""
    
    activation_conditions: tuple[str, ...] = field(default_factory=tuple)
    """Conditions for activation."""
    
    deprecation_state: str = "active"
    """Deprecation state of this capability."""
    
    provenance: str = ""
    """Advertisement provenance."""


# =============================================================================
# CCP REQUIREMENT DECLARATION - Requirement declaration
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPRequirementDeclaration:
    """
    Immutable requirement declaration model.
    
    REQUIREMENT-LAW-001: Requirement declaration is declarative
    REQUIREMENT-LAW-002: Requirements preserve requesting network identity
    REQUIREMENT-LAW-003: Required capabilities are explicit
    """
    requirement: str = ""
    """Requirement identifier."""
    
    requesting_network: Optional[str] = None
    """Requesting network identity."""
    
    required_capability: Optional[str] = None
    """Required capability identifier."""
    
    provider_constraints: tuple[str, ...] = field(default_factory=tuple)
    """Constraints on acceptable providers."""
    
    strength: str = "required"
    """Requirement strength (required, optional, preferred)."""
    
    activation_condition: Optional[str] = None
    """Activation condition for this requirement."""
    
    semantic_deadline: Optional[str] = None
    """Semantic deadline for satisfaction."""
    
    accepted_limitations: tuple[str, ...] = field(default_factory=tuple)
    """Accepted limitations on this requirement."""
    
    provenance: str = ""
    """Requirement declaration provenance."""


# =============================================================================
# CCP NEGOTIATION REQUEST - Negotiation request model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPNegotiationRequest:
    """
    Immutable negotiation request model.
    
    NEGOTIATION-LAW-001: Negotiation is declarative
    NEGOTIATION-LAW-002: Every provider response is preserved
    NEGOTIATION-LAW-003: Rejected providers are explicit
    """
    negotiation_identity: str = ""
    """Unique negotiation identity."""
    
    requesting_network: Optional[str] = None
    """Network making the request."""
    
    requirement_reference: Optional[str] = None
    """Reference to required capability."""
    
    candidate_provider_constraints: tuple[str, ...] = field(default_factory=tuple)
    """Constraints on candidate providers."""
    
    requested_capability: Optional[str] = None
    """Requested capability identifier."""
    
    required_contract_version: str = "1.0.0"
    """Required contract version for providers."""
    
    semantic_scope: Optional[str] = None
    """Semantic scope of this negotiation."""
    
    accepted_limitations: tuple[str, ...] = field(default_factory=tuple)
    """Accepted limitations on this requirement."""
    
    semantic_deadline: Optional[str] = None
    """Deadline for completing negotiation."""
    
    provenance: str = ""
    """Negotiation request provenance."""


# =============================================================================
# CCP NEGOTIATION RESPONSE - Provider response to negotiation
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPNegotiationResponse:
    """
    Immutable provider response model.
    
    NEGOTIATION-LAW-001: Negotiation is declarative
    NEGOTIATION-LAW-002: Every provider response is preserved
    """
    negotiation_identity: str = ""
    """Associated negotiation identity."""
    
    responding_provider: Optional[str] = None
    """Provider network identity."""
    
    offered_capability_reference: Optional[str] = None
    """Offered capability reference."""
    
    compatibility: str = ""  # CCPCompatibilityStatus value
    """Compatibility with requirement."""
    
    availability: str = "unknown"
    """Availability state of provider."""
    
    readiness: str = "unknown"
    """Readiness to provide capability."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this offer."""
    
    confidence: float = 0.5
    """Confidence in response."""
    
    uncertainty: float = 0.5
    """Uncertainty in response."""
    
    response_status: str = ""  # CCPNegotiationResponseStatus value
    """Response status."""
    
    provenance: str = ""
    """Response provenance."""


# =============================================================================
# CCP NEGOTIATION RESULT - Final negotiation outcome
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPNegotiationResult:
    """
    Immutable negotiation result model.
    
    NEGOTIATION-LAW-001: Negotiation is declarative
    NEGOTIATION-LAW-002: Every provider response is preserved
    NEGOTIATION-LAW-005: Selection rationale is preserved
    """
    negotiation_identity: str = ""
    """Associated negotiation identity."""
    
    request_reference: Optional[str] = None
    """Reference to original request."""
    
    response_references: tuple[str, ...] = field(default_factory=tuple)
    """All provider response references."""
    
    selected_provider_references: tuple[str, ...] = field(default_factory=tuple)
    """Selected provider identities."""
    
    fallback_provider_references: tuple[str, ...] = field(default_factory=tuple)
    """Fallback providers if selection fails."""
    
    satisfaction_status: str = "unknown"
    """Requirement satisfaction status after negotiation."""
    
    selection_rationale: str = ""
    """Rationale for selections."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during negotiation."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this result."""
    
    confidence: float = 0.5
    """Confidence in result correctness."""
    
    uncertainty: float = 0.5
    """Uncertainty about result correctness."""
    
    provenance: str = ""
    """Result provenance."""


# =============================================================================
# CCP SYNCHRONIZATION REQUEST - Synchronization request model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPSynchronizationRequest:
    """
    Immutable synchronization request model.
    
    SYNC-LAW-001: Synchronization is semantic
    SYNC-LAW-002: Barrier status is explicit
    """
    cycle_identity: str = ""
    """Coordination cycle identity."""
    
    requesting_network: Optional[str] = None
    """Network making the request."""
    
    required_participants: tuple[str, ...] = field(default_factory=tuple)
    """Required participant networks."""
    
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)
    """Required capabilities for synchronization."""
    
    required_projection_revisions: tuple[int, ...] = field(default_factory=tuple)
    """Required projection revision numbers."""
    
    barrier_reference: Optional[str] = None
    """Reference to synchronization barrier."""
    
    synchronization_group_reference: Optional[str] = None
    """Reference to synchronization group."""
    
    semantic_deadline: Optional[str] = None
    """Deadline for synchronization."""
    
    provenance: str = ""
    """Request provenance."""


# =============================================================================
# CCP SYNCHRONIZATION STATUS - Synchronization status report
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPSynchronizationStatus:
    """
    Immutable synchronization status model.
    
    SYNC-LAW-001: Synchronization is semantic
    SYNC-LAW-003: Participant readiness is explicit
    """
    synchronization_request_reference: Optional[str] = None
    """Reference to request."""
    
    reporting_network: Optional[str] = None
    """Network reporting status."""
    
    readiness: str = "unknown"
    """Readiness state."""
    
    availability: str = "unknown"
    """Availability state."""
    
    satisfied_requirements: tuple[str, ...] = field(default_factory=tuple)
    """Satisfied requirements."""
    
    unsatisfied_requirements: tuple[str, ...] = field(default_factory=tuple)
    """Unsatisfied requirements."""
    
    active_constraints: tuple[str, ...] = field(default_factory=tuple)
    """Active constraints affecting synchronization."""
    
    status: str = ""  # CCPSynchronizationStatus value
    """Overall synchronization status."""
    
    confidence: float = 0.5
    """Confidence in this report."""
    
    uncertainty: float = 0.5
    """Uncertainty about this report."""
    
    provenance: str = ""
    """Status report provenance."""


# =============================================================================
# CCP BARRIER STATUS - Barrier state message
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPBarrierStatus:
    """
    Immutable barrier status model.
    
    SYNC-LAW-002: Barrier status is explicit
    SYNC-LAW-004: Missing participants are explicit
    """
    barrier_reference: Optional[str] = None
    """Unique barrier identity."""
    
    cycle_identity: str = ""
    """Cycle identity for this barrier."""
    
    barrier_status: str = "unknown"
    """Overall barrier status."""
    
    required_participants: tuple[str, ...] = field(default_factory=tuple)
    """Required participant identities."""
    
    satisfied_participants: tuple[str, ...] = field(default_factory=tuple)
    """Participants that have reached the barrier."""
    
    missing_participants: tuple[str, ...] = field(default_factory=tuple)
    """Participants not yet at barrier."""
    
    blocking_constraints: tuple[str, ...] = field(default_factory=tuple)
    """Constraints blocking progress."""
    
    unresolved_dependencies: tuple[str, ...] = field(default_factory=tuple)
    """Unresolved dependencies."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during barrier evaluation."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this status."""
    
    provenance: str = ""
    """Barrier status provenance."""


# =============================================================================
# CCP TRANSITION INTENTION - Transition intention message
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPTransitionIntention:
    """
    Immutable transition intention model.
    
    TRANSITION-LAW-001: Transition intention is distinct from completion
    TRANSITION-LAW-002: Prerequisites are explicit
    TRANSITION-LAW-003: Blocking constraints are explicit
    """
    transition_reference: Optional[str] = None
    """Unique transition identity."""
    
    source_network: Optional[str] = None
    """Source network identity."""
    
    source_state_reference: Optional[str] = None
    """Reference to source state."""
    
    target_state_reference: Optional[str] = None
    """Reference to target state."""
    
    prerequisites: tuple[str, ...] = field(default_factory=tuple)
    """Prerequisites for this transition."""
    
    blocking_constraints: tuple[str, ...] = field(default_factory=tuple)
    """Constraints that could block transition."""
    
    required_acknowledgements: tuple[str, ...] = field(default_factory=tuple)
    """Required acknowledgements before execution."""
    
    confidence: float = 0.5
    """Confidence in this intention."""
    
    uncertainty: float = 0.5
    """Uncertainty about this intention."""
    
    provenance: str = ""
    """Intention provenance."""


# =============================================================================
# CCP TRANSITION STATUS - Transition status message
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPTransitionStatus:
    """
    Immutable transition status model.
    
    TRANSITION-LAW-001: Status is distinct from completion
    TRANSITION-LAW-004: Status preserves lineage
    """
    transition_reference: Optional[str] = None
    """Reference to transition."""
    
    reporting_network: Optional[str] = None
    """Network reporting status."""
    
    status: str = ""  # CCPTransitionStatus value
    """Current transition status."""
    
    satisfied_prerequisites: tuple[str, ...] = field(default_factory=tuple)
    """Satisfied prerequisites."""
    
    missing_prerequisites: tuple[str, ...] = field(default_factory=tuple)
    """Missing prerequisites."""
    
    active_constraints: tuple[str, ...] = field(default_factory=tuple)
    """Active constraints."""
    
    acknowledgements: tuple[str, ...] = field(default_factory=tuple)
    """Received acknowledgements."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during status evaluation."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this status."""
    
    provenance: str = ""
    """Status report provenance."""


# =============================================================================
# CCP CONFLICT REPORT - Conflict report model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPConflictReport:
    """
    Immutable conflict report model.
    
    CONSTRAINT-LAW-004: Conflict reports preserve participating entities
    CONSTRAINT-LAW-005: Severity is explicit
    """
    conflict: str = ""
    """Conflict identifier."""
    
    reporting_network: Optional[str] = None
    """Network reporting the conflict."""
    
    participating_references: tuple[str, ...] = field(default_factory=tuple)
    """Participating entity references."""
    
    structural_or_cognitive: str = "unknown"
    """Type of conflict (structural vs cognitive)."""
    
    severity: str = "warning"
    """Conflict severity level."""
    
    blocking_status: str = "not_blocking"
    """Whether this blocks coordination."""
    
    resolution_authority: Optional[str] = None
    """Authority responsible for resolving."""
    
    confidence: float = 0.5
    """Confidence in report."""
    
    uncertainty: float = 0.5
    """Uncertainty about report."""
    
    provenance: str = ""
    """Conflict report provenance."""


# =============================================================================
# CCP FAILURE REPORT - Failure report model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPFailureReport:
    """
    Immutable failure report model.
    
    FAILURE-LAW-001: Failures preserve failed artifacts
    FAILURE-LAW-002: Affected capabilities are preserved
    """
    identity: str = ""
    """Unique failure identity."""
    
    reporting_network: Optional[str] = None
    """Network reporting the failure."""
    
    failed_artifact_reference: Optional[str] = None
    """Reference to failed artifact."""
    
    failure_kind: str = ""  # CCPFailureKind value (not yet defined)
    """Kind of failure."""
    
    severity: str = "warning"
    """Severity level."""
    
    affected_capabilities: tuple[str, ...] = field(default_factory=tuple)
    """Capabilities affected by this failure."""
    
    affected_requirements: tuple[str, ...] = field(default_factory=tuple)
    """Requirements affected by this failure."""
    
    recoverability: str = "unknown"
    """Whether this is recoverable."""
    
    proposed_recovery_scope: Optional[str] = None
    """Proposed recovery scope."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during failure evaluation."""
    
    provenance: str = ""
    """Failure report provenance."""


# =============================================================================
# CCP RECOVERY REQUEST - Recovery request model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPRecoveryRequest:
    """
    Immutable recovery request model.
    
    FAILURE-LAW-003: Recovery is declarative
    FAILURE-LAW-005: Selected paths are preserved
    """
    failed_artifact_reference: Optional[str] = None
    """Reference to failed artifact."""
    
    requesting_network: Optional[str] = None
    """Network requesting recovery."""
    
    recovery_scope: str = ""
    """Scope of recovery needed."""
    
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)
    """Required capabilities for recovery."""
    
    excluded_participants: tuple[str, ...] = field(default_factory=tuple)
    """Participants to exclude from recovery."""
    
    accepted_degradation: str = "none"
    """Acceptable degradation level."""
    
    semantic_deadline: Optional[str] = None
    """Deadline for recovery."""
    
    provenance: str = ""
    """Recovery request provenance."""


# =============================================================================
# CCP RECOVERY PROPOSAL - Recovery proposal model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPRecoveryProposal:
    """
    Immutable recovery proposal model.
    
    FAILURE-LAW-004: Proposals preserve degradation info
    """
    recovery_request_reference: Optional[str] = None
    """Reference to request."""
    
    proposing_network: Optional[str] = None
    """Network proposing the recovery."""
    
    recovery_path_reference: Optional[str] = None
    """Reference to proposed recovery path."""
    
    replacement_capabilities: tuple[str, ...] = field(default_factory=tuple)
    """Replacement capabilities being offered."""
    
    replacement_providers: tuple[str, ...] = field(default_factory=tuple)
    """Replacement providers."""
    
    degraded_semantics: str = "none"
    """Level of semantic degradation."""
    
    confidence: float = 0.5
    """Confidence in this proposal."""
    
    uncertainty: float = 0.5
    """Uncertainty about this proposal."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this proposal."""
    
    provenance: str = ""
    """Proposal provenance."""


# =============================================================================
# CCP RECOVERY RESULT - Recovery result model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPRecoveryResult:
    """
    Immutable recovery result model.
    
    FAILURE-LAW-005: Selected paths are preserved
    """
    recovery_request_reference: Optional[str] = None
    """Reference to request."""
    
    selected_recovery_path: Optional[str] = None
    """Selected recovery path."""
    
    accepted_proposals: tuple[str, ...] = field(default_factory=tuple)
    """Accepted proposals."""
    
    rejected_proposals: tuple[str, ...] = field(default_factory=tuple)
    """Rejected proposals."""
    
    resulting_plan_reference: Optional[str] = None
    """Resulting coordination plan reference."""
    
    resulting_cycle_reference: Optional[str] = None
    """Resulting cycle reference."""
    
    status: str = "unknown"
    """Recovery result status."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during recovery."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this result."""
    
    provenance: str = ""
    """Result provenance."""


# =============================================================================
# CCP LIFECYCLE NOTICE - Lifecycle state notice
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPLifecycleNotice:
    """
    Immutable lifecycle notice model.
    
    LIFECYCLE-LAW-001: Lifecycle notices are semantic
    LIFECYCLE-LAW-002: Lifecycle states are explicit
    """
    network_identity: Optional[str] = None
    """Network identity."""
    
    lifecycle_state: str = ""  # CCPLifecycleState value
    """Current lifecycle state."""
    
    affected_capabilities: tuple[str, ...] = field(default_factory=tuple)
    """Capabilities affected by this state."""
    
    affected_subscriptions: tuple[str, ...] = field(default_factory=tuple)
    """Subscriptions affected."""
    
    affected_requirements: tuple[str, ...] = field(default_factory=tuple)
    """Requirements affected."""
    
    effective_semantic_scope: Optional[str] = None
    """Semantic scope of this notice."""
    
    replacement_network_reference: Optional[str] = None
    """Reference to replacement network (if any)."""
    
    provenance: str = ""
    """Notice provenance."""


# =============================================================================
# CCP HEARTBEAT PROJECTION - Semantic heartbeat model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPHeartbeatProjection:
    """
    Immutable semantic heartbeat model.
    
    LIFECYCLE-LAW-007: Heartbeat is semantic (not a runtime liveness probe)
    """
    network_identity: Optional[str] = None
    """Network identity."""
    
    confirmed_projection_reference: Optional[str] = None
    """Reference to confirmed projection."""
    
    lifecycle_state: str = ""  # CCPLifecycleState value
    """Current lifecycle state."""
    
    availability: str = "unknown"
    """Availability state."""
    
    readiness: str = "unknown"
    """Readiness state."""
    
    contract_version: str = "1.0.0"
    """Contract version."""
    
    semantic_context_revision: Optional[str] = None
    """Semantic context revision."""
    
    provenance: str = ""
    """Heartbeat provenance."""