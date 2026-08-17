# Graph Analysis - Phase 7.11
# ============================

"""
Canonical Graph Analysis.

Graph analysis evaluates connectivity, reachability, cycles, and structural properties.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class GraphAnalysis:
    """
    Analysis of relational graph structure and properties.
    
    Analysis includes connectivity, reachability, cycles, cut vertices,
    centrality, and articulation points.
    """
    
    # Identity
    analysis_id: str                      # Unique analysis identifier
    
    # Computed metrics
    computed_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Structural properties
    structural_properties: Tuple[str, ...] = ()  # Properties like "connected", "acyclic"
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()       # Analysis diagnostics
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from graph
    
    @classmethod
    def create(
        cls,
    ) -> GraphAnalysis:
        """Create a new graph analysis."""
        return cls(
            analysis_id=f"graph_analysis:{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
        )
    
    def record_metric(self, metric_name: str, value: float) -> GraphAnalysis:
        """Record a computed metric."""
        new_metrics = dict(self.computed_metrics)
        new_metrics[metric_name] = value
        return dataclass_replace(
            self,
            computed_metrics=new_metrics,
        )
    
    def record_property(self, property_name: str) -> GraphAnalysis:
        """Record a structural property."""
        return dataclass_replace(
            self,
            structural_properties=self.structural_properties + (property_name,),
        )
    
    def record_diagnostic(self, diagnostic: str) -> GraphAnalysis:
        """Record a diagnostics message."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + (diagnostic,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GraphAnalysis",
]