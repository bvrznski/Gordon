# Relational Health - Phase 7.11
# ==============================

"""
Canonical Relational Health metrics.

Health metrics describe the state of relational reasoning without modifying artifacts.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class RelationalHealth:
    """
    Health metrics for relational reasoning sessions.
    
    Metrics remain descriptive - they never modify the underlying structures.
    """
    
    # Identity
    health_id: str                        # Unique health identifier
    
    # Entity metrics
    entities_represented: int = 0         # Number of entities in graph
    
    # Relation metrics
    relations_inferred: int = 0           # Number of relations discovered
    
    # Graph structure
    graph_density: float = 0.0            # Edge density (0.0 to 1.0)
    
    # Constraint health
    constraint_violations: int = 0        # Count of violations
    constraint_satisfied: int = 0         # Count of satisfied constraints
    
    # Structural consistency
    structural_consistency: str = "unknown"  # unknown, consistent, inconsistent
    
    # Validation results
    validation_success: bool = False      # Overall validation status
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()     # Health-related diagnostics
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from analysis
    
    @classmethod
    def create(
        cls,
    ) -> RelationalHealth:
        """Create a new relational health tracker."""
        return cls(
            health_id=f"relational_health:{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
        )
    
    def record_entities(self, count: int) -> RelationalHealth:
        """Record the number of entities represented."""
        return dataclass_replace(
            self,
            entities_represented=count,
        )
    
    def record_relations(self, count: int) -> RelationalHealth:
        """Record the number of relations inferred."""
        return dataclass_replace(
            self,
            relations_inferred=count,
        )
    
    def record_graph_density(self, density: float) -> RelationalHealth:
        """Record graph density (0.0 to 1.0)."""
        return dataclass_replace(
            self,
            graph_density=min(1.0, max(0.0, density)),
        )
    
    def record_constraint_violation(self) -> RelationalHealth:
        """Record a constraint violation."""
        return dataclass_replace(
            self,
            constraint_violations=self.constraint_violations + 1,
        )
    
    def record_constraint_satisfied(self) -> RelationalHealth:
        """Record a satisfied constraint."""
        return dataclass_replace(
            self,
            constraint_satisfied=self.constraint_satisfied + 1,
        )
    
    def set_consistency(self, consistency: str) -> RelationalHealth:
        """Set structural consistency status."""
        return dataclass_replace(
            self,
            structural_consistency=consistency,
        )
    
    def record_diagnostic(self, diagnostic: str) -> RelationalHealth:
        """Record a diagnostics message."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + (diagnostic,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RelationalHealth",
]