# Hypothetical Reasoning Subsystem - Phase 7.15
# ==============================================

"""
Canonical contracts for the Hypothetical Reasoning subsystem.

Hypothetical Reasoning generates structured candidate realities without
committing to their truth. It serves as Gordon's possibility generation engine.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.hypothetical.shared import (
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
    
    # Assumptions
    AssumptionKind,
    AssumptionJustification,
    Assumption,
    AssumptionManagement,
    HiddenAssumption,
    
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
    
    # Evolution
    EvolutionIdentity,
    HypothesisEvolution,
    
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
    
    # Diagnostics
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