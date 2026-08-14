# Gordon Core - Communication Module (Phase 3.21)
# ================================================
#
# Canonical Communication, Messaging, and Event Architecture
#
# This module provides the single source of truth for all communication
# within the Gordon Core architecture.
#
# ARCHITECTURAL PRINCIPLES:
# - One canonical communication architecture throughout the repository
# - No implicit communication (all contracts are explicit)
# - Immutable messages after publication
# - Deterministic routing based on policies
# - Comprehensive observability and diagnostics

"""
Gordon Core Communication Module (Phase 3.21)

This module provides the single source of truth for all communication within
the Gordon Core architecture.

ARCHITECTURAL VISION:
-------------------
Every architectural entity shall communicate through explicit, typed,
deterministic contracts. No implicit communication shall exist.
Communication shall never rely upon global mutable state, hidden callbacks,
singleton notifications, or undocumented side effects.

COMPONENTS:
-----------
- foundations: Communication philosophy, terminology, ownership, boundaries
- endpoints: Endpoint types, identity, ownership, visibility, authority
- messages: Canonical message types with rich metadata
- routing: Routing algorithms and address resolution
- delivery: Delivery guarantees and reliability mechanisms
- publication: Publish-subscribe patterns
- policies: Communication policies (authorization, rate limiting, etc.)
- observability: Tracing, metrics, and diagnostics

INTEGRATION:
----------
This module integrates with:
- Phase 3.11 - Streams (durable ordered transport)
- Phase 3.12 - Core Architecture
- Phase 3.14 - Interaction Architecture (requests, responses, commands, events)
- Phase 3.17 - Execution (work performance)

ARCHITECTURAL INTEGRITY GUARANTEES:
----------------------------------
- IMMU-001: Messages are immutable after publication
- TYPED-001: Every message has an explicit type
- VALIDATED-001: Messages must pass validation before routing
- CORR-001: Related messages share correlation context
- PROV-001: Provenance is preserved throughout lifecycle

OWNERSHIP INVARIANTS:
--------------------
- OWN-MSG-001: Every message has exactly one originating runtime
- OWN-MSG-002: Ownership cannot be transferred without explicit action
- OWN-EP-001: Every endpoint has exactly one owner type
- OWN-EP-002: Ownership cannot be transferred without explicit action

VISIBILITY INVARIANTS:
---------------------
- VIS-EP-001: Endpoints can only see what they have visibility into
- VIS-EP-002: Visibility is preserved throughout message lifecycle

AUTHORITY INVARIANTS:
--------------------
- AUT-EP-001: Authority determines what operations are permitted
- AUT-EP-002: Authority cannot be elevated without explicit grant

DELIVERY INVARIANTS:
-------------------
- DLV-EP-001: Policy determines how messages are delivered
- DLV-EP-002: Policy is evaluated before message processing

MESSAGE INTEGRITY GUARANTEES:
----------------------------
- MSG-ID-001: Every message has exactly one unique identity
- MSG-ID-002: Identity is immutable once created
- MSG-ID-003: No two messages share the same identity
- MSG-STS-001: Status is immutable once set to terminal state
- MSG-STS-002: Terminal states preserve all provenance data

ROUTING INVARIANTS:
------------------
- RT-001: Every message has exactly one route type
- RT-002: Route type determines delivery mechanism
- RP-001: Policy determines how routes are resolved
- RP-002: Policy is evaluated before route selection
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple

# =============================================================================
# FOUNDATIONS (Phase 3.21.1)
# =============================================================================

from .foundations import (
    CommunicationPrinciple,
    CommunicationOwnership,
    CommunicationOwnershipRecord,
    MessageLifecyclePhase,
    CommunicationBoundary,
    CommunicationBoundaryRecord,
    CommunicationResponsibilities,
    IntegrityGuarantees,
    is_terminal_lifecycle_state,
    is_valid_lifecycle_transition,
    CanonicalCommunicationMetadata,
)

# =============================================================================
# ENDPOINTS (Phase 3.21.2)
# =============================================================================

from .endpoints import (
    EndpointId,
    EndpointOwnershipType,
    EndpointOwnership,
    VisibilityScope,
    EndpointVisibility,
    EndpointAuthority,
    EndpointAuthorityRecord,
    DeliveryPolicy,
    EndpointPolicy,
    EndpointType,
    EndpointDescriptor,
    EndpointRegistry,
    EndpointRoutingKey,
    IEndpointSender,
    IEndpointReceiver,
)

# =============================================================================
# MESSAGES (Phase 3.21.3)
# =============================================================================

from .messages import (
    MessageType,
    MessagePriority,
    MessageStatus,
    MessageId,
    MessageCorrelation,
    MessageProvenance,
    MessagePayload,
    CanonicalMessage,
    RequestMessage,
    ResponseMessage,
    CommandMessage,
    EventMessage,
    QueryMessage,
    NotificationMessage,
    MessageValidationResult,
    MessageValidation,
    DeliveryMetadata,
)

# =============================================================================
# ROUTING (Phase 3.21.6)
# =============================================================================

from .routing import (
    RouteType,
    RoutingRule,
    RoutingPolicy,
    Address,
    AddressResolver,
    RouteTable,
)

# =============================================================================
# PUBLICATION & SUBSCRIPTION (Phase 3.21.7)
# =============================================================================

from .subscription import (
    SubscriptionId,
    SubscriptionFilter,
    SubscriptionDescriptor,
    SubscriberRegistry,
    PublicationContext,
    PublishResult,
)

# =============================================================================
# DELIVERY GUARANTEES (Phase 3.21.8)
# =============================================================================

from .delivery_guarantees import (
    DeliveryMode,
    DeliveryState,
    DeliveryAttempt,
    ReliableDeliveryEngine,
    AtMostOnceStrategy,
    AtLeastOnceStrategy,
    ExactlyOnceStrategy,
)

# =============================================================================
# RELIABILITY (Phase 3.21.10)
# =============================================================================

from .reliability import (
    AcknowledgementPolicy,
    RetryStrategy,
    DeadLetterConfig,
    IdempotencyKey,
    ReplayProtectionContext,
)

# =============================================================================
# POLICIES (Phase 3.21.11)
# =============================================================================

from .policies import (
    AuthorizationRule,
    RateLimitConfig,
    VisibilityRule,
    RoutingRestriction,
    EncryptionPolicy,
    ValidationPolicy,
    CommunicationPolicies,
)


# =============================================================================
# OBSERVABILITY (Phase 3.21.13)
# =============================================================================

from .observability import (
    TraceId,
    SpanId,
    MessageTrace,
    DeliveryMetric,
    EndpointHealth,
    DiagnosticEvent,
)


# =============================================================================
# CROSS-RUNTIME COMMUNICATION (Phase 3.21.12)
# =============================================================================

from .cross_runtime import (
    RuntimeAddress,
    ClusterIdentity,
    FederationMessage,
    GatewayProtocol,
)


# =============================================================================
# CANONICAL MESSAGE BUS
# =============================================================================

class CanonicalMessageBus:
    """
    The canonical message bus for the Gordon Core.
    
    This is the single entry point for all communication within a runtime.
    It integrates all communication components and provides a unified API.
    
    Invariants:
        - CBUS-001: Exactly one message bus per runtime
        - CBUS-002: All messages pass through this bus
        - CBUS-003: Messages are immutable after publication
        - CBUS-004: Routing is deterministic and policy-driven
    """
    
    def __init__(self):
        self._endpoints = EndpointRegistry()
        self._subscriptions = SubscriberRegistry()
        
    async def publish(
        self,
        message: CanonicalMessage,
        endpoint_descriptor: Optional[EndpointDescriptor] = None,
    ) -> bool:
        """Publish a message to its intended recipients."""
        # Implementation would integrate routing, delivery, and subscription
        raise NotImplementedError
    
    async def subscribe(
        self,
        subscriber_descriptor: EndpointDescriptor,
        filter: SubscriptionFilter,
        delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
    ) -> str:
        """Subscribe an endpoint to messages matching a filter."""
        # Implementation would register the subscription
        raise NotImplementedError
    
    async def unregister_endpoint(self, endpoint_id: str) -> bool:
        """Unregister an endpoint and cancel its subscriptions."""
        return self._endpoints.unregister(endpoint_id)


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Foundations (3.21.1)
    "CommunicationPrinciple",
    "CommunicationOwnership",
    "CommunicationOwnershipRecord",
    "MessageLifecyclePhase",
    "CommunicationBoundary",
    "CommunicationBoundaryRecord",
    "CommunicationResponsibilities",
    "IntegrityGuarantees",
    "is_terminal_lifecycle_state",
    "is_valid_lifecycle_transition",
    "CanonicalCommunicationMetadata",
    
    # Endpoints (3.21.2)
    "EndpointId",
    "EndpointOwnershipType",
    "EndpointOwnership",
    "VisibilityScope",
    "EndpointVisibility",
    "EndpointAuthority",
    "EndpointAuthorityRecord",
    "DeliveryPolicy",
    "EndpointPolicy",
    "EndpointType",
    "EndpointDescriptor",
    "EndpointRegistry",
    "EndpointRoutingKey",
    "IEndpointSender",
    "IEndpointReceiver",
    
    # Messages (3.21.3)
    "MessageType",
    "MessagePriority",
    "MessageStatus",
    "MessageId",
    "MessageCorrelation",
    "MessageProvenance",
    "MessagePayload",
    "CanonicalMessage",
    "RequestMessage",
    "ResponseMessage",
    "CommandMessage",
    "EventMessage",
    "QueryMessage",
    "NotificationMessage",
    "MessageValidationResult",
    "MessageValidation",
    "DeliveryMetadata",
    
    # Routing (3.21.6)
    "RouteType",
    "RoutingRule",
    "RoutingPolicy",
    "Address",
    "AddressResolver",
    "RouteTable",
    
    # Publication & Subscription (3.21.7)
    "SubscriptionId",
    "SubscriptionFilter",
    "SubscriptionDescriptor",
    "SubscriberRegistry",
    "PublicationContext",
    "PublishResult",
    
    # Delivery Guarantees (3.21.8)
    "DeliveryMode",
    "DeliveryState",
    "DeliveryAttempt",
    "ReliableDeliveryEngine",
    "AtMostOnceStrategy",
    "AtLeastOnceStrategy",
    "ExactlyOnceStrategy",
    
    # Reliability (3.21.10)
    "AcknowledgementPolicy",
    "RetryStrategy",
    "DeadLetterConfig",
    "IdempotencyKey",
    "ReplayProtectionContext",
    
    # Policies (3.21.11)
    "AuthorizationRule",
    "RateLimitConfig",
    "VisibilityRule",
    "RoutingRestriction",
    "EncryptionPolicy",
    "ValidationPolicy",
    "CommunicationPolicies",
    
    # Observability (3.21.13)
    "TraceId",
    "SpanId",
    "MessageTrace",
    "DeliveryMetric",
    "EndpointHealth",
    "DiagnosticEvent",
    
    # Cross-runtime (3.21.12)
    "RuntimeAddress",
    "ClusterIdentity",
    "FederationMessage",
    "GatewayProtocol",
    
    # Main bus
    "CanonicalMessageBus",
]