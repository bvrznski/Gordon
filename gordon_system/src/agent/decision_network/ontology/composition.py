# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Composition Ontology

This module defines the canonical Action composition taxonomy that describes
how Actions can be composed together.

ACTION COMPOSITION TAXONOMY
===========================

Composition describes how Actions can be combined to create more complex
behavior from simpler components.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet, Tuple, Optional


# =============================================================================
# ACTION COMPOSITION TYPES - Structural organization
# =============================================================================

class ActionCompositionType(Enum):
    """
    The type of composition relationship between Actions.
    
    Composition types describe how Actions are structured together to
    create more complex behavior from simpler components.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # STRUCTURAL COMPOSITION - How actions are organized
    # =============================================================================
    
    ATOMIC = "atomic"
    """Single, indivisible semantic operation."""
    
    SEQUENCE = "sequence"
    """Ordered composition of Actions."""
    
    PARALLEL = "parallel"
    """Parallel execution of independent Actions."""
    
    CHOICE = "choice"
    """Alternative composition where only one Action executes."""
    
    CONDITIONAL = "conditional"
    """Conditional execution based on guard predicate."""
    
    LOOP = "loop"
    """Repeated execution until condition is met."""
    
    # =============================================================================
    # TEMPORAL COMPOSITION - Timing relationships
    # =============================================================================
    
    CONCURRENT = "concurrent"
    """Actions execute simultaneously."""
    
    OVERLAPPING = "overlapping"
    """Actions partially overlap in time."""
    
    SEQUENTIAL = "sequential"
    """Actions execute one after another."""
    
    # =============================================================================
    # DEPENDENCY COMPOSITION - Control flow
    # =============================================================================
    
    DEPENDENT = "dependent"
    """Action depends on completion of another."""
    
    INDEPENDENT = "independent"
    """Action is independent of others."""
    
    BARRIER = "barrier"
    """Waits for all dependencies before executing."""
    
    FAN_IN = "fan_in"
    """Combines results from multiple Actions."""
    
    FAN_OUT = "fan_out"
    """Distributes to multiple Actions."""


# =============================================================================
# ACTION COMPOSITE REFERENCES - Reference patterns
# =============================================================================

class ActionCompositeReference(Enum):
    """
    How a composite Action references its components.
    
    Composite references describe how complex Actions refer to their
    constituent parts without embedding runtime information.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    DIRECT_REFERENCE = "direct_reference"
    """Direct reference to component Actions."""
    
    INDEX_REFERENCE = "index_reference"
    """Reference by position in sequence."""
    
    LABEL_REFERENCE = "label_reference"
    """Reference by symbolic label."""
    
    PATTERN_REFERENCE = "pattern_reference"
    """Reference by template pattern."""
    
    DYNAMIC_REFERENCE = "dynamic_reference"
    """Reference resolved at runtime."""
    
    # =============================================================================
    # REFERENCE CARDINALITY
    # =============================================================================
    
    SINGLE = "single"
    """Reference exactly one component."""
    
    MULTIPLE = "multiple"
    """Reference multiple components."""
    
    OPTIONAL = "optional"
    """Component may or may not be present."""
    
    ZERO_OR_MORE = "zero_or_more"
    """Zero or more components."""
    
    ONE_OR_MORE = "one_or_more"
    """At least one component required."""


# =============================================================================
# ACTION ATOMICITY - Indivisibility levels
# =============================================================================

class ActionAtomicity(Enum):
    """
    The atomicity level of an Action - how indivisible it is semantically.
    
    Atomicity describes whether an Action represents a single semantic
    operation or can be meaningfully broken down further.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # ATOMICITY LEVELS
    # =============================================================================
    
    SEMANTICALLY_ATOMIC = "semantically_atomic"
    """Indivisible at semantic level."""
    
    LOGICALLY_ATOMIC = "logically_atomic"
    """Atomic within logical context."""
    
    EXECUTION_ATOMIC = "execution_atomic"
    """Atomically executed (runtime concept, reference only)."""
    
    TRANSACTIONALLY_ATOMIC = "transactionally_atomic"
    """Atomically within transaction (reference only)."""
    
    COMPOSITE = "composite"
    """Composed of multiple operations."""
    
    # =============================================================================
    # ATOMICITY PROPERTIES
    # =============================================================================
    
    IS_INDIVISIBLE = "is_indivisible"
    """Cannot be further decomposed."""
    
    IS_REVERSIBLE_ATOMIC = "is_reversible_atomic"
    """Atomic but reversible."""
    
    IS_IDEMPOTENT_ATOMIC = "is_idempotent_atomic"
    """Atomic and idempotent."""


# =============================================================================
# ACTION GRANULARITY - Scope levels
# =============================================================================

class ActionGranularity(Enum):
    """
    The granularity or scope level of an Action.
    
    Granularity describes whether the action represents a single semantic
    operation, multiple operations, or a composite reference.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # GRANULARITY LEVELS
    # =============================================================================
    
    ATOMIC_OPERATION = "atomic_operation"
    """Single atomic semantic operation."""
    
    SINGLE_TARGET = "single_target"
    """Operation on one target entity."""
    
    MULTI_TARGET = "multi_target"
    """Operation on multiple ordered targets."""
    
    BATCH_OPERATION = "batch_operation"
    """Batch operation across many similar targets."""
    
    COMPOSITE_REFERENCE = "composite_reference"
    """Reference to composite behavior (not the composition itself)."""
    
    OPEN_ENDED = "open_ended"
    """Operation with potentially unbounded scope or duration."""


# =============================================================================
# COMPOSITE ACTION PATTERNS
# =============================================================================

class ActionCompositePattern(Enum):
    """
    Common patterns for composite Actions.
    
    Composite patterns describe recurring structures in how Actions are
    combined to achieve complex goals.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # SEQUENTIAL PATTERNS
    # =============================================================================
    
    PIPELINE = "pipeline"
    """Actions chained with output feeding into input."""
    
    CHAIN = "chain"
    """Linear sequence of dependent operations."""
    
    FLOW = "flow"
    """Data flow through multiple transformations."""
    
    # =============================================================================
    # PARALLEL PATTERNS
    # =============================================================================
    
    MAP = "map"
    """Apply same operation to multiple targets."""
    
    REDUCE = "reduce"
    """Combine results from parallel operations."""
    
    SCATTER_GATHER = "scatter_gather"
    """Distribute work and collect results."""
    
    # =============================================================================
    # CONDITIONAL PATTERNS
    # =============================================================================
    
    BRANCH = "branch"
    """Conditional execution paths."""
    
    FORK_JOIN = "fork_join"
    """Parallel branches with synchronization."""
    
    RETRY = "retry"
    """Repeat on failure."""
    
    CIRCUIT_BREAKER = "circuit_breaker"
    """Stop after repeated failures."""
    
    # =============================================================================
    # LOOP PATTERNS
    # =============================================================================
    
    ITERATE = "iterate"
    """Repeat until completion condition."""
    
    WHILE = "while"
    """Loop while condition is true."""
    
    UNTIL = "until"
    """Loop until condition becomes true."""
    
    EACH = "each"
    """Process each item in collection."""


# =============================================================================
# COMPOSITION VALIDATION RESULTS
# =============================================================================

class CompositionValidationError(Enum):
    """
    Types of validation errors for composite Actions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    CYCLE_DETECTED = "cycle_detected"
    """Circular dependency detected."""
    
    INCOMPATIBLE_TYPES = "incompatible_types"
    """Incompatible composition types."""
    
    MISSING_DEPENDENCY = "missing_dependency"
    """Required component is missing."""
    
    CONFLICTING_ORDER = "conflicting_order"
    """Conflicting temporal order constraints."""
    
    INVALID_CARDINALITY = "invalid_cardinality"
    """Incorrect number of components."""
    
    # =============================================================================
    # VALIDATION SEVERITIES
    # =============================================================================
    
    ERROR = "error"
    """Error - composition is invalid."""
    
    WARNING = "warning"
    """Warning - composition may be problematic."""
    
    INFO = "info"
    """Info - informational message."""


# =============================================================================
# UTILITY TYPES - Collection types
# =============================================================================

class ActionCompositeReferences(FrozenSet[ActionCompositeReference]):
    """A collection of ActionCompositeReference values."""
    
    def __new__(cls, references: Tuple[ActionCompositeReference, ...] = ()):
        return super().__new__(cls, references)
    
    @classmethod
    def all(cls) -> "ActionCompositeReferences":
        """Get all canonical composite reference types."""
        return cls(tuple(ActionCompositeReference))


class ActionAtomicities(FrozenSet[ActionAtomicity]):
    """A collection of ActionAtomicity values."""
    
    def __new__(cls, atomicities: Tuple[ActionAtomicity, ...] = ()):
        return super().__new__(cls, atomicities)
    
    @classmethod
    def all(cls) -> "ActionAtomicities":
        """Get all canonical atomicity levels."""
        return cls(tuple(ActionAtomicity))


class ActionGranularities(FrozenSet[ActionGranularity]):
    """A collection of ActionGranularity values."""
    
    def __new__(cls, granularities: Tuple[ActionGranularity, ...] = ()):
        return super().__new__(cls, granularities)
    
    @classmethod
    def all(cls) -> "ActionGranularities":
        """Get all canonical granularity levels."""
        return cls(tuple(ActionGranularity))


class ActionCompositePatterns(FrozenSet[ActionCompositePattern]):
    """A collection of ActionCompositePattern values."""
    
    def __new__(cls, patterns: Tuple[ActionCompositePattern, ...] = ()):
        return super().__new__(cls, patterns)
    
    @classmethod
    def all(cls) -> "ActionCompositePatterns":
        """Get all canonical composite patterns."""
        return cls(tuple(ActionCompositePattern))


class CompositionValidationErrors(FrozenSet[CompositionValidationError]):
    """A collection of CompositionValidationError values."""
    
    def __new__(cls, errors: Tuple[CompositionValidationError, ...] = ()):
        return super().__new__(cls, errors)
    
    @classmethod
    def all(cls) -> "CompositionValidationErrors":
        """Get all canonical validation errors."""
        return cls(tuple(CompositionValidationError))


__all__ = [
    "ActionCompositionType",
    "ActionCompositeReference",
    "ActionAtomicity",
    "ActionGranularity",
    "ActionCompositePattern",
    "CompositionValidationError",
    "ActionCompositeReferences",
    "ActionAtomicities",
    "ActionGranularities",
    "ActionCompositePatterns",
    "CompositionValidationErrors",
]