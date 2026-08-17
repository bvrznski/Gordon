# Counterfactual Health - Phase 7.6
# ================================

"""
Health metrics for counterfactual reasoning evaluation.

Metrics include:
    - Worlds generated
    - Branch depth
    - Average divergence
    - Comparison completeness
    - Validation success
    - Resource efficiency
    - Diagnostics

Health remains descriptive (measures state, doesn't modify it).
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class CounterfactualHealth:
    """
    Health metrics for counterfactual reasoning sessions.
    
    Metrics include:
        - Worlds generated (total and per session)
        - Branch depth (how deep is the world tree?)
        - Average divergence (how much do alternatives differ from reference?)
        - Comparison completeness (% of expected comparisons made)
        - Validation success rate
        - Resource efficiency (time, memory usage)
    """
    
    # Identity
    health_id: str                            # Unique health identifier
    
    # World generation metrics
    worlds_generated: int = 0                 # Total alternative worlds created
    reference_worlds_evaluated: int = 0       # Reference world count (usually 1)
    
    # Branching metrics
    branch_count: int = 0                     # Total branches in the tree
    max_branch_depth: int = 0                 # Deepest branch from reference
    
    # Divergence metrics
    average_divergence_magnitude: float = 0.0 # Average divergence strength
    
    # Comparison metrics
    comparisons_completed: int = 0            # Successful comparisons
    comparison_count_target: int = 0          # Expected comparison count
    comparison_rate: float = 0.0              # completion rate
    
    # Validation metrics
    validation_successes: int = 0             # Passed validation
    validation_failures: int = 0              # Failed validation
    validation_rate: float = 0.0              # success rate
    
    # Resource metrics
    total_time_seconds: float = 0.0           # Total reasoning time
    peak_memory_mb: float = 0.0               # Peak memory usage
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_sessions(self) -> int:
        """Total counterfactual sessions tracked."""
        return self.reference_worlds_evaluated
    
    @classmethod
    def create(cls, health_id: Optional[str] = None) -> CounterfactualHealth:
        """Create a new counterfactual health record."""
        return cls(
            health_id=health_id or f"counterfactual_health:{uuid.uuid4().hex[:16]}",
        )


@dataclass(frozen=True)
class CounterfactualDiagnostics:
    """
    Diagnostic information for counterfactual reasoning sessions.
    
    Diagnostics track:
        - Performance metrics
        - Memory usage patterns
        - Branch explosion warnings
        - Validation bottlenecks
        - Resource constraints
    
    These remain inspectable but never modify reasoning artifacts.
    """
    
    # Identity
    diagnostics_id: str                       # Unique diagnostics identifier
    
    # Session context
    session_id: str                           # Which session?
    
    # Performance metrics
    steps_completed: int = 0                  # Reasoning steps executed
    total_steps_target: int = 0               # Expected step count
    
    # Memory tracking
    memory_peak_mb: float = 0.0               # Peak memory usage
    memory_warnings: Tuple[str, ...] = ()     # Memory-related warnings
    
    # Branch tracking
    branches_created: int = 0                 # Branches generated
    branch_explosion_warning: bool = False    # Did we hit the limit?
    
    # Validation issues
    validation_issues: Tuple[str, ...] = ()   # Problems found during validation
    divergence_trace_length: int = 0          # Length of longest divergence trace
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, session_id: str) -> CounterfactualDiagnostics:
        """Create a new diagnostics record."""
        return cls(
            diagnostics_id=f"diagnostics:{uuid.uuid4().hex[:16]}",
            session_id=session_id,
        )
    
    def add_memory_warning(self, warning: str) -> CounterfactualDiagnostics:
        """Return a copy with an additional memory warning."""
        return dataclass_replace(
            self,
            memory_warnings=self.memory_warnings + (warning,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CounterfactualHealth",
    "CounterfactualDiagnostics",
]