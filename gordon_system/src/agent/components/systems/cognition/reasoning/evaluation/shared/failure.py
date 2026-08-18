# Evaluation Failure - Phase 7.23
# ==============================

"""
Evaluation Failure handling for Gordon's Evaluation Reasoning subsystem.

Failures include:
- Missing observations
- Invalid metrics
- Conflicting evidence
- Undefined expectations
- Insufficient confidence
- Evaluation ambiguity
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Kinds of evaluation failures."""
    
    OBSERVATION_MISSING = "observation_missing"        # Required observation not available
    METRIC_INVALID = "metric_invalid"                  # Metric calculation failed
    EVIDENCE_CONFLICTING = "evidence_conflicting"      # Contradictory evidence found
    EXPECTATIONS_UNDEFINED = "expectations_undefined"  # No reference expectations
    CONFIDENCE_INSUFFICIENT = "confidence_insufficient"  # Low confidence in data
    AMBIGUOUS_RESULT = "ambiguous_result"              # Result unclear or indeterminate


@dataclass(frozen=True)
class EvaluationFailure:
    """
    A record of evaluation failure details.
    
    A failure contains:
        - Failure identity and kind
        - Diagnostics explaining what went wrong
        - Recovery options (if available)
        - Provenance tracking
    
    Failures remain explicit and independently inspectable.
    """
    
    # Identity
    failure_id: str                   # Unique failure identifier
    semantic_identity: str            # Semantic identity for traceability
    
    # Failure details
    failure_kind: FailureKind         # What kind of failure?
    failure_description: str          # Human-readable description
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Recovery options
    recovery_options: List[str] = field(default_factory=list)  # Possible recovery actions
    
    # Metadata
    detected_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_failure_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def is_recoverable(self) -> bool:
        """Check if failure might be recoverable."""
        return len(self.recovery_options) > 0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        failure_kind: FailureKind,
        failure_description: str,
        diagnostics: Optional[Dict[str, Any]] = None,
        recovery_options: Optional[List[str]] = None,
        origin_context: str = "unknown",
        source_failure_id: Optional[str] = None,
    ) -> EvaluationFailure:
        """Create a new evaluation failure record."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            failure_kind=failure_kind,
            failure_description=failure_description,
            diagnostics=dict(diagnostics or {}),
            recovery_options=list(recovery_options or []),
            origin_context=origin_context,
            source_failure_id=source_failure_id,
            detected_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "FailureKind",
    "EvaluationFailure",
]