# Planning Reasoning - Phase 7.20
# ================================

"""
Planning Reasoning for the Gordon Cognitive Architecture.

Planning Reasoning is Gordon's operational synthesis engine.
It transforms explicit commitments into executable operational structures
without performing execution itself.

Architecture Position:
    Decision → Planning Reasoning → Scheduler → Execution
    
Canonical Contracts:
    - shared/: Contract definitions (descriptors, plans, tasks, dependencies,
              resources, contingencies, refinement, validation, failure,
              governance, health)
    
Planning Laws:
    PLANNING-LAW-001: Every Planning Session has one immutable Semantic Identity
    PLANNING-LAW-002: Planning Reasoning executes over one explicit Plan Set
    PLANNING-LAW-003: Every Execution Plan references one explicit originating Decision
    PLANNING-LAW-004: Planning Reasoning preserves provenance
    PLANNING-LAW-005: Planning Reasoning preserves reasoning lineage
    PLANNING-LAW-006: Planning Reasoning remains independently inspectable
    PLANNING-LAW-007: Planning Reasoning is deterministic given identical inputs
    PLANNING-LAW-008: Completed Planning Sessions remain immutable

Anti-Patterns to Avoid:
    - Execute plans during construction
    - Omit dependency graphs
    - Ignore resource constraints
    - Produce hidden task ordering
    - Discard contingency plans
    - Overwrite historical plans
    - Bypass validation or governance
    - Lose provenance
"""

# Shared contracts (canonical Planning contracts)
from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.descriptor import (
    PlanningDescriptor,
    PlanningSessionIdentity,
    PlanningMode,
    PlanningLifecycle,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.plan_set import (
    ExecutionPlan,
    PlanSet,
    PlanConstruction,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.tasks import (
    PlannedTask,
    TaskKind,
    TaskState,
    TaskManagement,
    TaskDecomposition,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.dependencies import (
    TaskDependency,
    DependencyKind,
    DependencyGraphState,
    DependencyGraph,
    DependencyAnalysis,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.resources import (
    ResourceAllocation,
    ResourceType,
    AllocationPolicy,
    ResourcePlanning,
    ResourceAvailability,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.contingencies import (
    ContingencyPlan,
    ContingencyKind,
    ContingencyState,
    ContingencyManagement,
    RecoveryTrigger,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.refinement import (
    PlanningRefinement,
    PlanHistory,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.validation import (
    PlanningValidation,
    ValidationFindingKind,
    ValidationFinding,
    ValidationTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.failure import (
    PlanningFailure,
    FailureKind,
    FailureTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.governance import (
    PlanningGovernance,
    GovernanceFindingKind,
    GovernanceFinding,
    PlanningSessionGovernance,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.health import (
    PlanningHealth,
    HealthMetricsSnapshot,
    HealthAlert,
)

__all__ = [
    # Shared
    "PlanningDescriptor",
    "PlanningSessionIdentity",
    "PlanningMode",
    "PlanningLifecycle",
    
    # Plan Set
    "ExecutionPlan",
    "PlanSet",
    "PlanConstruction",
    
    # Tasks
    "PlannedTask",
    "TaskKind",
    "TaskState",
    "TaskManagement",
    "TaskDecomposition",
    
    # Dependencies
    "TaskDependency",
    "DependencyKind",
    "DependencyGraphState",
    "DependencyGraph",
    "DependencyAnalysis",
    
    # Resources
    "ResourceAllocation",
    "ResourceType",
    "AllocationPolicy",
    "ResourcePlanning",
    "ResourceAvailability",
    
    # Contingencies
    "ContingencyPlan",
    "ContingencyKind",
    "ContingencyState",
    "ContingencyManagement",
    "RecoveryTrigger",
    
    # Refinement
    "PlanningRefinement",
    "PlanHistory",
    
    # Validation
    "PlanningValidation",
    "ValidationFindingKind",
    "ValidationFinding",
    "ValidationTrace",
    
    # Failure
    "PlanningFailure",
    "FailureKind",
    "FailureTrace",
    
    # Governance
    "PlanningGovernance",
    "GovernanceFindingKind",
    "GovernanceFinding",
    "PlanningSessionGovernance",
    
    # Health
    "PlanningHealth",
    "HealthMetricsSnapshot",
    "HealthAlert",
]