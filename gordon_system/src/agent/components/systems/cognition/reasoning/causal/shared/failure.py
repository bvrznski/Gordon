# Causal Failure - Phase 7.5
# ==========================

"""
Canonical Causal Failure.

Causal failures include unknown mechanisms, missing variables,
cyclic dependencies, contradictory mechanisms, and resource exhaustion.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Kinds of causal reasoning failures."""
    
    UNKNOWN_MECHANISM = "unknown_mechanism"         # Mechanism not in the set
    MISSING_VARIABLE = "missing_variable"           # Variable needed but not defined
    CYCLIC_DEPENDENCY = "cyclic_dependency"         # Causal cycle detected
    CONTRADICTORY_MECHANISMS = "contradictory_mechanisms"  # Conflicting mechanisms
    RESOURCE_EXHAUSTION = "resource_exhaustion"     # Time/memory limit exceeded
    INVALID_GRAPH_STRUCTURE = "invalid_graph_structure"   # Graph is malformed
    TIMEOUT = "timeout"                             # Reasoning took too long
    UNRESOLVABLE_DEPENDENCY = "unresolvable_dependency"    # Dependency cannot be satisfied


@dataclass(frozen=True)
class CausalFailure:
    """
    A failure record for a causal reasoning session.
    
    Failures remain explicit and inspectable.
    """
    
    # Identity
    failure_id: str                     # Unique failure identifier
    
    # Failure kind
    failure_kind: FailureKind           # What type of failure?
    
    # Location
    affected_element: Optional[str] = None  # Which element caused the issue?
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()   # Detailed diagnostic information
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()  # How can this be fixed?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def is_recoverable(self) -> bool:
        """Check if failure has defined recovery options."""
        return len(self.recovery_options) > 0


@dataclass(frozen=True)
class FailureTrace:
    """
    A trace of failures during reasoning.
    
    For debugging and learning from errors.
    """
    
    # Identity
    trace_id: str                       # Unique trace identifier
    
    # All failures encountered
    failure_chain: Tuple[CausalFailure, ...]
    
    # Final outcome
    final_status: str = "failed"        # "completed", "partial", "failed"
    
    @property
    def total_failures(self) -> int:
        """Total number of failures in the trace."""
        return len(self.failure_chain)


def make_causal_failure(
    kind: FailureKind,
    diagnostics: Tuple[str, ...],
    affected_element: Optional[str] = None,
    recovery_options: Tuple[str, ...] = (),
) -> CausalFailure:
    """Create a new causal failure record."""
    return CausalFailure(
        failure_id=f"failure:{uuid.uuid4().hex[:16]}",
        failure_kind=kind,
        affected_element=affected_element,
        diagnostics=diagnostics,
        recovery_options=recovery_options,
    )


__all__ = [
    "FailureKind",
    "CausalFailure",
    "FailureTrace",
]