# Explanation Failure - Phase 7.14
# ================================

"""
Explanation failure handling for explanatory reasoning.

Failures include:
    - Insufficient evidence
    - Unsupported claims
    - Contradictory justifications
    - Incomplete reasoning
    - Resource exhaustion
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Kinds of explanation failures."""
    
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"   # Not enough evidence
    UNSUPPORTED_CLAIMS = "unsupported_claims"        # Claims lack support
    CONTRADICTORY_JUSTIFICATIONS = "contradictory_justifications"  # Conflicting justifications
    INCOMPLETE_REASONING = "incomplete_reasoning"     # Reasoning gaps remain
    RESOURCE_EXHAUSTED = "resource_exhausted"         # Ran out of resources
    INVALID_INPUT = "invalid_input"                   # Bad input data


@dataclass(frozen=True)
class FailureIdentity:
    """
    Immutable identity for an explanation failure.
    """
    
    semantic_identity: str                    # Stable identity across runs
    failure_number: int = 1                   # For repeated failures
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, failure_number: int = 1) -> FailureIdentity:
        """Create a new failure identity."""
        return cls(
            semantic_identity=semantic_identity,
            failure_number=failure_number,
        )


@dataclass(frozen=True)
class ExplanationFailure:
    """
    Record of an explanation failure.
    
    Failures remain explicit and inspectable with full diagnostics
    and potential recovery options.
    """
    
    # Identity
    failure_id: str                           # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Failure details
    failure_kind: FailureKind                 # What kind of failure?
    diagnostics: Tuple[Dict[str, Any], ...]   # Diagnostic information
    
    # Recovery options (what could fix it?)
    recovery_options: Tuple[str, ...]         # How to recover?
    
    # Process tracking
    failed_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_recoverable(self) -> bool:
        """Check if failure can be recovered."""
        return len(self.recovery_options) > 0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        failure_kind: FailureKind,
        diagnostics: List[Dict[str, Any]],
        recovery_options: Optional[List[str]] = None,
    ) -> "ExplanationFailure":
        """Create a new failure record."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            failure_kind=failure_kind,
            diagnostics=tuple(diagnostics),
            recovery_options=tuple(recovery_options or []),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "FailureIdentity",
    "ExplanationFailure",
    "FailureKind",
]