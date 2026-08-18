# Reasoning Shared Contracts - Phase 7.0
# =======================================

"""
Shared contract types for the reasoning subsystem.

This module provides canonical implementations of all reasoning contracts:

    Descriptor       - Metadata about reasoning operations
    Inference        - Deriving conclusions from knowledge
    Hypothesis       - Candidate explanations under evaluation
    Alternatives     - Candidate solutions under consideration
    Deliberation     - Comparing and selecting alternatives
    Conclusion       - Summarizing reasoning results
    Pipeline         - Complete reasoning execution flow
    Validation       - Evaluating reasoning without modification
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.descriptor import (
    ReasoningDescriptor,
    ReasoningKind,
    ReasoningState,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.inference import (
    Inference,
    InferenceTrace,
    InferenceStrategy,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.hypothesis import (
    ReasoningHypothesis,
    HypothesisEvaluation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.alternatives import (
    ReasoningAlternative,
    AlternativeComparison,
    AlternativeRanking,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.deliberation import (
    Deliberation,
    DeliberationPipeline,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.conclusion import (
    ReasoningConclusion,
    ConclusionTrace,
    ConclusionEvaluation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.pipeline import (
    ReasoningPipeline,
    ReasoningSession,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.validation import (
    ReasoningValidation,
    ReasoningFailure,
    ReasoningGovernance,
)

# Planning Reasoning exports (Phase 7.20)
from gordon_system.src.agent.components.systems.cognition.reasoning.planning import (
    # Descriptors
    PlanningDescriptor,
    PlanningSessionIdentity,
    PlanningMode,
    PlanningLifecycle,
    
    # Plan Set
    ExecutionPlan,
    PlanSet,
    PlanConstruction,
    
    # Tasks
    PlannedTask,
    TaskKind,
    TaskState,
    TaskManagement,
    TaskDecomposition,
    
    # Dependencies
    TaskDependency,
    DependencyKind,
    DependencyGraphState,
    DependencyGraph,
    DependencyAnalysis,
    
    # Resources
    ResourceAllocation,
    ResourceType,
    AllocationPolicy,
    ResourcePlanning,
    ResourceAvailability,
    
    # Contingencies
    ContingencyPlan,
    ContingencyKind,
    ContingencyState,
    ContingencyManagement,
    RecoveryTrigger,
    
    # Refinement
    PlanningRefinement,
    PlanHistory,
    
    # Validation
    PlanningValidation,
    ValidationFindingKind,
    ValidationFinding,
    ValidationTrace,
    
    # Failure
    PlanningFailure,
    FailureKind,
    FailureTrace,
    
    # Governance
    PlanningGovernance,
    GovernanceFindingKind,
    GovernanceFinding,
    PlanningSessionGovernance,
    
    # Health
    PlanningHealth,
    HealthMetricsSnapshot,
    HealthAlert,
)

# Hypothetical Reasoning exports (Phase 7.15)
from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical import (
    # Descriptors
    HypotheticalDescriptor,
    HypothesisSessionIdentity,
    HypotheticalMode,
    HypotheticalLifecycle,
    
    # Hypothesis sets
    HypothesisIdentity,
    ExplorationStrategy,
    HypothesisSetIdentity,
    HypothesisSet,
    AssumptionSet,
    
    # Possibility spaces
    PossibilityKind,
    PossibilityIdentity,
    Constraint,
    PossibilitySpaceIdentity,
    PossibilitySpace,
    PossibilitySpaceConstruction,
    
    # Scenarios
    ScenarioEnvironmentKind,
    ScenarioIdentity,
    EnvironmentalCondition,
    HypotheticalScenario,
    ScenarioExploration,
    
    # Comparison
    ComparisonMetric,
    HypothesisComparisonIdentity,
    ComparisonResult,
    HypothesisComparison,
    
    # Refinement
    RefinementIdentity,
    HypothesisRefinement,
    HypothesisRefinementPipeline,
    
    # Validation
    ValidationFindingKind,
    ValidationIdentity,
    ValidationFinding,
    ValidationResult,
    HypotheticalValidationError,
    
    # Failure
    HypotheticalFailureKind,
    HypotheticalFailure,
    FailureTrace,
    
    # Governance
    GovernanceRule,
    GovernanceFindingKind,
    GovernanceIdentity,
    GovernanceFinding,
    HypotheticalGovernance,
    GovernanceHealth,
    
    # Health
    HypotheticalHealth,
    HypotheticalTrace,
)

__all__ = [
    # Descriptor
    "ReasoningDescriptor",
    "ReasoningKind", 
    "ReasoningState",
    
    # Inference
    "Inference",
    "InferenceTrace",
    "InferenceStrategy",
    
    # Hypothesis
    "ReasoningHypothesis",
    "HypothesisEvaluation",
    
    # Alternatives
    "ReasoningAlternative",
    "AlternativeComparison",
    "AlternativeRanking",
    
    # Deliberation
    "Deliberation",
    "DeliberationPipeline",
    
    # Conclusion
    "ReasoningConclusion",
    "ConclusionTrace",
    "ConclusionEvaluation",
    
    # Pipeline
    "ReasoningPipeline",
    "ReasoningSession",
    
    # Validation
    "ReasoningValidation",
    "ReasoningFailure",
    "ReasoningGovernance",
    
    # Planning Reasoning contracts (Phase 7.20)
    "PlanningDescriptor",
    "PlanningSessionIdentity",
    "PlanningMode",
    "PlanningLifecycle",
    
    "ExecutionPlan",
    "PlanSet",
    "PlanConstruction",
    
    "PlannedTask",
    "TaskKind",
    "TaskState",
    "TaskManagement",
    "TaskDecomposition",
    
    "TaskDependency",
    "DependencyKind",
    "DependencyGraphState",
    "DependencyGraph",
    "DependencyAnalysis",
    
    "ResourceAllocation",
    "ResourceType",
    "AllocationPolicy",
    "ResourcePlanning",
    "ResourceAvailability",
    
    "ContingencyPlan",
    "ContingencyKind",
    "ContingencyState",
    "ContingencyManagement",
    "RecoveryTrigger",
    
    "PlanningRefinement",
    "PlanHistory",
    
    "PlanningValidation",
    "ValidationFindingKind",
    "ValidationFinding",
    "ValidationTrace",
    
    "PlanningFailure",
    "FailureKind",
    "FailureTrace",
    
    "PlanningGovernance",
    "GovernanceFindingKind",
    "GovernanceFinding",
    "PlanningSessionGovernance",
    
    "PlanningHealth",
    "HealthMetricsSnapshot",
    "HealthAlert",
    
    # Hypothetical Reasoning contracts (Phase 7.15)
    "HypotheticalDescriptor",
    "HypothesisSessionIdentity",
    "HypotheticalMode",
    "HypotheticalLifecycle",
    
    "HypothesisIdentity",
    "ExplorationStrategy",
    "HypothesisSetIdentity",
    "HypothesisSet",
    "AssumptionSet",
    
    "PossibilityKind",
    "PossibilityIdentity",
    "Constraint",
    "PossibilitySpaceIdentity",
    "PossibilitySpace",
    "PossibilitySpaceConstruction",
    
    "ScenarioEnvironmentKind",
    "ScenarioIdentity",
    "EnvironmentalCondition",
    "HypotheticalScenario",
    "ScenarioExploration",
    
    "ComparisonMetric",
    "HypothesisComparisonIdentity",
    "ComparisonResult",
    "HypothesisComparison",
    
    "RefinementIdentity",
    "HypothesisRefinement",
    "HypothesisRefinementPipeline",
    
    "ValidationFindingKind",
    "ValidationIdentity",
    "ValidationFinding",
    "ValidationResult",
    "HypotheticalValidationError",
    
    "HypotheticalFailureKind",
    "HypotheticalFailure",
    "FailureTrace",
    
    "GovernanceRule",
    "GovernanceFindingKind",
    "GovernanceIdentity",
    "GovernanceFinding",
    "HypotheticalGovernance",
    "GovernanceHealth",
    
    "HypotheticalHealth",
    "HypotheticalTrace",
]