# Counterfactual Reasoning Subsystem - Phase 7.6
# ==============================================

"""
The Counterfactual Reasoning subsystem is Gordon's alternative world reasoning engine.

It constructs and evaluates hypothetical worlds created through explicit interventions
applied to a reference world. Counterfactual reasoning answers:
    "What would have happened if...?" (alternative reality analysis)
    "What could be different if...?" (intervention analysis)

Architecture Position:
    Observed World → World Model → Causal Model → Counterfactual Reasoning → Alternative Worlds
                                                              ↓
                                                         Comparison → Reasoning Output

Canonical Components:
    - shared/       : Contract definitions (descriptor, world_set, branching, etc.)
    - worlds/       : Reference and alternative world management
    - interventions/: Intervention specification and application
    - branching/    : World branching logic
    - comparison/   : World state comparison
    - divergence/   : Causal divergence analysis
    - validation/   : Validation of counterfactual reasoning
    - governance/   : Governance evaluation
    - observability/: Observability and diagnostics

Counterfactual Reasoning Laws:
    COUNTERFUAL-LAW-001: Every session has one immutable semantic identity
    COUNTERFUAL-LAW-002: Counterfactual reasoning executes over one explicit Reference World
    COUNTERFUAL-LAW-003: Every Alternative World originates from one explicitly declared Intervention
    COUNTERFUAL-LAW-004: Provenance is always preserved
    COUNTERFUAL-LAW-005: Reasoning lineage is preserved
    COUNTERFUAL-LAW-006: Counterfactual reasoning remains independently inspectable
    COUNTERFUAL-LAW-007: Counterfactual reasoning remains deterministic given identical states
    COUNTERFUAL-LAW-008: Completed sessions remain immutable

Anti-Patterns to Avoid:
    - Mutating the Reference World during reasoning
    - Creating branches without explicit interventions
    - Merging worlds implicitly (branches must preserve ancestry)
    - Discarding branch ancestry or traceability
    - Hiding divergence propagation paths
    - Executing interventions during reasoning (only hypothetical analysis)
    - Silently repairing or modifying generated worlds
    - Bypassing validation or governance

Architecture Note:
    Counterfactual Reasoning should operate on persistent world snapshots rather than
    mutable world models. Each generated world should be an immutable branch with explicit
    ancestry, allowing Gordon to replay, compare and revisit any hypothetical scenario.

    Future extensions: parallel counterfactual search where multiple interventions are
    explored concurrently, with dynamic compute allocation for high-value branches.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual.shared import (
    # Descriptors
    CounterfactualDescriptor,
    CounterfactualMode,
    CounterfactualLifecycle,
    
    # World Set Management
    WorldSet,
    WorldSetIdentity,
    BranchingStructure,
    
    # Reference World
    ReferenceWorld,
    WorldSnapshot,
    CausalState,
    TemporalPosition,
    
    # Alternative Worlds
    AlternativeWorld,
    WorldBranch,
    
    # Interventions
    CounterfactualIntervention,
    InterventionPipeline,
    
    # Divergence
    WorldDivergence,
    DivergencePipeline,
    
    # Comparison
    CounterfactualComparison,
    ComparisonPipeline,
    
    # Refinement
    CounterfactualRefinement,
    
    # Validation
    CounterfactualValidation,
    ValidationResultKind,
    ValidationFinding,
    ValidationTrace,
    
    # Governance
    CounterfactualGovernance,
    GovernanceRule,
    GovernanceFinding,
    GovernanceHealth,
    
    # Failure
    CounterfactualFailure,
    FailureKind,
    
    # Health and Diagnostics
    CounterfactualHealth,
    CounterfactualDiagnostics,
)

__all__ = [
    # Descriptors
    "CounterfactualDescriptor",
    "CounterfactualMode",
    "CounterfactualLifecycle",
    
    # World Set Management
    "WorldSet",
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