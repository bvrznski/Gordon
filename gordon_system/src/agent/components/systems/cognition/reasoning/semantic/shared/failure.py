# Semantic Failure - Phase 7.10
# ==============================

"""
Canonical Semantic Failure contracts.

Semantic failures include:
    - Missing ontology
    - Contradictory concepts
    - Inheritance conflicts
    - Undefined concepts
    - Resource exhaustion

Failures remain explicit and inspectable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class SemanticFailure:
    """
    Semantic failure record.
    
    A SemanticFailure contains:
        - Failure identity
        - Failure kind
        - Diagnostics
        - Recovery options
        - Provenance tracking
    
    Failures remain explicit and reconstructable.
    """
    
    # Identity
    failure_id: str                         # Unique identifier
    
    # Reasoning goal at time of failure
    reasoning_goal: str                     # What were we trying to reason about?
    
    # Failure kind
    failure_kind: str                       # e.g., "missing_ontology", "contradiction"
    
    # Diagnostics
    diagnostics: Tuple[DiagnosticsRecord, ...] = ()
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()  # Possible ways to recover
    
    # Partial results (if any)
    partial_results: Optional[Dict[str, Any]] = None
    
    # State
    state: str = "failed"
    
    # Timing
    failed_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        reasoning_goal: str,
        failure_kind: str,
    ) -> SemanticFailure:
        """Create a new semantic failure record."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            reasoning_goal=reasoning_goal,
            failure_kind=failure_kind,
        )
    
    def with_recovery_options(self, options: List[str]) -> SemanticFailure:
        """Add recovery options."""
        new_options = tuple(self.recovery_options) + tuple(options)
        return dataclass_replace(
            self,
            recovery_options=new_options,
        )


@dataclass(frozen=True)
class DiagnosticsRecord:
    """
    Diagnostic record from semantic failure.
    """
    
    diagnostic_id: str                      # Unique identifier
    diagnostic_type: str                    # e.g., "missing", "conflict"
    message: str                            # Diagnostic message
    severity: str = "error"                 # error, warning, info
    
    @classmethod
    def missing(cls, item: str) -> DiagnosticsRecord:
        """Create a missing item diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="missing",
            message=f"{item} not found",
            severity="error",
        )
    
    @classmethod
    def conflict(cls, items: List[str], details: str) -> DiagnosticsRecord:
        """Create a conflict diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="conflict",
            message=f"Conflict between {', '.join(items)}: {details}",
            severity="error",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SemanticFailure",
    "DiagnosticsRecord",
]