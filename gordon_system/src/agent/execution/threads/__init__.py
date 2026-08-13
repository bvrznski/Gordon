# ExecutionThread Architecture Package
# ====================================
#
# PHASE 3.10.7 - Canonical ExecutionThread Architecture
# PHASE 3.10.9 - Concrete execution taxonomy implementation
#
# An ExecutionThread is NOT:
#     - An operating-system thread, coroutine, task, worker, process, or scheduler entry
#     - A runtime execution unit (that belongs to Core)
#     - A scheduling entity (that belongs to Core)
#
# An ExecutionThread IS:
#     - The semantic owner of one continuous agent activity
#     - Persistent identity across multiple finite executions  
#     - Purpose-driven: maintains purpose while objectives may evolve
#     - Lifecycle-managed through controlled delta application
#
# Ownership Model:
#     Core:  runtime scheduling, lifecycle state transitions, resource allocation
#     ExecutionThread: semantic continuity, identity, purpose, objectives, completion intent

from .identity import (
    ThreadId,
    ThreadName,
    ThreadMetadata,
    ThreadDescriptor,
)

from .lifecycle import (
    ThreadLifecycleState,
    ThreadLifecycleTransitionGraph, 
    ThreadLifecycleReason,
    ThreadLifecycleSnapshot,
    ThreadLifecycleTransitionRequest,
    ThreadLifecycleTransitionResult,
)

from .state import (
    ThreadSemanticState,
    ThreadContext,
    BehavioralMode,
    ThreadObjective,
)

from .delta import (
    DeltaValidationResult,
    ThreadSemanticDelta,
    ThreadDeltaBatch, 
    DeltaApplicationResult,
    ThreadDeltaValidator,
)

from .relationships import (
    RelationshipKind,
    ThreadRelationship,
    ParentChildRelationship,
    ThreadRelationshipGraph,
    ThreadRelationshipSnapshot,
)

from .snapshot import (
    ThreadSnapshot as SnapshotClass,
)

from .entity import (
    ExecutionThread,
    ExecutionThreadSnapshot,
    # Backward compatibility aliases (deprecated, will be removed in future)
    Thread as ExecutionThreadAlias,
    ThreadSnapshot as ExecutionThreadSnapshotAlias,
)

# =============================================================================
# PHASE 3.10.9 - Concrete Thread Types
# =============================================================================

from .concrete import (
    # Conversation thread types
    ConversationPurpose,
    ConversationParticipant,
    ConversationState,
    ConversationThread,
    ConversationSnapshot,
    
    # Task thread types
    TaskStatus,
    TaskConstraints,
    TaskPlan,
    TaskProgress,
    TaskState,
    TaskThread,
    TaskSnapshot,
    
    # Monitoring thread types
    ObservationType,
    MonitoringTarget,
    Baseline,
    MonitoringState,
    MonitoringThread,
    MonitoringSnapshot,
    
    # Internal thread types
    InternalPurpose,
    InternalContext,
    InternalState,
    InternalThread,
    InternalSnapshot,
)

__all__ = [
    # Identity
    "ThreadId",           # Canonical semantic identity for ExecutionThread
    "ThreadName",
    "ThreadMetadata", 
    "ThreadDescriptor",
    
    # Lifecycle (semantic intent)
    "ThreadLifecycleState",
    "ThreadLifecycleTransitionGraph", 
    "ThreadLifecycleReason",
    "ThreadLifecycleSnapshot",
    "ThreadLifecycleTransitionRequest",
    "ThreadLifecycleTransitionResult",
    
    # Semantic state
    "ThreadSemanticState",
    "ThreadContext",
    "BehavioralMode",
    "ThreadObjective",
    
    # Delta (controlled state change)
    "DeltaValidationResult",
    "ThreadSemanticDelta",
    "ThreadDeltaBatch", 
    "DeltaApplicationResult",
    "ThreadDeltaValidator",
    
    # Relationships
    "RelationshipKind",
    "ThreadRelationship",
    "ParentChildRelationship",
    "ThreadRelationshipGraph",
    "ThreadRelationshipSnapshot",
    
    # Snapshots (immutable views)
    "SnapshotClass",
    
    # Canonical ExecutionThread entity (IMMUTABLE!)
    "ExecutionThread",           # Primary canonical name
    "ExecutionThreadSnapshot",   # Read-only snapshot for Loop evaluation
    
    # Backward compatibility aliases (deprecated, will be removed in future)
    "ExecutionThreadAlias",      # Alias for Thread → use ExecutionThread instead
    "ExecutionThreadSnapshotAlias",
    
    # =============================================================================
    # PHASE 3.10.9 - Concrete Thread Types
    # =============================================================================
    
    # Conversation thread types
    "ConversationPurpose",
    "ConversationParticipant",
    "ConversationState",
    "ConversationThread",
    "ConversationSnapshot",
    
    # Task thread types
    "TaskStatus",
    "TaskConstraints",
    "TaskPlan",
    "TaskProgress",
    "TaskState",
    "TaskThread",
    "TaskSnapshot",
    
    # Monitoring thread types
    "ObservationType",
    "MonitoringTarget",
    "Baseline",
    "MonitoringState",
    "MonitoringThread",
    "MonitoringSnapshot",
    
    # Internal thread types
    "InternalPurpose",
    "InternalContext",
    "InternalState",
    "InternalThread",
    "InternalSnapshot",
]

# Backward compatibility: Thread and ThreadSnapshot are now aliased to ExecutionThread
Thread = ExecutionThread
ThreadSnapshot = ExecutionThreadSnapshot