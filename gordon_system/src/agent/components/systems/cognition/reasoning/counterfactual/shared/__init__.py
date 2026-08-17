# Counterfactual Reasoning Shared Contracts - Phase 7.6 Part 2
# =============================================================

"""
Canonical Counterfactual Contracts.

This module implements all canonical contracts specified in Phase 7.6:

Part 2 specifies:
    * Canonical Counterfactual contracts
    * World branching
    * Intervention semantics
    * Divergence analysis
    * Alternative world evaluation
    * Comparison
    * Validation
    * Governance

All contracts follow the principle that Counterfactual Reasoning operates on
immutable snapshots rather than mutable models, preserving complete traceability.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual.shared.descriptor import (
    CounterfactualDescriptor,
    CounterfactualMode,
    CounterfactualLifecycle,
    CounterfactualSessionIdentity,
    WorldSetIdentity,
    BranchingStructure,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual.shared.world_set import (
    WorldSet,
    ReferenceWorld,
    AlternativeWorld,
    WorldBranch,
    WorldSnapshot,
    CausalState,
    TemporalPosition,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual.shared.intervention_pipeline import (
    CounterfactualIntervention,
    InterventionPipeline,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual.shared.divergence import (
    WorldDivergence,
    DivergencePipeline,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual.shared.comparison_pipeline import (
    CounterfactualComparison,
    ComparisonPipeline,
    ComparisonDifference,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual.shared.refinement import (
    CounterfactualRefinement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual.shared.validation_result import (
    CounterfactualValidation,
    ValidationResultKind,
    ValidationFindingKind,
    ValidationFinding,
    ValidationTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual.shared.governance import (
    CounterfactualGovernance,
    GovernanceRule,
    GovernanceFinding,
    GovernanceHealth,
    GovernanceFindingKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual.shared.failure import (
    CounterfactualFailure,
    FailureKind,
    FailureMode,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual.shared.health import (
    CounterfactualHealth,
    CounterfactualDiagnostics,
)

__all__ = [
    # Descriptors
    "CounterfactualDescriptor",
    "CounterfactualMode",
    "CounterfactualLifecycle",
    
    # World Set Management
    "WorldSetIdentity",
    "BranchingStructure",
    
    # Reference World
    "ReferenceWorld",
    "WorldSnapshot",
    "CausalState",
    "TemporalPosition",
    
    # Alternative Worlds
    "AlternativeWorld",
    "WorldBranch",
    
    # Interventions
    "CounterfactualIntervention",
    "InterventionPipeline",
    
    # Divergence
    "WorldDivergence",
    "DivergencePipeline",
    
    # Comparison
    "CounterfactualComparison",
    "ComparisonPipeline",
    
    # Refinement
    "CounterfactualRefinement",
    
    # Validation
    "CounterfactualValidation",
    "ValidationResultKind",
    "ValidationFinding",
    "ValidationTrace",
    
    # Governance
    "CounterfactualGovernance",
    "GovernanceRule",
    "GovernanceFinding",
    "GovernanceHealth",
    
    # Failure
    "CounterfactualFailure",
    "FailureKind",
    
    # Health and Diagnostics
    "CounterfactualHealth",
    "CounterfactualDiagnostics",
]