# Perception Interfaces Shared Components - Phase 5.2.5
# =====================================================

"""
Shared components for all Perception Interfaces.

This module contains the core infrastructure used by all interface types:
- Contracts: Interface contracts defining communication semantics
- Requests: Request transport mechanism
- Responses: Response transport mechanism  
- Events: Event publication mechanism
"""

from .contract import (
    # Interface kinds
    InterfaceKind,
    
    # Status codes
    InterfaceStatus,
    
    # Versioning and compatibility
    CompatibilityRevision,
    CompatibilityEvaluator,
    
    # Authorization
    AuthorizationContext,
    
    # Core contract
    PerceptionInterfaceContract,
    
    # Discovery and health
    InterfaceDiscoveryResult,
    InterfaceHealth,
    
    # Capabilities
    PerceptionCapabilityDescriptor,
    
    # Version negotiation
    VersionNegotiationResult,
    VersionNegotiator,
)

from .request import (
    # Request kinds
    RequestKind,
    
    # Priority classes
    RequestPriority,
    
    # Scope
    RequestScope,
    
    # Core request types
    PerceptionInterfaceRequest,
    PerceptionInterfaceRequestBuilder,
    
    # Result
    RequestResult,
)

from .response import (
    # Status codes
    ResponseStatus,
    
    # Core response types
    PerceptionInterfaceResponse,
    
    # Sensor responses
    SensorAcquisitionResponse,
    
    # Workspace responses
    PerceptionWorkspacePublication,
    WorkspacePerceptionFeedback,
    
    # Memory responses  
    PerceptionMemoryAdmissionResponse,
    
    # Grounding responses
    PerceptionGroundingResponse,
)

from .event import (
    # Event kinds
    EventKind,
    
    # Context
    EventContext,
    
    # Core event type
    PerceptionInterfaceEvent,
    
    # Interface-specific events
    SensorStatusEvent,
    AcquisitionFailureEvent,
    UpdateGapEvent,
    MemoryCorrelationEvent,
    CoordinationStatusEvent,
    SubscriptionTerminationEvent,
)

__all__ = [
    # Contract
    "InterfaceKind",
    "InterfaceStatus",
    "CompatibilityRevision",
    "AuthorizationContext",
    "PerceptionInterfaceContract",
    "InterfaceDiscoveryResult",
    "InterfaceHealth",
    "PerceptionCapabilityDescriptor",
    "CompatibilityEvaluator",
    "VersionNegotiationResult",
    "VersionNegotiator",
    
    # Request
    "RequestKind",
    "RequestPriority", 
    "RequestScope",
    "PerceptionInterfaceRequest",
    "PerceptionInterfaceRequestBuilder",
    "RequestResult",
    
    # Response
    "ResponseStatus",
    "PerceptionInterfaceResponse",
    "SensorAcquisitionResponse",
    "PerceptionWorkspacePublication",
    "WorkspacePerceptionFeedback",
    "PerceptionMemoryAdmissionResponse",
    "PerceptionGroundingResponse",
    
    # Event
    "EventKind",
    "EventContext",
    "PerceptionInterfaceEvent",
    "SensorStatusEvent",
    "AcquisitionFailureEvent",
    "UpdateGapEvent",
    "MemoryCorrelationEvent",
    "CoordinationStatusEvent",
    "SubscriptionTerminationEvent",
]