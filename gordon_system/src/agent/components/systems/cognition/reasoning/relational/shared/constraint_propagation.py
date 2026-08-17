# Constraint Propagation - Phase 7.11
# =====================================

"""
Canonical Constraint Propagation.

Constraints propagate through relational graphs.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class RelationConstraintPropagation:
    """
    Propagation of constraints through relational graphs.
    
    Constraints include dependency, ownership, compatibility, communication,
    and hierarchical constraints.
    """
    
    # Identity
    propagation_id: str                     # Unique propagation identifier
    
    # Propagated constraints
    propagated_constraints: Tuple[str, ...] = ()   # Constraints that were propagated
    
    # Affected entities
    affected_entities: Tuple[str, ...] = ()        # Entity IDs affected by propagation
    
    # Resulting changes
    resulting_changes: Tuple[str, ...] = ()        # Changes made as a result
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from analysis
    
    @classmethod
    def create(
        cls,
    ) -> RelationConstraintPropagation:
        """Create a new constraint propagation tracker."""
        return cls(
            propagation_id=f"constraint_propagation:{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
        )
    
    def record_constraint(self, constraint: str) -> RelationConstraintPropagation:
        """Record a propagated constraint."""
        return dataclass_replace(
            self,
            propagated_constraints=self.propagated_constraints + (constraint,),
        )
    
    def record_affected_entity(self, entity_id: str) -> RelationConstraintPropagation:
        """Record an affected entity."""
        return dataclass_replace(
            self,
            affected_entities=self.affected_entities + (entity_id,),
        )
    
    def record_change(self, change: str) -> RelationConstraintPropagation:
        """Record a resulting change."""
        return dataclass_replace(
            self,
            resulting_changes=self.resulting_changes + (change,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RelationConstraintPropagation",
]