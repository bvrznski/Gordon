# Temporal Reasoning Subsystem - Phase 7.8
# ==========================================

"""
The Temporal Reasoning subsystem is Gordon's chronological reasoning engine.

It models time as an explicit semantic dimension, representing temporal relationships
between events without executing schedules or performing planning operations.

Architecture Position:
    Events → Memory → Knowledge → Temporal Reasoning → Temporal Models
    ↓
    Temporal Relations → Reasoning Output

Canonical Components:
    - shared/       : Contract definitions (descriptor, event_set, chronology, etc.)
    - events/       : Event management and processing
    - intervals/    : Interval reasoning operations
    - chronology/   : Chronology graph construction
    - constraints/  : Constraint propagation
    - dependencies/ : Dependency analysis
    - validation/   : Temporal validation
    - governance/   : Governance evaluation
    - diagnostics/  : Observability and diagnostics

Temporal Reasoning Laws:
    TEMPORAL-LAW-001: Every session has one immutable semantic identity
    TEMPORAL-LAW-002: Temporal reasoning executes over explicit Event Sets
    TEMPORAL-LAW-003: Every temporal relation references explicit participating events
    TEMPORAL-LAW-004: Provenance is always preserved
    TEMPORAL-LAW-005: Reasoning lineage is preserved
    TEMPORAL-LAW-006: Temporal reasoning remains independently inspectable
    TEMPORAL-LAW-007: Temporal reasoning remains deterministic
    TEMPORAL-LAW-008: Completed sessions remain immutable

Anti-Patterns to Avoid:
    - Executing schedules during reasoning (only modeling)
    - Modifying Knowledge during temporal analysis
    - Inferred chronology from insertion order
    - Merging temporal and causal dependencies
    - Discarding interval uncertainty
    - Bypassing validation or governance
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal.shared import (
    # Descriptors
    TemporalDescriptor,
    TemporalMode,
    TemporalLifecycle,
    
    # Event Sets
    TemporalEvent,
    EventSet,
    EventKind,
    TemporalScope,
    
    # Chronology
    TemporalRelation,
    ChronologyGraph,
    ChronologyConstruction,
    TemporalRelationType,
    
    # Intervals
    TemporalInterval,
    IntervalReasoning,
    IntervalRelationType,
    
    # Constraints & Concurrency
    TemporalConstraint,
    ConstraintPropagation,
    ConcurrencyAnalysis,
    ConstraintType,
    ConcurrencyType,
    
    # Dependency Graphs
    TemporalDependencyGraph,
    DependencyNode,
    DependencyEdge,
    DependencyType,
    
    # Validation
    TemporalValidation,
    ValidationResult,
    ValidationType,
    
    # Failure Handling
    TemporalFailure,
    FailureKind,
    
    # Governance
    TemporalGovernance,
    
    # Health Monitoring
    TemporalHealth,
    
    # Diagnostics
    TemporalDiagnostics,
)

__all__ = [
    # Descriptors
    "TemporalDescriptor",
    "TemporalMode",
    "TemporalLifecycle",
    
    # Events
    "TemporalEvent",
    "EventSet",
    "EventKind",
    "TemporalScope",
    
    # Chronology
    "TemporalRelation",
    "ChronologyGraph",
    "ChronologyConstruction",
    "TemporalRelationType",
    
    # Intervals
    "TemporalInterval",
    "IntervalReasoning",
    "IntervalRelationType",
    
    # Constraints & Concurrency
    "TemporalConstraint",
    "ConstraintPropagation",
    "ConcurrencyAnalysis",
    "ConstraintType",
    "ConcurrencyType",
    
    # Dependency Graphs
    "TemporalDependencyGraph",
    "DependencyNode",
    "DependencyEdge",
    "DependencyType",
    
    # Validation
    "TemporalValidation",
    "ValidationResult",
    "ValidationType",
    
    # Failure Handling
    "TemporalFailure",
    "FailureKind",
    
    # Governance
    "TemporalGovernance",
    
    # Health Monitoring
    "TemporalHealth",
    
    # Diagnostics
    "TemporalDiagnostics",
]