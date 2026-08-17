# Counterfactual Diagnostics - Phase 7.6
# ======================================

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

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class CounterfactualDiagnostics:
    """
    Diagnostic information for counterfactual reasoning sessions.
    
    Diagnostics track:
        - Performance metrics (time, steps completed)
        - Memory usage patterns (peak, warnings)
        - Branch explosion warnings (if limit exceeded)
        - Validation bottlenecks (slow validations, etc.)
        - Resource constraints (CPU, memory limits hit)
    
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
    
    # Resource constraints
    resource_constraints: Dict[str, str] = field(default_factory=dict)  # constraint_name -> status
    
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
    
    def set_resource_constraint(self, constraint_name: str, status: str) -> CounterfactualDiagnostics:
        """Return a copy with a resource constraint set."""
        new_constraints = dict(self.resource_constraints)
        new_constraints[constraint_name] = status
        return dataclass_replace(
            self,
            resource_constraints=new_constraints,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CounterfactualDiagnostics",
]