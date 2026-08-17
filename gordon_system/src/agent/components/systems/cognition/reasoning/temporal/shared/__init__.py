# Temporal Reasoning Shared Contracts - Phase 7.8
# ==============================================

"""
Shared contracts for the Temporal Reasoning subsystem.

This module provides canonical contract definitions for:
    - Descriptors (TemporalDescriptor, TemporalLifecycle)
    - Event Sets (EventSet, TemporalEvent, EventKind)
    - Chronology (ChronologyGraph, ChronologyConstruction, TemporalRelation)
    - Interval Reasoning (TemporalInterval, IntervalReasoning)
    - Constraint Propagation (TemporalConstraint, ConstraintPropagation, ConcurrencyAnalysis)
    - Dependency Graphs (TemporalDependencyGraph, DependencyNode, DependencyEdge)
    - Validation (TemporalValidation, ValidationResult, ValidationType)
    - Failure Handling (TemporalFailure, FailureKind)
    - Governance (TemporalGovernance)
    - Health Monitoring (TemporalHealth)
    - Diagnostics (TemporalDiagnostics)
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.descriptor import (
    TemporalDescriptor,
    TemporalSessionIdentity,
    TemporalMode,
    TemporalLifecycle,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.event_set import (
    TemporalEvent,
    EventSet,
    EventSetIdentity,
    EventKind,
    TemporalScope,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.chronology import (
    TemporalRelation,
    ChronologyGraph,
    ChronologyConstruction,
    ChronologyIdentity,
    TemporalRelationType,
    ChronologyState,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.interval_reasoning import (
    TemporalInterval,
    IntervalReasoning,
    IntervalReasoningIdentity,
    IntervalRelationType,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.constraint_propagation import (
    TemporalConstraint,
    ConstraintPropagation,
    ConstraintPropagationIdentity,
    ConcurrencyAnalysis,
    ConcurrencyAnalysisIdentity,
    ConstraintType,
    ConstraintState,
    ConcurrencyType,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.dependency_graph import (
    DependencyNode,
    DependencyEdge,
    TemporalDependencyGraph,
    DependencyGraphIdentity,
    DependencyType,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.validation import (
    TemporalValidation,
    TemporalValidationIdentity,
    ValidationType,
    ValidationResult,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.refinement import (
    TemporalRefinement,
    TemporalRefinementIdentity,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.failure import (
    TemporalFailure,
    TemporalFailureIdentity,
    FailureKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.governance import (
    TemporalGovernance,
    TemporalGovernanceIdentity,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.health import (
    TemporalHealth,
    TemporalHealthIdentity,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared.diagnostics import (
    TemporalDiagnostics,
    TemporalDiagnosticsIdentity,
    DiagnosticType,
)

__all__ = [
    # Descriptors
    "TemporalDescriptor",
    "TemporalSessionIdentity",
    "TemporalMode",
    "TemporalLifecycle",
    
    # Events
    "TemporalEvent",
    "EventSet",
    "EventSetIdentity",
    "EventKind",
    "TemporalScope",
    
    # Chronology
    "TemporalRelation",
    "ChronologyGraph",
    "ChronologyConstruction",
    "ChronologyIdentity",
    "TemporalRelationType",
    "ChronologyState",
    
    # Intervals
    "TemporalInterval",
    "IntervalReasoning",
    "IntervalReasoningIdentity",
    "IntervalRelationType",
    
    # Constraints & Concurrency
    "TemporalConstraint",
    "ConstraintPropagation",
    "ConstraintPropagationIdentity",
    "ConcurrencyAnalysis",
    "ConcurrencyAnalysisIdentity",
    "ConstraintType",
    "ConstraintState",
    "ConcurrencyType",
    
    # Dependency Graphs
    "DependencyNode",
    "DependencyEdge",
    "TemporalDependencyGraph",
    "DependencyGraphIdentity",
    "DependencyType",
    
    # Validation
    "TemporalValidation",
    "TemporalValidationIdentity",
    "ValidationType",
    "ValidationResult",
    
    # Refinement
    "TemporalRefinement",
    "TemporalRefinementIdentity",
    
    # Failure Handling
    "TemporalFailure",
    "TemporalFailureIdentity",
    "FailureKind",
    
    # Governance
    "TemporalGovernance",
    "TemporalGovernanceIdentity",
    
    # Health Monitoring
    "TemporalHealth",
    "TemporalHealthIdentity",
    
    # Diagnostics
    "TemporalDiagnostics",
    "TemporalDiagnosticsIdentity",
    "DiagnosticType",
]