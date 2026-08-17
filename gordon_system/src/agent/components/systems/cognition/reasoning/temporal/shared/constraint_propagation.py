# Temporal Constraints - Phase 7.8
# ==================================

"""
Canonical Temporal Constraint Propagation.

Temporal constraints define ordering requirements between events and
propagate through event dependencies.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ConstraintType(Enum):
    """Types of temporal constraints."""
    
    MUST_BEFORE = "must_before"             # Event A must occur before event B
    MUST_AFTER = "must_after"               # Event A must occur after event B
    DEADLINE = "deadline"                   # Event must occur by a deadline
    MIN_DURATION = "min_duration"           # Event must last at least X seconds
    MAX_DURATION = "max_duration"           # Event must last at most X seconds
    MUTUAL_EXCLUSION = "mutual_exclusion"   # Events cannot overlap in time


class ConstraintState(Enum):
    """Constraint state during propagation."""
    
    ACTIVE = "active"
    SATISFIED = "satisfied"
    VIOLATED = "violated"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TemporalConstraint:
    """
    Temporal constraint on events.
    
    Constraints include:
        - Must occur before
        - Must occur after
        - Deadline
        - Minimum duration
        - Maximum duration
        - Mutual exclusion
    
    Constraints remain explicit.
    """
    
    # Identity
    constraint_id: str                      # Unique constraint identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Participating events
    participating_event_ids: Tuple[str, ...]  # Events this constraint applies to
    
    # Constraint type and parameters
    constraint_type: ConstraintType         # What kind of constraint?
    constraint_parameters: Dict[str, Any] = field(default_factory=dict)  # Type-specific params
    
    # State during propagation
    state: ConstraintState = ConstraintState.ACTIVE
    
    # Provenance
    source_constraint_id: Optional[str] = None   # If derived from another constraint
    origin_system: str = "unknown"              # Where did the constraint originate?
    
    @property
    def is_binary(self) -> bool:
        """Check if this is a binary constraint (involves two events)."""
        return len(self.participating_event_ids) == 2
    
    @property
    def is_must_order_constraint(self) -> bool:
        """Check if this is a must-before/must-after constraint."""
        return self.constraint_type in (
            ConstraintType.MUST_BEFORE,
            ConstraintType.MUST_AFTER,
        )
    
    def applies_to_event(self, event_id: str) -> bool:
        """Check if this constraint applies to the given event."""
        return event_id in self.participating_event_ids
    
    def get_other_events(self, event_id: str) -> Tuple[str, ...]:
        """Get other events involved in this constraint (excluding the given one)."""
        return tuple(eid for eid in self.participating_event_ids if eid != event_id)
    
    def invert(self) -> TemporalConstraint:
        """Return an inverted version of this constraint."""
        inverse_map = {
            ConstraintType.MUST_BEFORE: ConstraintType.MUST_AFTER,
            ConstraintType.MUST_AFTER: ConstraintType.MUST_BEFORE,
            ConstraintType.MIN_DURATION: ConstraintType.MAX_DURATION,
            ConstraintType.MAX_DURATION: ConstraintType.MIN_DURATION,
        }
        
        new_type = inverse_map.get(self.constraint_type, self.constraint_type)
        return dataclass_replace(
            self,
            constraint_type=new_type,
        )


@dataclass(frozen=True)
class ConstraintPropagation:
    """
    Result of constraint propagation through event dependencies.
    
    Propagation evaluates:
        - Ordering
        - Duration
        - Deadlines
        - Waiting conditions
        - Temporal exclusions
    
    Propagation remains explicit.
    """
    
    # Identity
    propagation_id: str                     # Unique propagation identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Input constraints
    input_constraints: Tuple[TemporalConstraint, ...]
    
    # Propagated constraints
    propagated_constraints: Tuple[TemporalConstraint, ...] = ()
    
    # Affected events
    affected_events: Tuple[str, ...] = ()   # Event IDs affected by propagation
    
    # Resulting schedule (if any)
    resulting_schedule: Optional[Dict[str, float]] = None  # event_id -> start_time
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_propagation_id: Optional[str] = None   # If derived from another propagation
    origin_context: str = "unknown"               # Where did the propagation originate?
    
    @property
    def constraint_count(self) -> int:
        """Return total number of constraints (input + propagated)."""
        return len(self.input_constraints) + len(self.propagated_constraints)
    
    @property
    def has_violations(self) -> bool:
        """Check if any constraints were violated during propagation."""
        return any(c.state == ConstraintState.VIOLATED for c in self.input_constraints)
    
    @property
    def is_consistent(self) -> bool:
        """Check if all active constraints are satisfied."""
        return not self.has_violations
    
    def get_constraint_by_id(self, constraint_id: str) -> Optional[TemporalConstraint]:
        """Get a constraint by its ID."""
        for constraint in self.input_constraints + self.propagated_constraints:
            if constraint.constraint_id == constraint_id:
                return constraint
        return None


@dataclass(frozen=True)
class ConstraintPropagationIdentity:
    """
    Immutable identity for a constraint propagation result.
    
    Allows replay and verification of constraint analysis results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Context
    propagation_number: int = 1               # For repeated propagations
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, propagation_number: int = 1) -> ConstraintPropagationIdentity:
        """Create a new constraint propagation identity."""
        return cls(
            semantic_identity=semantic_identity,
            propagation_number=propagation_number,
        )


# Concurrency Reasoning

class ConcurrencyType(Enum):
    """Types of concurrency relationships."""
    
    TRUE_PARALLEL = "true_parallel"         # Events truly execute in parallel
    LOGICAL_PARALLEL = "logical_parallel"   # Events appear parallel but are interleaved
    SERIALIZATION = "serialization"         # Events must be serialized
    BLOCKING = "blocking"                   # One event blocks another
    RESOURCE_CONTENTION = "resource_contention"  # Events compete for resources
    SYNCHRONIZATION = "synchronization"     # Events synchronize at a point


@dataclass(frozen=True)
class ConcurrencyAnalysis:
    """
    Analysis of concurrent events.
    
    Concurrency analysis evaluates:
        - True parallelism
        - Logical parallelism
        - Serialization
        - Blocking
        - Resource contention
        - Synchronization
    
    Analysis remains explicit.
    """
    
    # Identity
    reasoning_id: str                       # Unique reasoning identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Concurrent event groups
    concurrent_groups: Tuple[Tuple[str, ...], ...] = ()  # Groups of concurrent events
    
    # Synchronization constraints
    synchronization_constraints: Tuple[TemporalConstraint, ...] = ()
    
    # Contention points
    contention_points: Tuple[str, ...] = ()  # Events that cause contention
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_reasoning_id: Optional[str] = None   # If derived from another analysis
    origin_context: str = "unknown"             # Where did the reasoning originate?
    
    @property
    def group_count(self) -> int:
        """Return the number of concurrent event groups."""
        return len(self.concurrent_groups)
    
    @property
    def total_concurrent_events(self) -> int:
        """Return total count of events in concurrent groups."""
        return sum(len(group) for group in self.concurrent_groups)


@dataclass(frozen=True)
class ConcurrencyAnalysisIdentity:
    """
    Immutable identity for a concurrency analysis result.
    
    Allows replay and verification of concurrency analysis results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Context
    analysis_number: int = 1                  # For repeated analyses
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, analysis_number: int = 1) -> ConcurrencyAnalysisIdentity:
        """Create a new concurrency analysis identity."""
        return cls(
            semantic_identity=semantic_identity,
            analysis_number=analysis_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TemporalConstraint",
    "ConstraintPropagation",
    "ConstraintPropagationIdentity",
    "ConcurrencyAnalysis",
    "ConcurrencyAnalysisIdentity",
    "ConstraintType",
    "ConstraintState",
    "ConcurrencyType",
]
