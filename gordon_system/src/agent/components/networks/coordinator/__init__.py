# Gordon Cognitive Architecture - Phase 4.11.1
# ===========================================

"""
Coordination Network - Inter-Network Coherence Layer

This module defines the canonical semantic architecture for coordinating
multiple cognitive networks into coherent global states.

COORDINATION NETWORK OVERVIEW
===========================

The Coordination Network is Gordon's canonical inter-network coherence layer.
It does not perform the cognitive work of the coordinated networks. It makes
their simultaneous operation coherent.

CANONICAL COORDINATED NETWORKS
----------------------------
1. Alerting Network - alert generation and interruption signals
2. Default Network - default-mode cognition and internally directed processing
3. Executive Network - executive evaluation and control directives
4. Focusing Network - focal selection and maintenance
5. Oriented Network - orientation and target-directed orienting
6. Predictive Network - predictions, errors, and precision
7. Reward Network - reward evidence, evaluation, and dynamics
8. Salience Network - salience evaluation and relevance
9. Sensorimotor Network - sensorimotor coupling and action preparation
10. Workspace Network - shared cognitive access and capacity

COORDINATION NETWORK RESPONSIBILITIES
-----------------------------------
- Network identity registration
- Network capability projections
- Network requirement projections
- Network constraint projections
- Network readiness projections
- Network availability projections
- Network participation state
- Coordination cycles
- Coordination requests
- Coordination plans
- Coordination dependencies
- Coordination constraints
- Coordination transitions
- Interaction relationships
- Request correlation
- Response correlation
- Conflict representation
- Compatibility validation
- Coordination findings
- Coordination limitations
- Coordination trace

COORDINATION NETWORK NON-OWNERSHIP
----------------------------------
The Coordination Network does NOT own:
- Coordinated network internals
- Network-specific semantic state
- Network-specific policies
- Cognitive content (predictions, reward, salience, etc.)
- Executive decisions
- Workspace admission
- Motor commands
- Network lifecycle implementation
- Process/thread scheduling
- Transport/serialization
- Service discovery
- Telemetry/diagnostics

ARCHITECTURAL PRINCIPLES
========================
1. Coordinated networks remain semantic peers (no hierarchy)
2. Coordination owns coherence, not cognition
3. All network inputs are immutable projections
4. Coordinated network internals remain inaccessible
5. Membership is explicit (no reflection/discovery)
6. Capabilities are declarative (not executable)
7. Requirements are explicit and typed
8. Constraints are typed
9. Readiness differs from availability
10. Coordination cycles remain bounded
11. Plans remain declarative
12. Cognitive conflicts remain unresolved by coordination
13. Executive remains external to coordination
14. Workspace remains external to coordination
15. No network-specific authority is absorbed

DETERMINISM INVARIANTS
======================
- Equivalent requests + projections = equivalent Coordination States
- Graph ordering is deterministic (stable semantic keys)
- Projection ordering is deterministic
- Parallel execution does not alter semantic output
- Randomness is prohibited
- Wall-clock acquisition is prohibited

ARCHITECTURAL LAWS
==================
COORD-LAW-001: Exactly one canonical Coordination Network exists per cycle
COORD-LAW-002: Exactly one canonical Coordination State exists per cycle
COORD-LAW-003: Coordination consumes immutable Network Projections only
COORD-LAW-004: Coordination never mutates participating networks
COORD-LAW-005: Coordination preserves semantic ownership
COORD-LAW-006: Coordination preserves provenance
COORD-LAW-007: Coordination preserves revision lineage
COORD-LAW-008: Coordination remains deterministic
COORD-LAW-009: Coordination remains side-effect free
COORD-LAW-010: Coordination exposes structure rather than behavior

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

__all__ = [
    # Core enums - Phase 4.11.1
    "CoordinatedNetworkKind",
    "NetworkCoordinationStatus",
    "NetworkReadinessState",
    "NetworkAvailabilityState",
    "ParticipationRole",
    "DependencyKind",
    "ConstraintKind",
    "ConflictKind",
    "CompatibilityStatus",
    "FindingCode",
    "LimitationCode",
    
    # Identity models - Phase 4.11.1
    "NetworkIdentity",
    "CoordinationRequestIdentity",
    "CoordinationCycleIdentity",
    "CoordinationStateIdentity",
    
    # Membership - Phase 4.11.1
    "CoordinationMembership",
    
    # Base projection contract - Phase 4.11.1
    "NetworkProjection",
    
    # Capability and requirement - Phase 4.11.1
    "NetworkCapability",
    "NetworkRequirement",
    "RequirementSatisfaction",
    
    # Constraint and dependency - Phase 4.11.1
    "CoordinationConstraint",
    "CoordinationDependency",
    
    # Transition and interaction - Phase 4.11.1
    "TransitionIntention",
    "NetworkInteraction",
    
    # Evaluation models - Phase 4.11.1
    "NetworkReadiness",
    "NetworkAvailability",
    "NetworkParticipation",
    
    # Graph types (imported from graph module)
    # "CoordinationDependencyGraph",  # Defined in coordination.graph
    # "CoordinationConstraintGraph",  # Defined in coordination.graph
    # "CoordinationTransitionGraph",  # Defined in coordination.graph
    # "CoordinationInteractionGraph",  # Defined in coordination.graph
    
    # Conflict and compatibility - Phase 4.11.1
    "CoordinationConflict",
    "CoordinationCompatibility",
    
    # Policy and plan - Phase 4.11.1
    "CoordinationPolicy",
    "CoordinationPlan",
    
    # Cycle and state - Phase 4.11.1
    "CoordinationCycle",
    "CoordinationState",
    
    # Results and findings - Phase 4.11.1
    "CoordinationResult",
    "CoordinationFinding",
    "CoordinationLimitation",
    "CoordinationTraceEvent",
    
    # Confidence and uncertainty - Phase 4.11.1
    "CoordinationConfidence",
    "CoordinationUncertainty",
    
    # Main engine - Phase 4.11.1
    "CoordinationNetwork",
    
    # Projection utility function - Phase 4.11.1
    "get_projection_for_kind",
    
    # =============================================================================
    # TEMPORAL COORDINATION MODELS - Phase 4.11.2
    # =============================================================================
    
    # Epoch models
    "CoordinationEpochStatus",
    "CoordinationEpochIdentity",
    "CoordinationEpoch",
    "CoordinationDomain",
    "EpochSemanticFingerprint",
    
    # Lifecycle models
    "CoordinationCycleLifecycleStatus",
    "CoordinationCycleKind",
    "LifecycleTransitionValidator",
    "CoordinationCycle",
    
    # Publication models
    "PublicationWindowStatus",
    "ProjectionPublicationIntention",
    "ProjectionAcceptanceStatus",
    "ProjectionAcceptance",
    "ProjectionPublicationWindow",
    "NetworkProjectionPublication",
    
    # Synchronization models
    "SynchronizationBarrierStatus",
    "SnapshotConsistencyStatus",
    "ProjectionFreshnessStatus",
    "CoordinationSynchronizationBarrier",
    "CoordinationSnapshot",
    "ProjectionFreshness",
    "SynchronizationBarrierEvaluator",
    
    # Incremental coordination models
    "CoordinationConvergenceStatus",
    "CoordinationDelta",
    "SemanticFingerprint",
    "CoordinationChangeDetector",
    "CoordinationConvergence",
    "CoordinationConvergenceEvaluator",
    "IncrementalInvalidation",
    "IncrementalGraphRebuilder",
    
    # Consumer models
    "CoordinationStateViewStatus",
    "CoordinationStateConsumptionRequest",
    "CoordinationStateView",
    "CoordinationStatePublication",
    "StatePublicationStatus",
    "CoordinationStateViewBuilder",
    
    # Validation models
    "ValidationFinding",
    "ValidationResult",
    "EpochValidator",
    "CycleValidator",
    "PublicationWindowValidator",
    "BarrierValidator",
    "ConvergenceValidator",
    "StateValidator",
    
    # =============================================================================
    # COGNITIVE COORDINATION PROTOCOL (CCP) - Phase 4.11.5
    # =============================================================================
    
    # CCP Enums
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
    
    # CCP Core Models
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
    "CCPNegotiationRequest",
    "CCPNegotiationResponse",
    "CCPNegotiationResult",
    "CCPSynchronizationRequest",
    "CCPSyncStatus",  # renamed to avoid conflict
    "CCPBarrierStatus",
    "CCPTransitionIntention",
    "CCPTransitionStatus",
    "CCPConflictReport",
    "CCPFailureReport",
    "CCPRecoveryRequest",
    "CCPRecoveryProposal",
    "CCPRecoveryResult",
    "CCPLifecycleNotice",
    "CCPHeartbeatProjection",
    
    # CCP Protocol
    "CCPProtocol",
    "CCPProcessingRequest",
    "CCPProcessingResult",
    "CCPMessageValidator",
    "CCPPublicationValidator",
    "CCPSubscriptionMatcher",
    "CCPCompatibilityChecker",
    
    # CCP Serialization
    "CCPSerializer",
    "CCPMessageSerializer",
    "CCPSerializationValidator",
    
    # =============================================================================
    # COGNITIVE EVENT MODEL (CEM) - Phase 4.11.6
    # =============================================================================
    
    # Event Enumerations
    "CognitiveEventKind",
    "CognitiveEventStatus",
    "EventImportance",
    "EventDurationKind",
    
    # Identity Models
    "SemanticTimeReference",
    "CognitiveEventIdentity",
    "CognitiveEventRevisionIdentity",
    "CognitiveEventStreamIdentity",
    "CognitiveTimelineIdentity",
    "CognitiveEpisodeIdentity",
    "EventAggregationIdentity",
    "EventCorrelationIdentity",
    
    # Revision Models
    "RevisionKind",
    "CognitiveEventRevision",
    
    # Duration Models  
    "EventDuration",
    "EventIntervalReference",
    
    # Event Model
    "CognitiveEvent",
    
    # Stream Models
    "CognitiveEventStream",
    "GlobalCognitiveEventStream",
    
    # Timeline Models
    "CognitiveTimelineScope",
    "CognitiveTimelineIdentity",
    "CognitiveTimeline",
    
    # Episode Models
    "CognitiveEpisodeKind",
    "CognitiveEpisodeIdentity",
    "CognitiveEpisode",
    
    # Aggregation Models
    "EventAggregationIdentity",
    "EventAggregation",
    
    # Correlation/Causation Models
    "EventCorrelationIdentity",
    "EventCorrelation",
    "EventCausation",
    
    # Lineage Models
    "EventLineage",
    
    # Index Types
    "EventIndexKey",
    
    # Replay Models
    "ReplayScope",
    "CognitiveReplayRequest",
    "CognitiveReplayResult",
    
    # Query Models
    "CognitiveEventQueryKind",
    "CognitiveEventQuery",
    "CognitiveEventQueryResult",
    
    # Validation Models
    "ValidationFindingCode",
    "ValidationFinding",
    "ValidationResult",
    "CognitiveEventValidationEngine",
    
    # Serialization Models
    "CognitiveEventSerializer",
    
    # Engine Models
    "CognitiveEventEngine",
    "CognitiveEventRequest",
    "CognitiveEventResult",
]

# Core enums - defined first to enable cross-references
from .enums import (
    CoordinatedNetworkKind,
    NetworkCoordinationStatus,
    NetworkReadinessState,
    NetworkAvailabilityState,
    ParticipationRole,
    DependencyKind,
    ConstraintKind,
    ConflictKind,
    CompatibilityStatus,
    FindingCode,
    LimitationCode,
)

# Import SemanticTimeReference from enums
from .enums import SemanticTimeReference

# Exceptions
from .exceptions import (
    CoordinationError,
    MembershipError,
    ProjectionError,
    ConstraintError,
    DependencyError,
    ValidationFailure,
)

# Models (core contracts)
from .models import (
    # Identity models
    NetworkIdentity,
    CoordinationRequestIdentity,
    CoordinationCycleIdentity,
    CoordinationStateIdentity,
    
    # Membership
    CoordinationMembership,
    
    # Base projection contract
    NetworkProjection,
    
    # Network-specific projections
    AlertingNetworkProjection,
    DefaultNetworkProjection,
    ExecutiveNetworkProjection,
    FocusingNetworkProjection,
    OrientedNetworkProjection,
    PredictiveNetworkProjection,
    RewardNetworkProjection,
    SalienceNetworkProjection,
    SensorimotorNetworkProjection,
    WorkspaceNetworkProjection,
)

# Capability and requirement models (to be implemented)
from .models import (
    NetworkCapability as _NetworkCapability,
    NetworkRequirement as _NetworkRequirement,
    RequirementSatisfaction as _RequirementSatisfaction,
)

# Constraint and dependency models (to be implemented)  
from .models import (
    CoordinationConstraint as _CoordinationConstraint,
    CoordinationDependency as _CoordinationDependency,
)

# Transition and interaction models (to be implemented)
from .models import (
    TransitionIntention as _TransitionIntention,
    NetworkInteraction as _NetworkInteraction,
)

# Evaluation models (to be implemented)
from .models import (
    NetworkReadiness as _NetworkReadiness,
    NetworkAvailability as _NetworkAvailability,
    NetworkParticipation as _NetworkParticipation,
)

# Conflict and compatibility models (to be implemented)
from .models import (
    CoordinationConflict as _CoordinationConflict,
    CoordinationCompatibility as _CoordinationCompatibility,
)

# Policy and plan models (to be implemented)
from .models import (
    CoordinationPolicy as _CoordinationPolicy,
    CoordinationPlan as _CoordinationPlan,
)

# Cycle and state models (to be implemented)
from .models import (
    CoordinationCycle as _CoordinationCycle,
    CoordinationState as _CoordinationState,
)

# Results and findings models (to be implemented)
from .models import (
    CoordinationResult as _CoordinationResult,
    CoordinationFinding as _CoordinationFinding,
    CoordinationLimitation as _CoordinationLimitation,
    CoordinationTraceEvent as _CoordinationTraceEvent,
)

# Confidence and uncertainty models (to be implemented)
from .models import (
    CoordinationConfidence as _CoordinationConfidence,
    CoordinationUncertainty as _CoordinationUncertainty,
)

# Main engine
from .engine import CoordinationNetwork

# Projection utility function
from .models import get_projection_for_kind

# =============================================================================
# CROSS-NETWORK DEPENDENCY RESOLUTION AND COORDINATION PLANNING - Phase 4.11.3
# =============================================================================

from .planning import (
    # Enums
    ProviderPriority,
    ProviderCompatibilityStatus,
    ProviderSelectionMode,
    RequirementSatisfactionStatus,
    CoordinationDependencyKind,
    SynchronizationGroupKind,
    DeadlockKind,
    DependencyPathKind,
    CycleClassification,
    
    # Core models
    NormalizedRequirement,
    NormalizedCapability,
    CapabilityProviderCandidate,
    ProviderCompatibility,
    CapabilityProviderSelection,
    ResolvedRequirement,
    NormalizedCoordinationDependency,
    CoordinationDependencyPath,
    CoordinationDependencyClosure,
    CoordinationSynchronizationGroup,
    CoordinationDependencyLayer,
    CoordinationFallbackPath,
    CoordinationRecoveryPath,
    CoordinationDeadlock,
    CoordinationPlanCandidate,
    CoordinationPlanAlternative,
    CoordinationPlan,
    DependencyResolutionState,
    CoordinationPlanningRequest,
    CoordinationPlanningResult,
    CoordinationPlanningPolicy,
)

from .planning_components import (
    # Components
    RequirementNormalizer,
    CapabilityNormalizer,
    CapabilityRequirementMatcher,
    ProviderSelector,
    DependencyNormalizer,
    DependencyClosureBuilder,
    SynchronizationGroupBuilder,
    DependencyLayerBuilder,
    CoordinationDeadlockDetector,
    FallbackPathBuilder,
    CoordinationPlanningEngine,
)

# =============================================================================
# TEMPORAL COORDINATION IMPORTS - Phase 4.11.2
# =============================================================================

# Epoch models
from .temporal.epoch import (
    CoordinationEpochStatus,
    CoordinationEpochIdentity,
    CoordinationEpoch,
    CoordinationDomain,
    EpochSemanticFingerprint,
)

# Lifecycle models - note: lifecycle module uses TemporalCoordinationCycle to avoid conflict
# with models.py CoordinationCycle. For now, we only import enums and validators.
from .temporal.lifecycle import (
    CoordinationCycleLifecycleStatus,
    CoordinationCycleKind,
    LifecycleTransitionValidator,
    TemporalCoordinationCycleIdentity,  # Identity from lifecycle module (not used by models.py)
)

# Models.py provides the main CoordinationCycle - keep for backward compatibility

# Publication models
from .temporal.publication import (
    PublicationWindowStatus,
    ProjectionPublicationIntention,
    ProjectionAcceptanceStatus,
    ProjectionAcceptance,
    ProjectionPublicationWindow,
    NetworkProjectionPublication,
)

# Synchronization models
from .temporal.synchronization import (
    SynchronizationBarrierStatus,
    SnapshotConsistencyStatus,
    ProjectionFreshnessStatus,
    CoordinationSynchronizationBarrier,
    CoordinationSnapshot,
    ProjectionFreshness,
    SynchronizationBarrierEvaluator,
)

# Incremental coordination models
from .temporal.incremental import (
    CoordinationConvergenceStatus,
    CoordinationDelta,
    SemanticFingerprint,
    CoordinationChangeDetector,
    CoordinationConvergence,
    CoordinationConvergenceEvaluator,
    IncrementalInvalidation,
    IncrementalGraphRebuilder,
)

# Consumer models
from .temporal.consumer import (
    CoordinationStateViewStatus,
    CoordinationStateConsumptionRequest,
    CoordinationStateView,
    CoordinationStatePublication,
    StatePublicationStatus,
    CoordinationStateViewBuilder,
)

# =============================================================================
# COGNITIVE COORDINATION PROTOCOL (CCP) - Phase 4.11.5
# =============================================================================

from .protocol import (
    CCPProtocolIdentity,
    CCPVersion,
    CCPMessage,
    CCPPublisherReference,
    CCPConsumerReference,
    CCPMessageVisibility,  # visibility scope model
    CCPPublication,
    CCPSubscription,
    CCPAcknowledgement,
    CCPMessageAcceptance,
    CCPMessageRejection,
    CCPMessageDeferral,
    CCPCapabilityAdvertisement,
    CCPRequirementDeclaration,
    CCPNegotiationRequest,
    CCPNegotiationResponse,
    CCPNegotiationResult,
    CCPSynchronizationRequest,
    CCPSyncStatus,  # renamed to avoid conflict
    CCPBarrierStatus,
    CCPTransitionIntention,
    CCPTransitionStatus,
    CCPConflictReport,
    CCPFailureReport,
    CCPRecoveryRequest,
    CCPRecoveryProposal,
    CCPRecoveryResult,
    CCPLifecycleNotice,
    CCPHeartbeatProjection,
    CCPProtocol,
    CCPProcessingRequest,
    CCPProcessingResult,
    CCPMessageValidator,
    CCPPublicationValidator,
    CCPSubscriptionMatcher,
    CCPCompatibilityChecker,
)

from .protocol import (
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

from .protocol.serialization import (
    CCPSerializer,
    CCPMessageSerializer,
    CCPSerializationValidator,
)

# =============================================================================
# COGNITIVE EVENT MODEL (CEM) - Phase 4.11.6
# =============================================================================

# =============================================================================
# COGNITIVE ORCHESTRATION ENGINE (COE) - Phase 4.11.7
# =============================================================================

from .orchestration import (
    # Enums
    CycleKind,
    StageKind,
    ParticipantRole,
    OrchestrationDependencyKind,
    SynchronizationPolicy,
    ResourceBudgetPolicy,
    CompletionPolicy,
    ExecutionPolicy,
    Status,
    
    # Identity
    OrchestrationIdentity,
    CycleIdentity,
    StageIdentity,
    ParticipantIdentity,
    
    # Core models
    CognitiveCycle,
    CycleParticipant,
    ParticipantStatus,
    CognitiveExecutionStage,
    StageStatus,
    ExecutionDependencyGraph,
    DependencyEdge,
    ParallelExecutionGroup,
    SynchronizationBarrier,
    ResourceAllocation,
    
    # Degraded mode and recovery
    DegradedOrchestrationMode,
    RecoveryStrategy,
    RecoveryCoordination,
    
    # Policies
    ExecutionPolicy as OrchestrationExecutionPolicy,
    CompletionPolicySpec,
    
    # Plan and request/result
    CognitiveOrchestrationPlan,
    PlanStatus,
    CognitiveOrchestrationRequest,
    CognitiveOrchestrationResult,
    
    # Validation
    OrchestrationValidator,
    ValidationFinding,
    ValidationResult,
    
    # Query
    OrchestrationQuery,
    QueryKind,
    
    # Serialization
    OrchestrationSerializer,
    PlanSerializer,
)

# =============================================================================
# COGNITIVE EVENT MODEL (CEM) - Phase 4.11.6
# =============================================================================

from .events import (
    # Enumerations
    CognitiveEventKind,
    CognitiveEventStatus,
    EventImportance,
    EventDurationKind,
    
    # Identity Models
    SemanticTimeReference,
    CognitiveEventIdentity,
    CognitiveEventRevisionIdentity,
    CognitiveEventStreamIdentity,
    CognitiveTimelineIdentity,
    CognitiveEpisodeIdentity,
    EventAggregationIdentity,
    EventCorrelationIdentity,
    
    # Revision Models
    RevisionKind,
    CognitiveEventRevision,
    
    # Duration Models
    EventDuration,
    EventIntervalReference,
    
    # Event Model
    CognitiveEvent,
    
    # Stream Models
    CognitiveEventStream,
    GlobalCognitiveEventStream,
    
    # Timeline Models
    CognitiveTimelineScope,
    CognitiveTimelineIdentity,
    CognitiveTimeline,
    
    # Episode Models
    CognitiveEpisodeKind,
    CognitiveEpisodeIdentity,
    CognitiveEpisode,
    
    # Aggregation Models
    EventAggregationIdentity,
    EventAggregation,
    
    # Correlation/Causation Models
    EventCorrelationIdentity,
    EventCorrelation,
    EventCausation,
    
    # Lineage Models
    EventLineage,
    
    # Index Types
    EventIndexKey,
    
    # Replay Models
    ReplayScope,
    CognitiveReplayRequest,
    CognitiveReplayResult,
    
    # Query Models
    CognitiveEventQueryKind,
    CognitiveEventQuery,
    CognitiveEventQueryResult,
    
    # Validation Models
    ValidationFindingCode,
    ValidationFinding,
    ValidationResult,
    CognitiveEventValidationEngine,
    
    # Serialization Models
    CognitiveEventSerializer,
    
    # Engine Models
    CognitiveEventEngine,
    CognitiveEventRequest,
    CognitiveEventResult,
)

# Validation models
from .temporal.validation import (
    ValidationFinding,
    ValidationResult,
    EpochValidator,
    CycleValidator,
    PublicationWindowValidator,
    BarrierValidator,
    ConvergenceValidator,
    StateValidator,
)

# =============================================================================
# GLOBAL COORDINATION GRAPH - Phase 4.11.4
# =============================================================================

from .global_graph import (
    # Enums
    CoordinationGraphNodeKind,
    CoordinationGraphEdgeKind,
    CoordinationNodeStatus,
    CoordinationEdgeStatus,
    GraphRevisionKind,
    ComponentKind,
    GraphPartitionKind,
    GraphDomainKind,
    SemanticScope,
    GraphConstructionPolicy,
    
    # Core models
    GlobalCoordinationGraphIdentity,
    GlobalCoordinationGraphRevisionIdentity,
    GlobalCoordinationGraph,
    CoordinationGraphNode,
    CoordinationGraphEdge,
    CoordinationGraphPartition,
    CoordinationGraphDomain,
    CoordinationGraphComponent,
    GlobalCoordinationGraphIndexes,
    
    # Delta models
    GlobalCoordinationGraphDelta,
    GraphRevisionBuildResult,
    IndexBuildResult,
)
