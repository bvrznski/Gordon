# Strategic Reasoning - Phase 7.18
# =================================

"""
Strategic Reasoning for the Gordon Cognitive Architecture.

Strategic Reasoning is Gordon's long-horizon cognitive direction engine.
It determines "What should be pursued?" and "What sequence of objectives 
best advances long-term success?"

Unlike Planning, which constructs executable plans, Strategic Reasoning
defines which plans should exist in the first place - establishing enduring
direction across the entire cognitive architecture.

This module implements Phase 7.18 specifications including:
    - Canonical strategic contracts
    - Objective management
    - Strategy formation
    - Policy construction
    - Trade-off analysis
    - Validation
    - Governance
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.descriptor import (
    StrategicDescriptor,
    StrategicState,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.objective_set import (
    Objective,
    ObjectiveSet,
    ObjectivePrioritization,
    ObjectivePriority,
    ObjectiveConstraintType,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.formation import (
    StrategyFormation,
    StrategyFormationFailure,
    StrategyFormationProgress,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.policies import (
    StrategicPolicy,
    PolicyConstruction,
    PolicyConflict,
    PolicyAdaptation,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.tradeoffs import (
    StrategicTradeoff,
    TradeoffAnalysis,
    TradeoffMetrics,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.prioritization import (
    ObjectivePrioritization,
    PrioritizationFailure,
    PrioritizationMetrics,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.adaptation import (
    StrategicAdaptation,
    StrategicAdaptationPipeline,
    AdaptationFailure,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.evolution import (
    StrategicEvolution,
    EvolutionStep,
    EvolutionFailure,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.validation import (
    StrategicValidation,
    ValidationFailure,
    ValidationTrace,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.failure import (
    StrategicFailure,
    FailureCategory,
    FailureRecoveryPlan,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.governance import (
    StrategicGovernance,
    GovernanceFinding,
    GovernanceReport,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.health import (
    StrategicHealth,
    HealthMetricsSnapshot,
    HealthAlert,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.diagnostics import (
    StrategicDiagnostics,
    DiagnosticEvent,
    DiagnosticTrace,
)

__all__ = [
    # Shared
    "StrategicDescriptor",
    "StrategicState",
    "Objective",
    "ObjectiveSet",
    "ObjectivePrioritization",
    "ObjectivePriority",
    "ObjectiveConstraintType",
    "StrategyFormation",
    "StrategyFormationFailure",
    "StrategyFormationProgress",
    "StrategicPolicy",
    "PolicyConstruction",
    "PolicyConflict",
    "PolicyAdaptation",
    "StrategicTradeoff",
    "TradeoffAnalysis",
    "TradeoffMetrics",
    "ObjectivePrioritization",
    "PrioritizationFailure",
    "PrioritizationMetrics",
    "StrategicAdaptation",
    "StrategicAdaptationPipeline",
    "AdaptationFailure",
    "StrategicEvolution",
    "EvolutionStep",
    "EvolutionFailure",
    "StrategicValidation",
    "ValidationFailure",
    "ValidationTrace",
    "StrategicFailure",
    "FailureCategory",
    "FailureRecoveryPlan",
    "StrategicGovernance",
    "GovernanceFinding",
    "GovernanceReport",
    "StrategicHealth",
    "HealthMetricsSnapshot",
    "HealthAlert",
    "StrategicDiagnostics",
    "DiagnosticEvent",
    "DiagnosticTrace",
]