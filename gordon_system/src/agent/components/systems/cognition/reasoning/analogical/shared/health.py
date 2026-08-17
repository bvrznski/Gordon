# Analogy Health - Phase 7.4
# =========================

"""
Canonical Analogy Health Contract.

Health metrics describe the state and effectiveness of analogical reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class AnalogyHealth:
    """
    Health metrics for an analogy session.
    
    Metrics include:
        - Cases retrieved (how many candidates found?)
        - Mapping quality (how good are the mappings?)
        - Transfer success rate (what transfers actually work?)
        - Schema reuse (are schemas being reused effectively?)
        - Analogy precision (are analogies accurate?)
        - Validation success (what passes validation?)
        - Diagnostics (any issues to address?)
    """
    
    # Identity
    health_id: str                            # Unique identifier
    
    # Cases and retrieval metrics
    cases_retrieved: int = 0                  # Total candidates found
    cases_evaluated: int = 0                  # How many were considered?
    
    # Mapping quality
    average_mapping_quality: float = 0.0      # Mean mapping score
    top_mapping_quality: float = 0.0          # Best mapping score
    
    # Transfer metrics
    transfers_attempted: int = 0              # How many transfer proposals?
    transfers_validated: int = 0              # How many validated?
    transfer_success_rate: float = 0.0        # % that passed validation
    
    # Schema reuse
    schemas_extracted: int = 0                # New schemas found
    schemas_reused: int = 0                   # Previously known schemas
    schema_reuse_rate: float = 0.0            # % reused vs new
    
    # Validation metrics
    validations_run: int = 0                  # How many validation checks?
    validations_passed: int = 0               # How many passed?
    
    # Diagnostics (current issues)
    diagnostics: Tuple[str, ...] = ()         # Any warnings/errors?
    
    # Metadata
    measured_at_utc: float = field(default_factory=time.time)
    
    @property
    def overall_health_score(self) -> float:
        """Calculate an overall health score (0-1)."""
        if self.validations_run == 0:
            return 1.0
        
        validation_rate = self.validations_passed / self.validations_run
        transfer_rate = self.transfer_success_rate
        
        # Weighted average
        return (validation_rate * 0.6 + transfer_rate * 0.4)
    
    @classmethod
    def create(cls) -> AnalogyHealth:
        """Create a new health record."""
        return cls(
            health_id=f"analogy_health:{uuid.uuid4().hex[:16]}",
        )


@dataclass(frozen=True)
class HealthMetrics:
    """
    Aggregated health metrics across multiple analogy sessions.
    
    Used for system-wide monitoring and improvement.
    """
    
    # Identity
    metrics_id: str                           # Unique identifier
    
    # Session counts
    total_sessions: int = 0
    completed_sessions: int = 0
    failed_sessions: int = 0
    
    # Aggregated metrics
    total_cases_retrieved: int = 0
    total_transfers_attempted: int = 0
    total_validations_run: int = 0
    
    # Success rates
    completion_rate: float = 0.0              # % sessions completed
    average_health_score: float = 0.0         # Mean health across sessions
    
    # Metadata
    generated_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls) -> HealthMetrics:
        """Create a new metrics set."""
        return cls(
            metrics_id=f"health_metrics:{uuid.uuid4().hex[:16]}",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AnalogyHealth",
    "HealthMetrics",
]