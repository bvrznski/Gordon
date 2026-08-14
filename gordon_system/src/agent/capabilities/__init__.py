# Capabilities layer - intelligent behaviors and actions.
# =========================================================

"""
Capabilities Layer for Gordon.

This package provides canonical contracts for capability invocation,
execution, and result publication while preserving architectural ownership,
authority, determinism, and integrity.

ARCHITECTURAL PRINCIPLES:
=========================

Execution schedules work.
Interactions request work.
Capabilities perform work.
Streams transport interaction records.
Systems own persistent state.

OWNERSHIP MODEL:
================

Capabilities own computation.
Execution owns scheduling.
Interactions own communication semantics.
Streams own transport.
Systems own persistent state.

These ownership rights are immutable throughout invocation lifecycle.


INVOCATION FLOW:
================

Execution → Interaction → Capability Admission → Capability Invocation
    → Capability Execution → Capability Result → Interaction Publication


INVOCATION LIFECYCLE:
=====================

Created → Validated → Admitted → Scheduled → Executing
    │                              ├─► Cancelled
    │                              ├─► Failed
    ▼
Completed → Published


AUTHORITY MODEL:
================

Capabilities never self-authorize.
Capability invocation is always subject to external authority verification.
Authority remains external to computation.

"""

from gordon_system.src.agent.capabilities.invocation import (
    # Identity types
    CapabilityInvocationId,
    CapabilityAdmissionId,
    CapabilityExecutionId,
    
    # Lifecycle states
    CapabilityLifecycleState,
    is_terminal_state,
    get_allowed_transitions,
    
    # Context types
    InvocationContext,
    AdmissionContext,
    ExecutionExecutionContext,
    ExecutionContextCancellationView,
    ExecutionCancelledError,
    
    # Protocol types
    ExecutionObservabilityPort,
    TraceRecord,
    AuditRecord,
    CapabilityExecutor,
    
    # Result types
    CapabilityExecutionResult,
    ExecutionStatus,
    PublishedResult,
    
    # Metadata
    CapabilityMetadata,
    
    # Request/Handle types
    CapabilityInvocationRequest,
    CapabilityInvocationHandle,
    
    # Cancellation types
    InvocationCancellationRequest,
    CancellationSource,
    
    # Failure types
    CapabilityFailureCategory,
    CapabilityFailure,
    
    # Publication types
    ResultPublication,
    PublicationStatus,
    
    # Stream integration
    CapabilityStreamIntegration,
    
    # Protocol types for verification
    OwnershipPreservationProtocol,
    AuthorityPreservationProtocol,
    
    # Replay types
    ReplayMetadata,
    
    # Observability types
    InvocationObservabilityMetadata,
    
    # Base protocol
    Capability,
)

__all__ = [
    "CapabilityInvocationId",
    "CapabilityAdmissionId",
    "CapabilityExecutionId",
    "CapabilityLifecycleState",
    "is_terminal_state",
    "get_allowed_transitions",
    "InvocationContext",
    "AdmissionContext",
    "ExecutionExecutionContext",
    "ExecutionContextCancellationView",
    "ExecutionCancelledError",
    "ExecutionObservabilityPort",
    "TraceRecord",
    "AuditRecord",
    "CapabilityExecutor",
    "CapabilityExecutionResult",
    "ExecutionStatus",
    "PublishedResult",
    "CapabilityMetadata",
    "CapabilityInvocationRequest",
    "CapabilityInvocationHandle",
    "InvocationCancellationRequest",
    "CancellationSource",
    "CapabilityFailureCategory",
    "CapabilityFailure",
    "ResultPublication",
    "PublicationStatus",
    "CapabilityStreamIntegration",
    "OwnershipPreservationProtocol",
    "AuthorityPreservationProtocol",
    "ReplayMetadata",
    "InvocationObservabilityMetadata",
    "Capability",
]