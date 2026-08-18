# Adaptation Failure - Phase 7.25
# ==============================

"""
Canonical Adaptation Failure contract.

Failures include configuration conflicts, policy incompatibility, resource
exhaustion, adaptation instability, rollback failure, and context ambiguity.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Kinds of adaptation failures."""
    
    CONFIGURATION_CONFLICT = "configuration_conflict"
    POLICY_INCOMPATIBILITY = "policy_incompatibility"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    ADAPTATION_INSTABILITY = "adaptation_instability"
    ROLLBACK_FAILURE = "rollback_failure"
    CONTEXT_AMBIGUITY = "context_ambiguity"
    INTEGRATION_ERROR = "integration_error"


@dataclass(frozen=True)
class AdaptationFailure:
    """
    A failure in the adaptation process.
    
    Failures remain explicit and are never silently discarded.
    """
    
    # Identity
    failure_identity: str                 # Unique failure identifier
    
    # Failure kind
    failure_kind: FailureKind             # What type of failure?
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Recovery options
    recovery_options: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle
    created_at_utc: float = field(default_factory=time.time)
    detected_at_utc: Optional[float] = None
    
    @property
    def is_recoverable(self) -> bool:
        """Check if failure has recovery options."""
        return len(self.recovery_options) > 0
    
    @classmethod
    def create(
        cls,
        failure_kind: FailureKind,
        diagnostics: Optional[Dict[str, Any]] = None,
        recovery_options: Optional[List[str]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> AdaptationFailure:
        """Create a new adaptation failure."""
        return cls(
            failure_identity=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            diagnostics=diagnostics or {},
            recovery_options=tuple(recovery_options or []),
            provenance=provenance or {},
            detected_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AdaptationFailure",
    "FailureKind",
]