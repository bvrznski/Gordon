# Legal Failure - Phase 7.47 Part 1
# ==================================

"""
Failure Contract.

Legal failures include:
    - missing jurisdiction
    - conflicting authorities
    - ambiguous interpretation
    - obsolete legislation
    - missing facts
    - conflicting precedents

Failures remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class LegalFailure:
    """
    A legal reasoning failure with diagnostic information.
    
    A failure includes:
        - Failure category/kind
        - Diagnostics explaining the issue
        - Recovery options if available
        - Provenance tracking
    
    Failures are never silently discarded.
    """
    
    # Identity
    failure_id: str                           # Unique identifier
    
    # Type
    failure_kind: str                         # e.g., "missing_jurisdiction", "conflicting_authorities"
    
    # Location
    affected_component_type: Optional[str] = None  # What failed?
    affected_component_id: Optional[str] = None    # Which component?
    
    # Diagnostics
    diagnostic_message: str = ""              # Human-readable explanation
    error_details: Dict[str, Any] = field(default_factory=dict)  # Structured details
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()    # How can this be fixed?
    
    # Timing
    occurred_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        failure_kind: str,
        diagnostic_message: str,
    ) -> LegalFailure:
        """Create a new legal failure."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            diagnostic_message=diagnostic_message,
        )
    
    def with_recovery_options(self, options: List[str]) -> LegalFailure:
        """Add recovery options to the failure."""
        return dataclass_replace(
            self,
            recovery_options=tuple(options),
        )


@dataclass(frozen=True)
class FailureManager:
    """
    Manager for legal reasoning failures.
    
    Tracks all failures and their diagnostics.
    """
    
    manager_id: str                           # Unique identifier
    
    # Known failures
    failures: Dict[str, LegalFailure] = field(default_factory=dict)  # ID -> failure
    
    # Failure statistics
    failure_counts: Dict[str, int] = field(default_factory=dict)  # kind -> count
    
    # Recovery tracking
    recovered_failures: Tuple[str, ...] = ()
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
    ) -> FailureManager:
        """Create a new failure manager."""
        return cls(
            manager_id=f"failure_manager:{uuid.uuid4().hex[:16]}",
        )
    
    def add_failure(self, failure: LegalFailure) -> FailureManager:
        """Add a failure to the manager."""
        # Update counts
        counts = dict(self.failure_counts)
        counts[failure.failure_kind] = counts.get(failure.failure_kind, 0) + 1
        
        new_failures = dict(self.failures)
        new_failures[failure.failure_id] = failure
        
        return dataclass_replace(
            self,
            failures=new_failures,
            failure_counts=counts,
        )
    
    def get_failures_by_kind(
        self,
        kind: str,
    ) -> Tuple[LegalFailure, ...]:
        """Get all failures of a specific kind."""
        return tuple(f for f in self.failures.values() if f.failure_kind == kind)
    
    def mark_as_recovered(self, failure_id: str) -> FailureManager:
        """Mark a failure as recovered."""
        return dataclass_replace(
            self,
            recovered_failures=self.recovered_failures + (failure_id,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "LegalFailure",
    "FailureManager",
]