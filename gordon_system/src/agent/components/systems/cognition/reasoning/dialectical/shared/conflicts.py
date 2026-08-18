# Dialectical Conflict Resolution - Phase 7.17
# =============================================

"""
Canonical Conflict Resolution Contract.

Conflict resolution evaluates:
    - Logical incompatibility
    - Semantic incompatibility
    - Causal incompatibility
    - Evidential incompatibility
    - Assumption incompatibility
    - Goal incompatibility
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ConflictResolution:
    """
    Resolution of a conflict between arguments.

    Conflicts may include:
        - Logical incompatibility (mutual exclusion)
        - Semantic incompatibility (different meanings)
        - Causal incompatibility (conflicting causal claims)
        - Evidential incompatibility (contradictory evidence)
        - Assumption incompatibility (conflicting premises)
        - Goal incompatibility (conflicting objectives)

    Resolution remains explicit and traceable.
    """

    # Identity
    resolution_id: str                      # Unique identifier

    # Participating arguments
    participating_arguments: Tuple[str, ...]  # Argument IDs involved

    # Conflict graph (mapping conflicts to participants)
    conflict_graph: Dict[str, List[str]] = field(default_factory=dict)

    # Resolution strategy (how was the conflict resolved?)
    resolution_strategy: str = "none"       # e.g., "synthesis", "compromise", "rejection"

    # Timing
    analyzed_at_utc: float = field(default_factory=time.time)
    resolved_at_utc: Optional[float] = None

    # Provenance
    origin_context: str = "unknown"
    evidence_for_resolution: Tuple[Dict[str, Any], ...] = ()

    @property
    def is_resolved(self) -> bool:
        """Check if conflict has been resolved."""
        return self.resolution_strategy != "none"

    @classmethod
    def create(
        cls,
        participating_arguments: List[str],
        origin_context: str = "unknown",
    ) -> ConflictResolution:
        """Create a new conflict resolution record."""
        return cls(
            resolution_id=f"conflict_resolution:{uuid.uuid4().hex[:16]}",
            participating_arguments=tuple(participating_arguments),
            origin_context=origin_context,
        )

    def with_conflict(self, conflict_type: str, affected_args: List[str]) -> ConflictResolution:
        """Add a conflict to the graph."""
        new_graph = dict(self.conflict_graph)
        new_graph[conflict_type] = affected_args
        return dataclass_replace(
            self,
            conflict_graph=new_graph,
        )

    def with_resolution_strategy(self, strategy: str) -> ConflictResolution:
        """Set resolution strategy and mark as resolved."""
        return dataclass_replace(
            self,
            resolution_strategy=strategy,
            resolved_at_utc=time.time(),
        )

    def with_evidence(self, evidence: Dict[str, Any]) -> ConflictResolution:
        """Add evidence supporting the resolution."""
        return dataclass_replace(
            self,
            evidence_for_resolution=self.evidence_for_resolution + (evidence,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ConflictResolution",
]