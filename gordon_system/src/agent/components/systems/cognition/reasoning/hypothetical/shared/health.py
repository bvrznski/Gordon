# Hypothetical Health Metrics - Phase 7.15 Part 2
# ================================================

"""
Canonical Hypothetical Health Contract.

Health metrics are descriptive and observational.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class HypotheticalHealth:
    """
    Health metrics for hypothetical reasoning.
    
    Metrics remain descriptive and observational.
    """
    
    # Identity
    health_id: str                            # Unique identifier
    
    # Metrics
    hypotheses_generated: int = 0             # Total hypotheses generated
    assumptions_tracked: int = 0              # Assumptions tracked
    scenario_diversity: float = 0.0           # Diversity of scenarios (0-1)
    possibility_coverage: float = 0.0         # Coverage of possibility space (0-1)
    novel_hypotheses: int = 0                 # Novel hypotheses (not seen before)
    validation_success: float = 0.0           # Validation success rate (0-1)
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)  # Additional metrics
    
    # Metadata
    measured_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        hypotheses_generated: int = 0,
        assumptions_tracked: int = 0,
        scenario_diversity: float = 0.0,
        possibility_coverage: float = 0.0,
        novel_hypotheses: int = 0,
        validation_success: float = 0.0,
        diagnostics: Optional[Dict[str, Any]] = None,
    ) -> HypotheticalHealth:
        """Create a new health metrics record."""
        return cls(
            health_id=f"hypothetical_health:{uuid.uuid4().hex[:16]}",
            hypotheses_generated=hypotheses_generated,
            assumptions_tracked=assumptions_tracked,
            scenario_diversity=scenario_diversity,
            possibility_coverage=possibility_coverage,
            novel_hypotheses=novel_hypotheses,
            validation_success=validation_success,
            diagnostics=diagnostics or {},
        )


@dataclass(frozen=True)
class HypotheticalTrace:
    """
    Trace of a complete hypothetical reasoning session.
    
    Contains all hypotheses, assumptions, possibility spaces, scenarios,
    refinements, and validation results for inspection.
    """
    
    # Identity
    trace_id: str                             # Unique identifier
    
    # Reasoning steps (chronological)
    reasoning_steps: Tuple[str, ...] = ()     # All reasoning steps taken
    
    # Hypothesis graph
    hypothesis_graph: Dict[str, List[str]] = field(default_factory=dict)  # adjacency list
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)  # Session metrics
    
    # Metadata
    trace_created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        reasoning_steps: Optional[List[str]] = None,
        hypothesis_graph: Optional[Dict[str, List[str]]] = None,
        diagnostics: Optional[Dict[str, Any]] = None,
    ) -> HypotheticalTrace:
        """Create a new trace record."""
        return cls(
            trace_id=f"trace:{uuid.uuid4().hex[:16]}",
            reasoning_steps=tuple(reasoning_steps or []),
            hypothesis_graph=hypothesis_graph or {},
            diagnostics=diagnostics or {},
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "HypotheticalHealth",
    "HypotheticalTrace",
]