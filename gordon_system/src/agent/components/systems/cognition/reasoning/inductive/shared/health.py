# Induction Health - Phase 7.2
# ============================

"""
Canonical Induction Health Contract.

Health metrics provide diagnostic information about induction performance.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class InductionHealth:
    """
    Health metrics for an induction session or system.
    
    Metrics include:
        - Observations analyzed
        - Patterns discovered
        - Generalizations produced
        - Outliers detected
        - Average confidence
        - Generalization stability
        - Failure rate
    
    Health remains descriptive, not prescriptive.
    """
    
    # Identity
    health_id: str                        # Unique identifier for this health report
    
    # Session metrics
    observations_analyzed: int = 0        # Total observations processed
    patterns_discovered: int = 0          # Patterns found
    generalizations_produced: int = 0     # Generalizations created
    outliers_detected: int = 0            # Outliers identified
    
    # Quality metrics
    average_confidence: float = 0.5       # Mean confidence across all results
    average_coverage: float = 0.0         # Mean coverage ratio
    
    # Stability metrics
    generalization_stability: float = 1.0 # How stable are generalizations?
    pattern_consistency: float = 1.0      # Consistency of patterns
    
    # Failure metrics
    total_sessions_attempted: int = 0     # Total induction attempts
    successful_sessions: int = 0          # Completed successfully
    failed_sessions: int = 0              # Failed
    failure_rate: float = 0.0             # Failed / Total
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    health_period_start_utc: Optional[float] = None  # For time-bounded reports
    health_period_end_utc: Optional[float] = None


@dataclass(frozen=True)
class HealthMetrics:
    """
    Detailed metrics for induction components.
    
    Allows component-level health assessment.
    """
    
    metrics_id: str
    
    # Component-specific metrics
    component_name: str                   # e.g., "pattern_discovery", "generalization"
    
    # Activity counts
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    
    # Quality metrics
    average_duration_seconds: float = 0.0
    success_rate: float = 1.0
    
    # Output measures
    outputs_generated: int = 0
    average_confidence: float = 0.5
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class HealthSummary:
    """
    Summary health report for induction system.
    
    Provides high-level overview of system performance and quality.
    """
    
    summary_id: str
    
    # Overall metrics
    total_observations_processed: int = 0
    total_sessions_completed: int = 0
    average_session_duration_seconds: float = 0.0
    
    # Quality scores (0-1)
    observation_quality_score: float = 1.0
    pattern_discovery_quality: float = 1.0
    generalization_quality: float = 1.0
    
    # System metrics
    throughput_sessions_per_minute: float = 0.0
    error_rate: float = 0.0
    
    # Health status
    system_health_status: str = "healthy"  # healthy, warning, critical
    recommendations: Tuple[str, ...] = ()
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)


__all__ = [
    "InductionHealth",
    "HealthMetrics",
    "HealthSummary",
]