# Shared Components - Phase 7.15
# ===============================

"""
Shared components for Hypothetical Reasoning.

Exports all canonical contracts, types, and utilities used across
hypothetical reasoning modules.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.descriptor import (
    HypotheticalDescriptor,
    HypothesisSessionIdentity,
    HypotheticalMode,
    HypotheticalLifecycle,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.hypothesis_set import (
    HypothesisIdentity,
    ExplorationStrategy,
    HypothesisSetIdentity,
    HypothesisSet,
    AssumptionSet,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.possibility_space import (
    PossibilityKind,
    PossibilityIdentity,
    Constraint,
    PossibilitySpaceIdentity,
    PossibilitySpace,
    PossibilitySpaceConstruction,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.assumptions import (
    AssumptionKind,
    AssumptionJustification,
    Assumption,
    AssumptionManagement,
    HiddenAssumption,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.scenarios import (
    ScenarioEnvironmentKind,
    ScenarioIdentity,
    EnvironmentalCondition,
    HypotheticalScenario,
    ScenarioExploration,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.comparison import (
    ComparisonMetric,
    HypothesisComparisonIdentity,
    ComparisonResult,
    HypothesisComparison,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.refinement import (
    RefinementIdentity,
    HypothesisRefinement,
    HypothesisRefinementPipeline,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.evolution import (
    EvolutionIdentity,
    HypothesisEvolution,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.validation import (
    ValidationFindingKind,
    ValidationIdentity,
    ValidationFinding,
    ValidationResult,
    HypotheticalValidationError,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.failure import (
    HypotheticalFailureKind,
    HypotheticalFailure,
    FailureTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.governance import (
    GovernanceRule,
    GovernanceFindingKind,
    GovernanceIdentity,
    GovernanceFinding,
    HypotheticalGovernance,
    GovernanceHealth,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.health import (
    HypotheticalHealth,
    HypotheticalTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared.diagnostics import (
    DiagnosticType,
    HypotheticalDiagnostics,
    DiagnosticsRecord,
)


__all__ = [
    # Descriptors
    "HypotheticalDescriptor",
    "HypothesisSessionIdentity",
    "HypotheticalMode",
    "HypotheticalLifecycle",
    
    # Hypothesis sets
    "HypothesisIdentity",
    "ExplorationStrategy",
    "HypothesisSetIdentity",
    "HypothesisSet",
    "AssumptionSet",
    
    # Possibility spaces
    "PossibilityKind",
    "PossibilityIdentity",
    "Constraint",
    "PossibilitySpaceIdentity",
    "PossibilitySpace",
    "PossibilitySpaceConstruction",
    
    # Assumptions
    "AssumptionKind",
    "AssumptionJustification",
    "Assumption",
    "AssumptionManagement",
    "HiddenAssumption",
    
    # Scenarios
    "ScenarioEnvironmentKind",
    "ScenarioIdentity",
    "EnvironmentalCondition",
    "HypotheticalScenario",
    "ScenarioExploration",
    
    # Comparison
    "ComparisonMetric",
    "HypothesisComparisonIdentity",
    "ComparisonResult",
    "HypothesisComparison",
    
    # Refinement
    "RefinementIdentity",
    "HypothesisRefinement",
    "HypothesisRefinementPipeline",
    
    # Evolution
    "EvolutionIdentity",
    "HypothesisEvolution",
    
    # Validation
    "ValidationFindingKind",
    "ValidationIdentity",
    "ValidationFinding",
    "ValidationResult",
    "HypotheticalValidationError",
    
    # Failure
    "HypotheticalFailureKind",
    "HypotheticalFailure",
    "FailureTrace",
    
    # Governance
    "GovernanceRule",
    "GovernanceFindingKind",
    "GovernanceIdentity",
    "GovernanceFinding",
    "HypotheticalGovernance",
    "GovernanceHealth",
    
    # Health
    "HypotheticalHealth",
    "HypotheticalTrace",
    
    # Diagnostics
    "DiagnosticType",
    "HypotheticalDiagnostics",
    "DiagnosticsRecord",
]