# Analogy Failure - Phase 7.4
# ==========================

"""
Canonical Analogy Failure Contract.

Failures record when analogical reasoning cannot complete.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class AnalogyFailure:
    """
    An analogy failure with diagnostic information.
    
    Failures include:
        - No suitable source case found
        - Poor structural match
        - Conflicting constraints
        - Domain incompatibility
        - Resource exhaustion
    
    Failures remain explicit; they don't silently terminate sessions.
    """
    
    # Identity
    failure_id: str                           # Unique identifier
    
    # Failure details
    failure_kind: str                         # What type of failure?
    affected_reasoning: str                   # Which reasoning failed?
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None       # Human-readable description
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()    # How might this be recovered?
    
    # Timing
    occurred_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_recoverable(self) -> bool:
        """Check if recovery is possible."""
        return len(self.recovery_options) > 0
    
    @classmethod
    def create(
        cls,
        failure_kind: str,
        affected_reasoning: str,
        diagnostics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        recovery_options: Optional[List[str]] = None,
    ) -> AnalogyFailure:
        """Create a new failure record."""
        return cls(
            failure_id=f"analogy_failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            affected_reasoning=affected_reasoning,
            diagnostics=diagnostics or {},
            error_message=error_message,
            recovery_options=tuple(recovery_options or []),
            occurred_at_utc=time.time(),
        )
    
    def with_diagnostic(self, key: str, value: Any) -> AnalogyFailure:
        """Return a copy with an additional diagnostic."""
        new_diagnostics = dict(self.diagnostics)
        new_diagnostics[key] = value
        return dataclass_replace(
            self,
            diagnostics=new_diagnostics,
        )


@dataclass(frozen=True)
class FailureKind:
    """
    Predefined failure kinds for consistent failure reporting.
    """
    
    NO_SUITABLE_SOURCE_CASE: str = "no_suitable_source_case"
    POOR_STRUCTURAL_MATCH: str = "poor_structural_match"
    CONFLICTING_CONSTRAINTS: str = "conflicting_constraints"
    DOMAIN_INCOMPATIBILITY: str = "domain_incompatibility"
    RESOURCE_EXHAUSTION: str = "resource_exhaustion"
    CONSTRAINT_VIOLATION: str = "constraint_violation"
    NO_VALID_MAPPING_FOUND: str = "no_valid_mapping_found"


FAILURE_KINDS = FailureKind()


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AnalogyFailure",
    "FAILURE_KINDS",
]