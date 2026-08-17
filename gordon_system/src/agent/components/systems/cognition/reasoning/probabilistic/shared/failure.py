# Probabilistic Failure - Phase 7.7
# ==================================

"""
Canonical failure contracts for probabilistic reasoning.

Failures remain explicit and never silently discard evidence.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class FailureKind(Enum):
    """Kinds of probabilistic failures."""
    
    MISSING_PRIOR = "missing_prior"                 # No prior distribution available
    INVALID_DISTRIBUTION = "invalid_distribution"   # Distribution parameters invalid
    INCONSISTENT_EVIDENCE = "inconsistent_evidence" # Evidence contradicts itself
    DEPENDENCY_CYCLE = "dependency_cycle"           # Circular dependency detected
    RESOURCE_EXHAUSTED = "resource_exhausted"       # Time/memory limits exceeded
    LIKELIHOOD_UNDEFINED = "likelihood_undefined"   # Cannot compute likelihood


@dataclass(frozen=True)
class ProbabilisticFailure:
    """
    A probabilistic failure with diagnostic information.
    
    Failures may include:
        - Missing priors
        - Invalid distributions
        - Inconsistent evidence
        - Dependency cycles
        - Resource exhaustion
    
    Failures remain explicit; they don't silently terminate sessions.
    """
    
    # Identity
    failure_id: str                         # Unique identifier
    
    # Failure details
    failure_kind: FailureKind               # What type of failure?
    affected_reasoning: str                 # Which reasoning failed?
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None     # Human-readable description
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()  # How might this be recovered?
    
    # Timing
    occurred_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_recoverable(self) -> bool:
        """Check if recovery is possible."""
        return len(self.recovery_options) > 0
    
    @classmethod
    def create(
        cls,
        failure_kind: FailureKind,
        affected_reasoning: str,
        diagnostics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        recovery_options: Optional[List[str]] = None,
    ) -> ProbabilisticFailure:
        """Create a new failure record."""
        return cls(
            failure_id=f"prob_failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            affected_reasoning=affected_reasoning,
            diagnostics=diagnostics or {},
            error_message=error_message,
            recovery_options=tuple(recovery_options or []),
            occurred_at_utc=time.time(),
        )
    
    def with_diagnostic(self, key: str, value: Any) -> ProbabilisticFailure:
        """Return a copy with an additional diagnostic."""
        new_diagnostics = dict(self.diagnostics)
        new_diagnostics[key] = value
        return dataclass_replace(
            self,
            diagnostics=new_diagnostics,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ProbabilisticFailure",
    "FailureKind",
]