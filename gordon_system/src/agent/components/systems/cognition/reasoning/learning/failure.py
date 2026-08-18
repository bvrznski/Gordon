# Learning Failure - Phase 7.24
# =============================

"""
Canonical Learning Failure Contract.

Learning Failures record when learning cannot complete.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class LearningFailure:
    """
    A learning failure with diagnostic information.
    
    Failures may include:
        - Insufficient evidence
        - Invalid generalization
        - Model refinement errors
        - Integration conflicts
        - Resource limits
    
    Failures remain explicit; they don't silently terminate sessions.
    """
    
    # Identity
    failure_id: str                           # Unique identifier
    
    # Failure details
    failure_kind: str                         # What type of failure?
    affected_learning: str                    # Which learning failed?
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None       # Human-readable description
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()    # How might this be recovered?
    
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
        failure_kind: str,
        affected_learning: str,
        diagnostics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        recovery_options: Optional[List[str]] = None,
    ) -> LearningFailure:
        """Create a new failure record."""
        return cls(
            failure_id=f"learning_failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            affected_learning=affected_learning,
            diagnostics=diagnostics or {},
            error_message=error_message,
            recovery_options=tuple(recovery_options or []),
            occurred_at_utc=time.time(),
        )
    
    def with_diagnostic(self, key: str, value: Any) -> LearningFailure:
        """Return a copy with an additional diagnostic."""
        new_diagnostics = dict(self.diagnostics)
        new_diagnostics[key] = value
        return dataclass_replace(
            self,
            diagnostics=new_diagnostics,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "LearningFailure",
]