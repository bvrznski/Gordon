# Hypothetical Failure - Phase 7.15 Part 2
# ==========================================

"""
Canonical Hypothetical Failure Contract.

Failures include contradictory assumptions, inconsistent possibility spaces,
unsatisfiable constraints, runaway expansion, and resource exhaustion.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class HypotheticalFailureKind(Enum):
    """Kinds of hypothetical reasoning failures."""
    
    CONTRADICTORY_ASSUMPTIONS = "contradictory_assumptions"     # Conflicting assumptions
    INCONSISTENT_SPACE = "inconsistent_space"                   # Inconsistent possibility space
    UNSATISFIABLE_CONSTRAINTS = "unsatisfiable_constraints"     # No valid solutions
    RUNAWAY_EXPANSION = "runaway_expansion"                     # Too many candidates
    RESOURCE_EXHAUSTED = "resource_exhausted"                   # Out of resources


@dataclass(frozen=True)
class HypotheticalFailure:
    """
    Record of a hypothetical reasoning failure.
    
    Failures remain explicit and inspectable at all times.
    """
    
    # Identity
    failure_id: str                           # Unique identifier
    
    # Failure details
    failure_kind: HypotheticalFailureKind     # What kind of failure?
    failure_statement: str                    # Description of the failure
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)  # Diagnostic info
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()    # How might this be recovered?
    
    # Metadata
    occurred_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_recoverable(self) -> bool:
        """Check if failure has possible recovery paths."""
        return len(self.recovery_options) > 0
    
    @classmethod
    def create(
        cls,
        failure_kind: HypotheticalFailureKind,
        failure_statement: str,
        diagnostics: Optional[Dict[str, Any]] = None,
        recovery_options: Optional[List[str]] = None,
    ) -> HypotheticalFailure:
        """Create a new hypothetical failure."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            failure_statement=failure_statement,
            diagnostics=diagnostics or {},
            recovery_options=tuple(recovery_options or []),
        )


@dataclass(frozen=True)
class FailureTrace:
    """
    Trace of failures during hypothetical reasoning.
    
    Allows reconstruction of partial results from failed sessions.
    """
    
    # Identity
    trace_id: str                             # Unique identifier
    
    # Failures in order
    failure_sequence: Tuple[HypotheticalFailure, ...] = ()  # All failures
    
    # Partial state (what was generated before failure)
    partial_state: Dict[str, Any] = field(default_factory=dict)  # Partial results
    
    @property
    def total_failures(self) -> int:
        """Return number of failures in trace."""
        return len(self.failure_sequence)
    
    @classmethod
    def create(
        cls,
        failure_sequence: Optional[List[HypotheticalFailure]] = None,
        partial_state: Optional[Dict[str, Any]] = None,
    ) -> FailureTrace:
        """Create a new failure trace."""
        return cls(
            trace_id=f"failure_trace:{uuid.uuid4().hex[:16]}",
            failure_sequence=tuple(failure_sequence or []),
            partial_state=partial_state or {},
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "HypotheticalFailureKind",
    "HypotheticalFailure",
    "FailureTrace",
]