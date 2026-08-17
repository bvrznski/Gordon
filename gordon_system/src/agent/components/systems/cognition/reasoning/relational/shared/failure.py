# Relational Failure - Phase 7.11
# =================================

"""
Canonical Relational Failure.

Failures include missing entities, conflicting relations, invalid graph topology,
constraint violations, and resource exhaustion.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Kinds of relational failures."""
    
    MISSING_ENTITIES = "missing_entities"               # Required entities not found
    CONFLICTING_RELATIONS = "conflicting_relations"     # Relations contradict each other
    INVALID_TOPOLOGY = "invalid_topology"               # Graph structure invalid
    CONSTRAINT_VIOLATION = "constraint_violation"       # Constraints not satisfied
    RESOURCE_EXHAUSTED = "resource_exhausted"           # Resource limits exceeded


@dataclass(frozen=True)
class RelationalFailure:
    """
    Explicit relational failure with diagnostics and recovery options.
    
    Failures remain explicit and never silently discard graph components.
    """
    
    # Identity
    failure_id: str                       # Unique failure identifier
    
    # Failure kind
    failure_kind: FailureKind             # What kind of failure occurred?
    
    # Diagnostics (why did it fail?)
    diagnostics: Tuple[str, ...] = ()     # Detailed diagnostic information
    
    # Recovery options (how can it be fixed?)
    recovery_options: Tuple[str, ...] = ()   # Available recovery strategies
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from session
    
    @classmethod
    def create(
        cls,
        failure_kind: FailureKind = FailureKind.CONSTRAINT_VIOLATION,
    ) -> RelationalFailure:
        """Create a new relational failure."""
        return cls(
            failure_id=f"relational_failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            created_at_utc=time.time(),
        )
    
    def add_diagnostic(self, diagnostic: str) -> RelationalFailure:
        """Add a diagnostic message."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + (diagnostic,),
        )
    
    def add_recovery_option(self, option: str) -> RelationalFailure:
        """Add a recovery option."""
        return dataclass_replace(
            self,
            recovery_options=self.recovery_options + (option,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RelationalFailure",
    "FailureKind",
]