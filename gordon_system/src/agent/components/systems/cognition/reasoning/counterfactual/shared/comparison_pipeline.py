# Comparison Pipeline - Phase 7.6
# ===============================

"""
World comparison for counterfactual reasoning.

Comparison evaluates:
    - State differences between worlds
    - Goal satisfaction differences
    - Resource usage differences
    - Behavior differences
    - Risk differences

Comparison remains deterministic and explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class CounterfactualComparison:
    """
    A comparison between two worlds (reference vs alternative or alternative vs alternative).
    
    Comparison evaluates differences in:
        - State variables
        - Goal satisfaction
        - Resource usage
        - Behavior patterns
        - Risk levels
    
    All comparisons remain deterministic and reproducible.
    """
    
    # Identity
    comparison_id: str                        # Unique comparison identifier
    
    # Worlds being compared
    compared_worlds: Tuple["AlternativeWorld", ...]  # At least two worlds
    
    # Comparison metrics (what we're comparing)
    comparison_metrics: Dict[str, Any] = field(default_factory=dict)  # metric_name -> value
    
    # Resulting differences found
    resulting_differences: Tuple[ComparisonDifference, ...] = ()  # What differs?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        world1: "AlternativeWorld",
        world2: "AlternativeWorld",
    ) -> CounterfactualComparison:
        """Create a comparison between two worlds."""
        return cls(
            comparison_id=f"comparison:{uuid.uuid4().hex[:16]}",
            compared_worlds=(world1, world2),
            comparison_metrics={},
            resulting_differences=(),
        )
    
    def with_metric(self, metric_name: str, metric_value: Any) -> CounterfactualComparison:
        """Return a copy with a comparison metric added."""
        new_metrics = dict(self.comparison_metrics)
        new_metrics[metric_name] = metric_value
        return dataclass_replace(self, comparison_metrics=new_metrics)
    
    def add_difference(self, difference: ComparisonDifference) -> CounterfactualComparison:
        """Return a copy with an additional difference found."""
        return dataclass_replace(
            self,
            resulting_differences=self.resulting_differences + (difference,),
        )


@dataclass(frozen=True)
class ComparisonPipeline:
    """
    Pipeline for comparing worlds and analyzing differences.
    
    The comparison evaluates differences in states, goals, resources, behavior, and risk
    while remaining deterministic and explicit about all findings.
    """
    
    # Identity
    pipeline_id: str                          # Unique pipeline identifier
    
    # Compared worlds
    compared_worlds: Tuple["AlternativeWorld", ...] = ()
    
    # Comparison metrics used
    comparison_metrics: Tuple[str, ...] = ()  # e.g., "state_diff", "goal_satisfaction"
    
    # Resulting analysis (summary of findings)
    resulting_analysis: str = ""              # Human-readable analysis
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        compared_worlds: Tuple["AlternativeWorld", ...],
    ) -> ComparisonPipeline:
        """Create a new comparison pipeline."""
        return cls(
            pipeline_id=f"comparison_pipeline:{uuid.uuid4().hex[:16]}",
            compared_worlds=compared_worlds,
            comparison_metrics=(),
            resulting_analysis="",
        )
    
    def with_metric(self, metric: str) -> ComparisonPipeline:
        """Return a copy with an additional comparison metric."""
        return dataclass_replace(
            self,
            comparison_metrics=self.comparison_metrics + (metric,),
        )


@dataclass(frozen=True)
class ComparisonDifference:
    """
    A specific difference found between compared worlds.
    
    Each difference has:
        - The variable/aspect that differs
        - Values in each world
        - Magnitude of the difference
        - Significance assessment
    """
    
    # Identity
    difference_id: str                        # Unique difference identifier
    
    # What differs
    variable_name: str                        # e.g., "memory_usage", "response_time"
    
    # Values in each world
    values_by_world: Dict[str, Any] = field(default_factory=dict)  # world_id -> value
    
    # Magnitude of difference
    magnitude: float = 0.0                    # How big is the difference?
    
    # Significance
    significance: str = "unknown"             # "minor", "moderate", "significant"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        variable_name: str,
        values_by_world: Dict[str, Any],
    ) -> ComparisonDifference:
        """Create a new comparison difference."""
        return cls(
            difference_id=f"difference:{uuid.uuid4().hex[:16]}",
            variable_name=variable_name,
            values_by_world=values_by_world,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CounterfactualComparison",
    "ComparisonPipeline",
    "ComparisonDifference",
]