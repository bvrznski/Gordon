# Execution Reasoning Shared Components - Phase 7.21
# =====================================================

"""
Shared components for the Execution Reasoning subsystem (Phase 7.21).

This package contains core execution contracts including:
    - Execution descriptors and identities
    - Execution sets and orchestration
    - Authorization, synchronization, adaptation models
    - Rollback management, validation, governance
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.descriptor import (
    ExecutionDescriptor,
    ExecutionSessionIdentity,
    ExecutionMode,
    ExecutionLifecycle,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.execution_set import (
    ExecutionCommand,
    ExecutionSet,
    CommandConstruction,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.orchestration import (
    ExecutionOrchestration,
    OrchestrationStrategy,
    ExecutionGraphState,
    OrchestrationTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.authorization import (
    ExecutionAuthorization,
    AuthorizationPolicy,
    AuthorizationState,
    AuthorizationResult,
    AuthorizationTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.synchronization import (
    SynchronizationPoint,
    SynchronizationPolicy,
    OrderingConstraints,
    SynchronizationGraph,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.adaptation import (
    ExecutionAdaptationPipeline,
    AdaptationTrigger,
    AdaptationStrategy,
    AdaptedExecutionState,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.rollback import (
    RollbackManagement,
    RollbackScope,
    RecoveryCheckpoint,
    RollbackPlan,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.validation import (
    ExecutionValidation,
    ValidationFindingKind,
    ValidationFinding,
    ValidationTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.failure import (
    ExecutionFailure,
    FailureKind,
    FailureTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.governance import (
    ExecutionGovernance,
    GovernanceFindingKind,
    GovernanceFinding,
    ExecutionSessionGovernance,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.health import (
    ExecutionHealth,
    HealthMetricsSnapshot,
    HealthAlert,
)

__all__ = [
    # Descriptors
    "ExecutionDescriptor",
    "ExecutionSessionIdentity",
    "ExecutionMode",
    "ExecutionLifecycle",
    
    # Execution Set
    "ExecutionCommand",
    "ExecutionSet",
    "CommandConstruction",
    
    # Orchestration
    "ExecutionOrchestration",
    "OrchestrationStrategy",
    "ExecutionGraphState",
    "OrchestrationTrace",
    
    # Authorization
    "ExecutionAuthorization",
    "AuthorizationPolicy",
    "AuthorizationState",
    "AuthorizationResult",
    "AuthorizationTrace",
    
    # Synchronization
    "SynchronizationPoint",
    "SynchronizationPolicy",
    "OrderingConstraints",
    "SynchronizationGraph",
    
    # Adaptation
    "ExecutionAdaptationPipeline",
    "AdaptationTrigger",
    "AdaptationStrategy",
    "AdaptedExecutionState",
    
    # Rollback
    "RollbackManagement",
    "RollbackScope",
    "RecoveryCheckpoint",
    "RollbackPlan",
    
    # Validation
    "ExecutionValidation",
    "ValidationFindingKind",
    "ValidationFinding",
    "ValidationTrace",
    
    # Failure
    "ExecutionFailure",
    "FailureKind",
    "FailureTrace",
    
    # Governance
    "ExecutionGovernance",
    "GovernanceFindingKind",
    "GovernanceFinding",
    "ExecutionSessionGovernance",
    
    # Health
    "ExecutionHealth",
    "HealthMetricsSnapshot",
    "HealthAlert",
]