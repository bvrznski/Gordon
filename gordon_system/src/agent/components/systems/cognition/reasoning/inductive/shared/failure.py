# Induction Failure - Phase 7.2
# =============================

"""
Canonical Induction Failure Contract.

Failures in induction include insufficient data, bias, and other problems.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class InductionFailureKind(Enum):
    """Kinds of induction failures."""
    
    INSUFFICIENT_OBSERVATIONS = "insufficient_observations"
    SAMPLING_BIAS = "sampling_bias"
    LOW_CONFIDENCE = "low_confidence"
    WEAK_STATISTICAL_SUPPORT = "weak_statistical_support"
    RESOURCE_LIMIT = "resource_limit"
    INVALID_INPUT = "invalid_input"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class InductionFailure:
    """
    Record of an induction failure.
    
    A failure record includes:
        - Kind of failure
        - Diagnostics about what went wrong
        - Recovery options (if available)
        - Provenance tracking
    
    Failures remain explicit and inspectable.
    """
    
    # Identity
    failure_identity: str                 # Unique identifier for this failure
    
    # Failure details
    failure_kind: InductionFailureKind    # What kind of failure?
    error_message: str                    # Human-readable description
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)  # Detailed diagnostic info
    
    # Recovery options (if any)
    recovery_options: Tuple[str, ...] = ()  # Possible ways to recover
    
    # Context
    context_observations_analyzed: int = 0  # How many observations were processed?
    context_patterns_found: int = 0         # How many patterns were discovered?
    
    # Timing
    failure_time_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None  # When did the session start?
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_recoverable(self) -> bool:
        """Check if this failure has potential recovery options."""
        return len(self.recovery_options) > 0
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if started and failed timestamps available."""
        if self.started_at_utc:
            return self.failure_time_utc - self.started_at_utc
        return 0.0


@dataclass(frozen=True)
class FailureTrace:
    """
    Trace of failure events for debugging.
    
    Each trace entry records a step where something went wrong.
    """
    
    # Identity
    trace_id: str                         # Unique trace identifier
    
    # Step information
    step_number: int                      # Order in sequence
    step_kind: str                        # e.g., "observation_processing", "pattern_search"
    
    # Failure context
    error_type: str                       # Type of error that occurred
    error_message: str                    # Description of the error
    
    # Timing
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create_step(
        cls,
        trace_id: str,
        step_number: int,
        step_kind: str,
        error_type: str,
        error_message: str,
    ) -> FailureTrace:
        """Create a new failure trace step."""
        return cls(
            trace_id=trace_id,
            step_number=step_number,
            step_kind=step_kind,
            error_type=error_type,
            error_message=error_message,
            timestamp_utc=time.time(),
        )


@dataclass(frozen=True)
class PartialAnalysis:
    """
    Record of partial induction analysis that did not complete.
    
    Allows reconstruction of what was accomplished before failure.
    """
    
    # Identity
    analysis_id: str                      # Unique identifier
    
    # Analysis metadata
    total_steps_expected: int = 0         # How many steps in full process?
    steps_completed: int = 0              # How many completed before failure?
    final_state_reached: str = "unknown"  # Where did it stop?
    
    # Results obtained
    observations_analyzed: Tuple[str, ...] = ()  # Which observations were processed?
    patterns_discovered: Tuple[str, ...] = ()    # Which patterns found?
    confidence_estimates: Dict[str, float] = field(default_factory=dict)  # Confidence scores
    
    # Failure point
    failure_step: Optional[str] = None    # What step failed?
    failure_reason: Optional[str] = None  # Why did it fail?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)


__all__ = [
    "InductionFailure",
    "InductionFailureKind",
    "FailureTrace",
    "PartialAnalysis",
]