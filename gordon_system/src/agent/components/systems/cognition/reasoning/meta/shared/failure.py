# Meta Reasoning Failure - Phase 7.13
# =====================================

"""
Canonical Meta-Reasoning Failure definition.

Failure handling captures when meta-reasoning execution encounters problems.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Kinds of meta-reasoning failures."""
    
    # Reasoner failures
    REASONER_DEADLOCK = "reasoner_deadlock"       # Reasoner stuck in infinite loop
    REASONER_ERROR = "reasoner_error"             # Reasoner execution error
    
    # Resource failures
    RESOURCE_EXHAUSTION = "resource_exhaustion"   # Out of resources
    TIMEOUT = "timeout"                           # Time budget exceeded
    
    # Orchestration failures
    ORCHESTRATION_FAILURE = "orchestration_failure"  # Orchestration failure
    POLICY_CONFLICT = "policy_conflict"           # Conflicting policies
    
    # Validation failures
    VALIDATION_FAILED = "validation_failed"       # Validation failed


@dataclass(frozen=True)
class RecoveryOptions:
    """
    Options for recovering from a failure.
    
    Recovery options are explicit and inspectable alternatives.
    """
    
    # Identity
    recovery_id: str                        # Unique recovery identifier
    
    # Recovery strategy
    strategy: str                           # What to do?
    rationale: str = ""                     # Why this approach?
    
    # Expected impact
    expected_success_rate: float = 0.5      # 0-1 probability of success


@dataclass(frozen=True)
class MetaReasoningFailure:
    """
    Failure in meta-reasoning execution.
    
    A failure contains:
        - Identity and kind
        - Diagnostics (when available)
        - Recovery options
        - Provenance tracking
    
    Failures remain explicit and reconstructable.
    """
    
    # Identity
    failure_id: str                         # Unique failure identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Failure details
    kind: FailureKind                       # What type of failure?
    message: str = ""                       # Human-readable description
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)  # Execution context
    
    # Diagnostics
    diagnostics: List[str] = field(default_factory=list)   # Diagnostic info
    trace_ids: List[str] = field(default_factory=list)     # Related trace IDs
    
    # Recovery
    recovery_options: List[RecoveryOptions] = field(default_factory=list)
    
    # Timing
    occurred_at_utc: float = field(default_factory=time.time)
    resolved_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate how long until resolution."""
        if self.resolved_at_utc:
            return self.resolved_at_utc - self.occurred_at_utc
        return 0.0
    
    @classmethod
    def create(
        cls,
        kind: FailureKind,
        message: str = "",
        semantic_identity: Optional[str] = None,
    ) -> MetaReasoningFailure:
        """Create a new failure."""
        if semantic_identity is None:
            semantic_identity = f"failure:{uuid.uuid4().hex[:16]}"
        
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            kind=kind,
            message=message,
        )
    
    def with_context(self, context: Dict[str, Any]) -> MetaReasoningFailure:
        """Add execution context and return updated failure."""
        new_context = dict(self.context)
        new_context.update(context)
        return dataclass_replace(
            self,
            context=new_context,
        )
    
    def with_diagnostics(self, diagnostics: List[str]) -> MetaReasoningFailure:
        """Add diagnostics and return updated failure."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + diagnostics,
        )
    
    def add_recovery_option(self, option: RecoveryOptions) -> MetaReasoningFailure:
        """Add a recovery option and return updated failure."""
        return dataclass_replace(
            self,
            recovery_options=self.recovery_options + [option],
        )
    
    def to_resolved(self, resolved_at_utc: Optional[float] = None) -> MetaReasoningFailure:
        """Mark failure as resolved."""
        if resolved_at_utc is None:
            resolved_at_utc = time.time()
        return dataclass_replace(
            self,
            resolved_at_utc=resolved_at_utc,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MetaReasoningFailure",
    "FailureKind",
    "RecoveryOptions",
]