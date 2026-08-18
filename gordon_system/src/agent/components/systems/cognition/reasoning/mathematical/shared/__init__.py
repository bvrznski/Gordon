# Mathematical Reasoning Shared Contracts - Phase 7.46
# ======================================================

"""
Shared contract types for the mathematical reasoning subsystem.

This module provides canonical implementations of all mathematical reasoning contracts:

    MathematicalDescriptor   - Metadata about mathematical sessions
    MathematicalModel        - Formal mathematical problem representation
    ConstraintAnalysis       - Constraint evaluation and analysis
    OptimizationAnalysis     - Optimization problem analysis
    ProofAnalysis            - Proof validation and verification
    NumericalAnalysis        - Numerical approximation analysis
    MathematicalTrace        - Complete reasoning trace
    MathematicalSession      - Active mathematical session
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.descriptor import (
    MathematicalDescriptor,
    MathematicalMode,
    MathematicalLifecycle,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.mathematical_set import (
    MathematicalSet,
    Variable,
    Constraint,
    ObjectiveFunction,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.pipeline import (
    MathematicalPipeline,
    PipelineStage,
    SolutionStrategy,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.constraints import (
    ConstraintSet,
    HardConstraint,
    SoftConstraint,
    ConstraintDependencyGraph,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.optimization import (
    OptimizationProblem,
    ObjectiveValue,
    OptimalSolution,
    ConvergenceMetrics,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.proofs import (
    ProofSystem,
    Theorem,
    ProofStructure,
    VerificationStatus,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.algebra import (
    AlgebraicExpression,
    SymbolicVariable,
    Equation,
    SystemOfEquations,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.geometry import (
    GeometricShape,
    GeometricRelation,
    Transformation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.numerics import (
    NumericalApproximation,
    ApproximationError,
    PrecisionMetrics,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.graphs import (
    MathematicalGraph,
    GraphNode,
    GraphEdge,
    GraphAlgorithm,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.evolution import (
    MathematicalEvolution,
    EvolutionHistory,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.validation import (
    MathematicalValidation,
    ValidationResult,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.failure import (
    MathematicalFailure,
    FailureKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.governance import (
    MathematicalGovernance,
    GovernanceFinding,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.health import (
    MathematicalHealth,
    HealthMetrics,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.mathematical.shared.diagnostics import (
    DiagnosticTrace,
    Diagnostics,
)

__all__ = [
    # Descriptor
    "MathematicalDescriptor",
    "MathematicalMode",
    "MathematicalLifecycle",
    
    # Mathematical Set
    "MathematicalSet",
    "Variable",
    "Constraint",
    "ObjectiveFunction",
    
    # Pipeline
    "MathematicalPipeline",
    "PipelineStage",
    "SolutionStrategy",
    
    # Constraints
    "ConstraintSet",
    "HardConstraint",
    "SoftConstraint",
    "ConstraintDependencyGraph",
    
    # Optimization
    "OptimizationProblem",
    "ObjectiveValue",
    "OptimalSolution",
    "ConvergenceMetrics",
    
    # Proofs
    "ProofSystem",
    "Theorem",
    "ProofStructure",
    "VerificationStatus",
    
    # Algebra
    "AlgebraicExpression",
    "SymbolicVariable",
    "Equation",
    "SystemOfEquations",
    
    # Geometry
    "GeometricShape",
    "GeometricRelation",
    "Transformation",
    
    # Numerics
    "NumericalApproximation",
    "ApproximationError",
    "PrecisionMetrics",
    
    # Graphs
    "MathematicalGraph",
    "GraphNode",
    "GraphEdge",
    "GraphAlgorithm",
    
    # Evolution
    "MathematicalEvolution",
    "EvolutionHistory",
    
    # Validation
    "MathematicalValidation",
    "ValidationResult",
    
    # Failure
    "MathematicalFailure",
    "FailureKind",
    
    # Governance
    "MathematicalGovernance",
    "GovernanceFinding",
    
    # Health
    "MathematicalHealth",
    "HealthMetrics",
    
    # Diagnostics
    "DiagnosticTrace",
    "Diagnostics",
]