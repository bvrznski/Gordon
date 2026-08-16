# Gordon Cognitive Architecture - Phase 4.11.5
# ===========================================

"""
Cognitive Coordination Protocol (CCP) Package
==============================================

Canonical semantic communication protocol for Gordon's cognitive architecture.

COGNITIVE COORDINATION PROTOCOL OVERVIEW
========================================

The Cognitive Coordination Protocol (CCP) is the canonical semantic communication
protocol between all canonical cognitive networks in Gordon:

    Alerting Network        Reward Network
           \                      /
            \                    /
             v                  v
         Predictive Network <- Workspace Network
              ^                  ^
             /                   \
            /                     \
      Salience Network       Sensorimotor Network

ALL communication between these networks occurs through CCP.

PROTOCOL OWNERSHIP
==================

CCP owns:
  - Protocol identity, versioning, compatibility
  - Message taxonomy and semantics
  - Publication contracts and validation
  - Subscription matching and filtering
  - Acknowledgement semantics (distinct from acceptance)
  - Negotiation processes
  - Synchronization protocols
  - Revision lineage and provenance

CCP does NOT own:
  - Transport mechanisms (in-process, IPC, network, etc.)
  - Runtime scheduling and threading
  - Message queues
  - RPC invocations
  - Network execution or cognition

ARCHITECTURAL PRINCIPLES
========================

1. Semantic communication: Messages represent MEANING, not implementation
2. Protocol immutability: All CCP artifacts are immutable
3. Network autonomy: Networks remain autonomous; CCP only coordinates
4. Deterministic processing: Equivalent inputs produce equivalent outputs
5. Version compatibility: Forward and backward compatible evolution
6. Provenance tracking: Every artifact preserves its origin

PUBLIC API
==========

Core Protocol:
  - CognitiveCoordinationProtocolIdentity: Protocol specification identity
  - CCPVersion: Protocol version model
  
Message Envelope:
  - CCPMessage: Immutable message envelope with semantic metadata
  - CCPPublisherReference: Publisher authority model
  - CCPConsumerReference: Consumer subscription model
  
Publications and Subscriptions:
  - CCPPublication: Publication contract record
  - CCPSubscription: Subscription contract model
  
Acknowledgements:
  - CCPAcknowledgement: Acknowledgement contract
  - CCPMessageAcceptance: Semantic acceptance record
  - CCPMessageRejection: Rejection with explicit reasons
  - CCPMessageDeferral: Deferred acceptance record

Protocol Processing:
  - CCPProcessingRequest: Protocol processing input
  - CCPProcessingResult: Protocol processing output

Enums:
  - CCPMessageKind: Canonical message kind taxonomy
  - CCPPayloadKind: Canonical payload kind ontology
  - CCPMessageVisibility: Semantic visibility scopes
  - CCPPublicationStatus: Publication status states
  - CCPAcknowledgementKind: Acknowledgement kinds
  - CCPCompatibilityStatus: Compatibility evaluation results

Serialization:
  - CCPSerializer: Deterministic serialization interface

Example Usage:
    # Create a protocol identity
    identity = CCPProtocolIdentity.v1_0()
    
    # Create a message publisher reference
    publisher = CCPPublisherReference.for_network("reward-net", "RewardNetwork")
    
    # Create a message envelope
    msg = CCPMessage(
        identity="msg:reward:1",
        message_kind=CCPMessageKind.PROJECTION_PUBLICATION.value,
        payload_kind=CCPPayloadKind.NETWORK_PROJECTION.value,
        publisher=publisher.network_identity,
        protocol_version="1.0.0",
        revision=1,
        semantic_time="epoch-1/cycle-5",
        correlation_id="corr:reward-pub:1",
        confidence=0.95,
        uncertainty=0.05,
    )
    
    # Create a publication
    visibility = CCPMessageVisibility(visibility_scope="targeted_networks")
    pub = CCPPublication.create_initial(msg, publisher, visibility)

DETERMINISM INVARIANTS
======================

This package maintains:

  - DETERM-INV-001: Equivalent inputs produce equivalent outputs
  - DETERM-INV-002: No wall-clock time acquisition during import
  - DETERM-INV-003: No random identity generation
  - DETERM-INV-004: No runtime network access during import
  - DETERM-INV-005: Deterministic serialization and deserialization

ARCHITECTURAL LAWS
==================

CCP-LAW-001: Every message has stable semantic identity
CCP-LAW-002: All messages are immutable (deeply frozen)
CCP-LAW-003: Publication does not imply acceptance
CCP-LAW-004: Acknowledgement is distinct from acceptance
CCP-LAW-005: Subscriptions remain declarative
CCP-LAW-006: Network autonomy is preserved
CCP-LAW-007: Protocol version compatibility is explicit
CCP-LAW-008: Provenance is never lost

IMPORT SAFETY
=============

This package is import-safe:
  - No filesystem access during import
  - No network access during import  
  - No model loading during import
  - No runtime initialization during import
  - No random identity generation during import
  - No wall-clock acquisition during import

All construction is deterministic given identical semantic inputs.
"""

# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

from .enums import (
    CCPMessageKind,
    CCPPayloadKind,
    CCPMessageVisibility,
    CCPPublicationStatus,
    CCPAcknowledgementKind,
    CCPMessageAcceptanceStatus,
    CCPRejectionKind,
    CCPDeferralReason,
    CCPNegotiationResponseStatus,
    CCPSynchronizationStatus,
    CCPTransitionStatus,
    CCPLifecycleState,
    CCPRevisionKind,
    CCPCompatibilityStatus,
)

from .protocol_models import (
    # Protocol identity and version
    CCPProtocolIdentity,
    CCPVersion,
    
    # Message envelope
    CCPMessage,
    CCPPublisherReference,
    CCPConsumerReference,
    
    # Contracts
    CCPPublication,
    CCPSubscription,
    CCPAcknowledgement,
    CCPMessageAcceptance,
    CCPMessageRejection,
    CCPMessageDeferral,
    CCPMessageVisibility as CCPMsgVisModel,  # renamed
    
    # Capability and requirement
    CCPCapabilityAdvertisement,
    CCPRequirementDeclaration,
    
    # Negotiation
    CCPNegotiationRequest,
    CCPNegotiationResponse,
    CCPNegotiationResult,
    
    # Synchronization
    CCPSynchronizationRequest,
    CCPSynchronizationStatus as CCPSyncStatus,  # renamed to avoid conflict
    CCPBarrierStatus,
    
    # Transitions
    CCPTransitionIntention,
    CCPTransitionStatus,
    
    # Conflict and failure
    CCPConflictReport,
    CCPFailureReport,
    
    # Recovery
    CCPRecoveryRequest,
    CCPRecoveryProposal,
    CCPRecoveryResult,
    
    # Lifecycle
    CCPLifecycleNotice,
    CCPHeartbeatProjection,
)

# Re-export visibility consistently (protocol_models is the source of truth)
CCPMessageVisibility = CCPMsgVisModel  # from protocol_models

# Also re-export from protocol module
from .protocol import (
    CCPProtocol,
    CCPProcessingRequest,
    CCPProcessingResult,
    CCPMessageValidator,
    CCPPublicationValidator,
    CCPSubscriptionMatcher,
    CCPCompatibilityChecker,
)

__all__ = [
    # Enums
    "CCPMessageKind",
    "CCPPayloadKind",
    "CCPMessageVisibility",
    "CCPPublicationStatus",
    "CCPAcknowledgementKind",
    "CCPMessageAcceptanceStatus",
    "CCPRejectionKind",
    "CCPDeferralReason",
    "CCPNegotiationResponseStatus",
    "CCPSynchronizationStatus",
    "CCPTransitionStatus",
    "CCPLifecycleState",
    "CCPRevisionKind",
    "CCPCompatibilityStatus",
    
    # Core models
    "CCPProtocolIdentity",
    "CCPVersion",
    "CCPMessage",
    "CCPPublisherReference",
    "CCPConsumerReference",
    "CCPPublication",
    "CCPSubscription",
    "CCPAcknowledgement",
    "CCPMessageAcceptance",
    "CCPMessageRejection",
    "CCPMessageDeferral",
    "CCPCapabilityAdvertisement",
    "CCPRequirementDeclaration",
    
    # Negotiation models
    "CCPNegotiationRequest",
    "CCPNegotiationResponse",
    "CCPNegotiationResult",
    
    # Synchronization models
    "CCPSynchronizationRequest",
    "CCPSynchronizationStatus",
    "CCPBarrierStatus",
    
    # Transition models
    "CCPTransitionIntention",
    "CCPTransitionStatus",
    
    # Conflict and failure models
    "CCPConflictReport",
    "CCPFailureReport",
    
    # Recovery models
    "CCPRecoveryRequest",
    "CCPRecoveryProposal",
    "CCPRecoveryResult",
    
    # Lifecycle models
    "CCPLifecycleNotice",
    "CCPHeartbeatProjection",
]

# =============================================================================
# PACKAGE METADATA
# =============================================================================

__version__ = "1.0.0"
__protocol_family__ = "gordon_ccp"
__protocol_identity__ = CCPProtocolIdentity.v1_0()