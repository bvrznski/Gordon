# Introspection Failure - Phase 7.29
# ===================================

"""
Introspection Failures capture when introspection cannot complete.

Failures include:
    - Missing telemetry
    - Inconsistent self-model
    - Observation ambiguity
    - Resource uncertainty
    - Conflicting subsystem reports
    - Identity inconsistency

Failures remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class IntrospectionFailure:
    """
    Failure of introspection reasoning.
    
    A failure contains:
        - Explicit identity
        - Failure kind (what went wrong?)
        - Diagnostics (supporting evidence)
        - Recovery options
        - Provenance tracking
    
    Failures remain independently inspectable.
    """
    
    # Identity
    failure_id: str                           # Unique identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Failure kind
    failure_kind: str = "unknown"             # See FAILURE_KINDS below
    
    # Diagnostics
    diagnostic_evidence: List[Dict[str, Any]] = field(default_factory=list)  # Supporting evidence
    affected_components: List[str] = field(default_factory=list)  # What failed?
    
    # Recovery options
    recovery_options: List[str] = field(default_factory=list)  # How can we recover?
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        failure_kind: str = "unknown",
    ) -> IntrospectionFailure:
        """Create a new introspection failure record."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            failure_kind=failure_kind,
        )
    
    def with_diagnostics(self, diagnostics: List[Dict[str, Any]]) -> IntrospectionFailure:
        """Return a copy with added diagnostics."""
        return dataclass_replace(
            self,
            diagnostic_evidence=self.diagnostic_evidence + diagnostics,
        )


FAILURE_KINDS = {
    "telemetry_missing": "Required telemetry is unavailable",
    "model_inconsistent": "Self-model contains conflicting information",
    "observation_ambiguous": "Observation lacks clear interpretation",
    "resource_uncertain": "Resource state cannot be determined",
    "subsystem_conflict": "Subsystems report inconsistent states",
    "identity_inconsistent": "Identity definition is ambiguous",
}


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "IntrospectionFailure",
    "FAILURE_KINDS",
]