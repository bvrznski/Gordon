# Temporal Health - Phase 7.8
# ===========================

"""
Canonical Temporal Health.

Health metrics describe:
    - Events analyzed
    - Intervals processed
    - Constraint violations
    - Ordering corrections
    - Concurrency groups
    - Validation success
    - Diagnostics
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class TemporalHealth:
    """
    Health status of temporal reasoning operations.
    
    Health remains descriptive - it never prescribes actions.
    """
    
    # Identity
    health_id: str                          # Unique health identifier
    
    # Metrics
    events_analyzed: int = 0                # Number of events analyzed
    intervals_processed: int = 0            # Number of intervals processed
    constraint_violations: int = 0          # Violation count
    ordering_corrections: int = 0           # Ordering fixes made
    concurrency_groups: int = 0             # Concurrent event groups found
    validation_success: bool = False        # Validation passed?
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()       # Health-related diagnostics
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_health_id: Optional[str] = None  # If derived from another health check
    origin_context: str = "unknown"         # Where did the health check originate?
    
    @property
    def total_operations(self) -> int:
        """Return total number of operations performed."""
        return self.events_analyzed + self.intervals_processed
    
    @property
    def has_issues(self) -> bool:
        """Check if any health issues are present."""
        return self.constraint_violations > 0 or not self.validation_success
    
    def get_metric(self, metric_name: str) -> int:
        """Get a specific metric value."""
        return getattr(self, metric_name, 0)


@dataclass(frozen=True)
class TemporalHealthIdentity:
    """
    Immutable identity for temporal health status.
    
    Allows replay and verification of health check results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Context
    health_number: int = 1                    # For repeated health checks
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, health_number: int = 1) -> TemporalHealthIdentity:
        """Create a new temporal health identity."""
        return cls(
            semantic_identity=semantic_identity,
            health_number=health_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TemporalHealth",
    "TemporalHealthIdentity",
]