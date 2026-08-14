# Interaction Architecture
# =======================
#
# PHASE 3.14.x - Interaction Taxonomy and Semantics

"""
Interaction Architecture Package for Gordon.

This package provides the canonical taxonomy of interactions,
enabling semantic classification of all architectural relationships.
"""

from .taxonomy import (
    # Primary categories (the taxonomy)
    InteractionCategory,
    
    # Secondary traits
    InteractionTrait,
    
    # Identity types
    InteractionId,
    InteractionCorrelation,
    
    # Base interaction type
    Interaction,
    
    # Concrete types (from taxonomy)
    Request as TaxonomyRequest,
    Response as TaxonomyResponse,
    Command as TaxonomyCommand,
    Event,
    Signal,
    Notification,
    Proposal,
    Observation,
    Query,
    Publication,
    Subscription,
    Checkpoint,
    Heartbeat,
    Synchronization,
    Transaction,
    Recovery,
    
    # Utility functions
    are_categories_compatible,
    is_primary_category_valid,
    CATEGORY_RELATIONSHIPS,
    INCOMPATIBLE_PAIRS,
)

from .semantics import (
    # Lifecycle states (canonical Phase 3.14.4)
    RequestState,
    ResponseState,
    CommandState,
    
    # Outcome types
    Outcome,
    
    # Diagnostic metadata for observability
    DiagnosticMetadata,
    
    # Canonical semantic types
    Request,
    Response,
    Command,
    
    # Utility functions
    dataclass_replace,
    are_semantic_categories_compatible,
    get_request_state_for_response,
)

from .observability import (
    # Diagnostic record types (Phase 3.14.16)
    DiagnosticRecord,
    DiagnosticSeverity,
    DiagnosticCategory,
    
    # Observation layer
    ObservationMode,
    ObservationContext,
    Observation,
    
    # Correlation system
    CorrelationType,
    CorrelationEdge,
    CorrelationGraph,
    
    # Provenance tracking
    ProvenanceRecord,
    ProvenanceChain,
    
    # Diagnostic lifecycle
    DiagnosticLifecycleState,
    DiagnosticLifecycleEvent,
    DiagnosticLifecycle,
    
    # Architectural metrics
    MetricType,
    MetricPoint,
    MetricAggregation,
    
    # Traceability
    TraceEventType,
    TraceEvent,
    ExecutionTrace,
    
    # Replay diagnostics
    ReplaySource,
    ReplayConfig,
    ReplayResult,
    
    # Certification diagnostics
    CertificationStatus,
    CertificationRecord,
    
    # Integrity verification
    IntegrityCheckResult,
    verify_diagnostic_integrity,
)

# Phase 3.14.5: Event, Signal, and Notification semantics
# These types are defined in event_signal_notification_semantics.py which is a future implementation

EventState = None  # To be implemented when event_signal_notification_semantics.py exists
SignalState = None
NotificationState = None

EventType = None
SignalType = None
NotificationType = None

EventSignalNotificationDiagnosticMetadata = None
ObserverReference = None
PublicationMetadata = None
ObservationRecord = None
OrderingGuarantee = None
ReplayMetadata = None

ESNEvent = None  # Aliased to Event when implemented
ESNSignal = None
ESNNotification = None

event_transition_created_to_published = None
signal_transition_observed_to_published = None
notification_transition_created_to_published = None

validate_event_semantics = None
validate_signal_semantics = None
validate_notification_semantics = None

esn_are_semantic_categories_compatible = None
get_lifecycle_state_for_category = None
# Phase 3.14.16: Import observability module

from .observability import (
    # Identity types
    DiagnosticIdType,
    DiagnosticId,
    ObservationId,
    CorrelationId,
)

__all__ = [
    # Taxonomy categories
    "InteractionCategory",
    "InteractionTrait",
    
    # Identity types
    "InteractionId",
    "InteractionCorrelation",
    
    # Base interaction type
    "Interaction",
    
    # Concrete types (from taxonomy)
    "TaxonomyRequest",
    "TaxonomyResponse",
    "TaxonomyCommand",
    "Event",
    "Signal",
    "Notification",
    "Proposal",
    "Observation",
    "Query",
    "Publication",
    "Subscription",
    "Checkpoint",
    "Heartbeat",
    "Synchronization",
    "Transaction",
    "Recovery",
    
    # Canonical semantic types (Phase 3.14.4)
    "Request",
    "Response",
    "Command",
    
    # Lifecycle states (Phase 3.14.4)
    "RequestState",
    "ResponseState",
    "CommandState",
    
    # Outcome types
    "Outcome",
    
    # Diagnostic metadata for observability (Phase 3.14.4)
    "DiagnosticMetadata",
    
    # Utility functions (Phase 3.14.4)
    "are_categories_compatible",
    "is_primary_category_valid",
    "dataclass_replace",
    "are_semantic_categories_compatible",
    "get_request_state_for_response",
    "CATEGORY_RELATIONSHIPS",
    "INCOMPATIBLE_PAIRS",
    
    # Lifecycle states (Phase 3.14.5)
    "EventState",
    "SignalState",
    "NotificationState",
    
    # Semantic type enumerations (Phase 3.14.5)
    "EventType",
    "SignalType",
    "NotificationType",
    
    # Diagnostic metadata for observability (Phase 3.14.5)
    "EventSignalNotificationDiagnosticMetadata",
    
    # Publication and tracking types (Phase 3.14.5)
    "ObserverReference",
    "PublicationMetadata",
    "ObservationRecord",
    
    # Ordering and replay (Phase 3.14.5)
    "OrderingGuarantee",
    "ReplayMetadata",
    
    # Canonical semantic types (Phase 3.14.5) - aliased to avoid conflict with taxonomy
    "ESNEvent",
    "ESNSignal",
    "ESNNotification",
    
    # Transition functions (Phase 3.14.5)
    "event_transition_created_to_published",
    "signal_transition_observed_to_published",
    "notification_transition_created_to_published",
    
    # Validation functions (Phase 3.14.5)
    "validate_event_semantics",
    "validate_signal_semantics",
    "validate_notification_semantics",
    
    # Utility functions (Phase 3.14.5)
    "esn_are_semantic_categories_compatible",
    "get_lifecycle_state_for_category",
    
    # Phase 3.14.16: Diagnostic observability and diagnostics architecture
    # Diagnostic record types
    "DiagnosticRecord",
    "DiagnosticSeverity",
    "DiagnosticCategory",
    
    # Observation layer
    "ObservationMode",
    "ObservationContext",
    "Observation",
    
    # Correlation system
    "CorrelationType",
    "CorrelationEdge",
    "CorrelationGraph",
    
    # Provenance tracking
    "ProvenanceRecord",
    "ProvenanceChain",
    
    # Diagnostic lifecycle
    "DiagnosticLifecycleState",
    "DiagnosticLifecycleEvent",
    "DiagnosticLifecycle",
    
    # Architectural metrics
    "MetricType",
    "MetricPoint",
    "MetricAggregation",
    
    # Traceability
    "TraceEventType",
    "TraceEvent",
    "ExecutionTrace",
    
    # Replay diagnostics
    "ReplaySource",
    "ReplayConfig",
    "ReplayResult",
    
    # Certification diagnostics
    "CertificationStatus",
    "CertificationRecord",
    
    # Integrity verification
    "IntegrityCheckResult",
    "verify_diagnostic_integrity",
    
    # Identity types (Phase 3.14.16)
    "DiagnosticIdType",
    "DiagnosticId",
    "ObservationId",
    "CorrelationId",
]