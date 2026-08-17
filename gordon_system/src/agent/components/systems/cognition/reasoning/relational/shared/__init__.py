# Relational Reasoning Shared - Phase 7.11
# =========================================

"""
Shared contracts for Relational Reasoning.

This module contains canonical contract definitions that are shared across
all relational reasoning components.
"""

# Descriptors and lifecycle
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.descriptor import (
    RelationalDescriptor,
    RelationalMode,
    RelationalState,
)

# Entity sets
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.entity_set import (
    RelationalEntity,
    RelationalEntitySet,
    EntityRole,
    RelationType,
)

# Graph construction
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.graph_construction import (
    GraphConstruction,
    GraphConstructionStrategy,
)

# Structural inference and composition
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.structural_inference import (
    StructuralInferenceAnalysis,
    StructuralComposition,
    InferencePattern,
)

# Constraint propagation
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.constraint_propagation import (
    RelationConstraintPropagation,
)

# Graph analysis
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.graph_analysis import (
    GraphAnalysis,
)

# Refinement
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.refinement import (
    RelationalRefinement,
)

# Validation
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.validation import (
    RelationalValidation,
    ValidationKind,
)

# Failure
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.failure import (
    RelationalFailure,
    FailureKind,
)

# Governance
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.governance import (
    RelationalGovernance,
)

# Health metrics
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.health import (
    RelationalHealth,
)

# Diagnostics and trace
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared.diagnostics import (
    RelationalTrace,
    DiagnosticsRecord,
)

__all__ = [
    # Descriptors
    "RelationalDescriptor",
    "RelationalMode",
    "RelationalState",
    
    # Entity Sets
    "RelationalEntity",
    "RelationalEntitySet",
    "EntityRole",
    "RelationType",
    
    # Graph Construction
    "GraphConstruction",
    "GraphConstructionStrategy",
    
    # Structural Inference
    "StructuralInferenceAnalysis",
    "StructuralComposition",
    "InferencePattern",
    
    # Constraint Propagation
    "RelationConstraintPropagation",
    
    # Graph Analysis
    "GraphAnalysis",
    
    # Refinement
    "RelationalRefinement",
    
    # Validation
    "RelationalValidation",
    "ValidationKind",
    
    # Failure
    "RelationalFailure",
    "FailureKind",
    
    # Governance
    "RelationalGovernance",
    
    # Health
    "RelationalHealth",
    
    # Diagnostics and Trace
    "RelationalTrace",
    "DiagnosticsRecord",
]