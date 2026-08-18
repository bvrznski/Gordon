# Social Failure - Phase 7.32
# ===========================

"""
Canonical Social Failure definitions.

Failures include:
- Insufficient observations
- Incorrect agent identity  
- Belief ambiguity
- Intention ambiguity
- Relationship inconsistency
- Prediction uncertainty

Failures remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class SocialFailure:
    """
    Social failure result.
    
    Represents a failure in social reasoning with:
        - Failure identity (stable identifier)
        - Failure kind (type of failure)
        - Diagnostics (why it happened)
        - Recovery options (how to recover)
        
    Failures never silently discard reasoning history.
    """
    
    # Identity
    failure_id: str                           # Unique identifier
    
    # Failure details
    failure_kind: str                         # The type of failure
    timestamp_utc: float                      # When did it occur?
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Recovery options (what could be done differently)
    recovery_options: Tuple[str, ...] = ()
    
    @classmethod
    def create(
        cls,
        failure_kind: str,
        diagnostics: Optional[Dict[str, Any]] = None,
    ) -> SocialFailure:
        """Create a new social failure record."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            timestamp_utc=time.time(),
            diagnostics=diagnostics or {},
        )
    
    def with_recovery_option(self, option: str) -> SocialFailure:
        """Return a copy with an additional recovery option."""
        return dataclass_replace(
            self,
            recovery_options=self.recovery_options + (option,),
        )


@dataclass(frozen=True)
class AgentModelPartial:
    """
    A partial agent model produced when full reasoning fails.
    
    Contains whatever was successfully inferred before failure,
    allowing reconstruction of what was possible.
    """
    
    model_id: str                             # Unique identifier
    agent_id: str                            # Which agent?
    created_at_utc: float                    # When was this created?
    
    available_inferences: Dict[str, Any] = field(default_factory=dict)
    incomplete_reasons: Tuple[str, ...] = ()
    confidence_on_available: float = 0.0
    
    @property
    def is_partially_complete(self) -> bool:
        """Check if some inferences were successful."""
        return len(self.available_inferences) > 0


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SocialFailure",
    "AgentModelPartial",
]