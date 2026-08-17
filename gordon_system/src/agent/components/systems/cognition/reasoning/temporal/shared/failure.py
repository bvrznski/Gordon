# Temporal Failure - Phase 7.8
# ============================

"""
Canonical Temporal Failure.

Temporal failures include missing timestamps, conflicting orderings,
clock inconsistencies, impossible intervals, constraint violations,
and resource exhaustion.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Kinds of temporal failures."""
    
    MISSING_TIMESTAMP = "missing_timestamp"               # Event lacks timestamp
    CONFLICTING_ORDERINGS = "conflicting_orderings"       # Orderings contradict
    CLOCK_INCONSISTENCY = "clock_inconsistency"           # Clock drift detected
    IMPOSSIBLE_INTERVAL = "impossible_interval"           # Interval has invalid bounds
    CONSTRAINT_VIOLATION = "constraint_violation"         # Temporal constraint failed
    RESOURCE_EXHAUSTION = "resource_exhaustion"           # System resources exhausted


@dataclass(frozen=True)
class TemporalFailure:
    """
    Record of a temporal failure.
    
    Failures remain explicit - never silently discarded.
    """
    
    # Identity
    failure_id: str                         # Unique failure identifier
    
    # Failure kind
    failure_kind: FailureKind              # What kind of failure?
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()       # Details about the failure
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()  # Possible recovery strategies
    
    # Provenance
    source_failure_id: Optional[str] = None   # If derived from another failure
    origin_context: str = "unknown"           # Where did the failure originate?
    
    @property
    def has_diagnostics(self) -> bool:
        """Check if diagnostic information is available."""
        return len(self.diagnostics) > 0
    
    @property
    def has_recovery_options(self) -> bool:
        """Check if recovery options are available."""
        return len(self.recovery_options) > 0


@dataclass(frozen=True)
class TemporalFailureIdentity:
    """
    Immutable identity for a temporal failure.
    
    Allows replay and verification of failure handling results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Context
    failure_number: int = 1                   # For repeated failures
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, failure_number: int = 1) -> TemporalFailureIdentity:
        """Create a new temporal failure identity."""
        return cls(
            semantic_identity=semantic_identity,
            failure_number=failure_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TemporalFailure",
    "TemporalFailureIdentity",
    "FailureKind",
]