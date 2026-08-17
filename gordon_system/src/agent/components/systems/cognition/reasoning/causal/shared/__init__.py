# Causal Reasoning Shared Contracts - Phase 7.5
# ==============================================

"""
Shared contract types for the causal reasoning subsystem.

This module provides canonical implementations of all causal reasoning contracts:

    CausalDescriptor         - Metadata about causal reasoning operations
    MechanismSet             - Set of explicit causal mechanisms
    GraphConstruction        - Causal graph construction results
    Intervention             - Hypothetical intervention analysis
    InterventionAnalysis     - Full intervention analysis with predictions
    EffectPropagation        - Propagation path through mechanisms
    DependencyAnalysis       - Dependency discovery and analysis
    StructuralCausalModel    - Structural causal equations
    CausalRefinement         - Model refinement history
    CounterfactualPreparation - Future counterfactual preparation
    CausalValidation         - Validation results
    CausalFailure            - Failure records
    CausalGovernance         - Governance evaluation
    CausalHealth             - Health metrics
    CausalDiagnostics        - Diagnostic events and process insight
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.descriptor import (
    CausalDescriptor,
    CausalMode,
    CausalLifecycle,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.mechanism_set import (
    MechanismSet,
    CausalMechanism,
    MechanismKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.graph_construction import (
    GraphConstruction,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.intervention import (
    Intervention,
    InterventionAnalysis,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.propagation import (
    EffectPropagation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.dependencies import (
    DependencyAnalysis,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.scm import (
    StructuralCausalModel,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.refinement import (
    CausalRefinement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.counterfactual import (
    CounterfactualPreparation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.validation import (
    CausalValidation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.failure import (
    CausalFailure,
    FailureKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.governance import (
    CausalGovernance,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.health import (
    CausalHealth,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.diagnostics import (
    CausalDiagnostics,
)

__all__ = [
    "CausalDescriptor",
    "CausalMode",
    "CausalLifecycle",
    "MechanismSet",
    "CausalMechanism",
    "MechanismKind",
    "GraphConstruction",
    "Intervention",
    "InterventionAnalysis",
    "EffectPropagation",
    "DependencyAnalysis",
    "StructuralCausalModel",
    "CausalRefinement",
    "CounterfactualPreparation",
    "CausalValidation",
    "CausalFailure",
    "FailureKind",
    "CausalGovernance",
    "CausalHealth",
    "CausalDiagnostics",
]