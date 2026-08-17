# Meta-Reasoning Shared Components - Phase 7.13
# ===============================================

"""
Shared contracts and data structures for Meta-Reasoning.

This module provides the canonical data models governing meta-reasoning
orchestration, strategy selection, monitoring, validation, governance,
and diagnostics.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.descriptor import (
    MetaReasoningDescriptor,
    MetaReasoningState,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.reasoner_set import (
    ReasonerSet,
    ReasonerCapability,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.strategy_selection import (
    StrategySelection,
    StrategyKind,
    SelectionRationale,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.orchestration import (
    ReasoningOrchestration,
    ExecutionGraph,
    SynchronizationPoint,
    OrchestrationPolicy,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.resources import (
    ReasoningResourceAllocation,
    ResourceKind,
    AllocationConstraints,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.monitoring import (
    ReasoningMonitoring,
    MonitoringMetric,
    MonitoringEvent,
    MonitorKind,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.adaptation import (
    AdaptiveOrchestration,
    StrategyAdaptation,
    AdaptationTrigger,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.refinement import (
    MetaReasoningRefinement,
    PolicyChange,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.validation import (
    MetaReasoningValidation,
    ValidationStatus,
    ValidationResult,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.failure import (
    MetaReasoningFailure,
    FailureKind,
    RecoveryOptions,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.governance import (
    MetaReasoningGovernance,
    GovernanceFindings,
    GovernanceViolation,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.health import (
    MetaReasoningHealth,
    HealthMetrics,
    HealthStatus,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.diagnostics import (
    MetaReasoningDiagnostics,
    DiagnosticEvent,
)

__all__ = [
    # Descriptor
    "MetaReasoningDescriptor",
    "MetaReasoningState",
    # Reasoner Set
    "ReasonerSet",
    "ReasonerCapability",
    # Strategy Selection
    "StrategySelection",
    "StrategyKind",
    "SelectionRationale",
    # Orchestration
    "ReasoningOrchestration",
    "ExecutionGraph",
    "SynchronizationPoint",
    "OrchestrationPolicy",
    # Resources
    "ReasoningResourceAllocation",
    "ResourceKind",
    "AllocationConstraints",
    # Monitoring
    "ReasoningMonitoring",
    "MonitoringMetric",
    "MonitoringEvent",
    "MonitorKind",
    # Adaptation
    "AdaptiveOrchestration",
    "StrategyAdaptation",
    "AdaptationTrigger",
    # Refinement
    "MetaReasoningRefinement",
    "PolicyChange",
    # Validation
    "MetaReasoningValidation",
    "ValidationStatus",
    "ValidationResult",
    # Failure
    "MetaReasoningFailure",
    "FailureKind",
    "RecoveryOptions",
    # Governance
    "MetaReasoningGovernance",
    "GovernanceFindings",
    "GovernanceViolation",
    # Health
    "MetaReasoningHealth",
    "HealthMetrics",
    "HealthStatus",
    # Diagnostics
    "MetaReasoningDiagnostics",
    "DiagnosticEvent",
]