# Execution Reasoning - Phase 7.21
# =================================

"""
Execution Reasoning provides Gordon's behavior orchestration engine.

This subsystem transforms validated execution plans into coordinated,
observable operational behavior.

Execution components perform concrete actions.
Monitoring observes outcomes.
Evaluation assesses results.

Execution Reasoning governs:
    - When actions are performed
    - How actions proceed safely and adaptively
    - Execution sequencing
    - Execution coordination
    - Execution authorization
    - Resource synchronization
    - Adaptive execution
    - Rollback initiation

Architectural Position:
    Decision → Planning → Execution Reasoning → Execution Commands → World

Implementation SCAFFOLD:
    cognition/
    └── reasoning/
        └── execution/
            ├── shared/          # Canonical contracts and data models
            ├── sequencing/      # Command ordering and parallelism
            ├── coordination/    # Worker and resource orchestration
            ├── validation/      # Execution validation
            ├── governance/      # Governance evaluation
            └── diagnostics/     # Diagnostic tools

Execution Reasoning should become Gordon's **transactional execution architecture**.

Every execution graph should behave like a cognitive transaction with:
    - Atomic execution regions
    - Checkpointing
    - Compensation actions
    - Partial rollback
    - Distributed synchronization
    - Resumable execution
    - Deterministic replay

Combined with Planning, Monitoring, Scheduling, Evaluation and Governance,
Execution Reasoning provides Gordon with reliable, auditable and adaptive
behavior while preserving complete traceability of every executed operation.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.descriptor import (
    ExecutionDescriptor,
    ExecutionSessionIdentity,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.execution_set import (
    ExecutionCommand,
    ExecutionSet,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.orchestration import (
    ExecutionOrchestration,
    OrchestrationStrategy,
    ExecutionGraphState,
    ExecutionCommandGroup,
    OrchestrationTrace,
    OrchestrationStep,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.authorization import (
    ExecutionAuthorization,
    AuthorizationPolicy,
    AuthorizationState,
    AuthorizationTrace,
    AuthorizationStep,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.execution.shared.synchronization import (
    SynchronizationPoint,
    SynchronizationPolicy,
    SynchronizationState,
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
    ValidationStep,
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
    # Shared
    "ExecutionDescriptor",
    "ExecutionSessionIdentity",
    "ExecutionCommand",
    "ExecutionSet",
    # Orchestration
    "ExecutionOrchestration",
    "OrchestrationStrategy",
    "ExecutionGraphState",
    "ExecutionCommandGroup",
    "OrchestrationTrace",
    "OrchestrationStep",
    # Authorization
    "ExecutionAuthorization",
    "AuthorizationPolicy",
    "AuthorizationState",
    "AuthorizationTrace",
    "AuthorizationStep",
    # Synchronization
    "SynchronizationPoint",
    "SynchronizationPolicy",
    "SynchronizationState",
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
    "ValidationStep",
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