# Divergence Analysis - Phase 7.6
# ==============================

"""
Causal divergence analysis for counterfactual reasoning.

Divergence propagation:
    Reference Event → Intervention → Mechanism Changes → Secondary Effects → Outcome Differences

Propagation remains explicit and reconstructable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class WorldDivergence:
    """
    A divergence point where the alternative world differs from the reference.
    
    Each divergence has:
        - One explicit origin (the intervention or mechanism change)
        - Reconstructable propagation paths
        - Secondary effects that may compound over time
    
    Divergences never hide intermediate changes - all are traceable.
    """
    
    # Identity
    divergence_id: str                        # Unique divergence identifier
    
    # Origin of divergence
    divergence_point: str                     # What caused the divergence? (e.g., "intervention_x")
    
    # Affected mechanisms/variables
    affected_mechanisms: Tuple[str, ...] = () # Mechanisms that diverged
    
    # Resulting changes
    resulting_changes: Dict[str, Any] = field(default_factory=dict)  # var_name -> change_description
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        divergence_point: str,
        affected_mechanisms: Tuple[str, ...] = (),
    ) -> WorldDivergence:
        """Create a new world divergence."""
        return cls(
            divergence_id=f"divergence:{uuid.uuid4().hex[:16]}",
            divergence_point=divergence_point,
            affected_mechanisms=affected_mechanisms,
            resulting_changes={},
        )
    
    def with_change(self, var_name: str, change_description: Any) -> WorldDivergence:
        """Return a copy with an additional result change."""
        new_changes = dict(self.resulting_changes)
        new_changes[var_name] = change_description
        return dataclass_replace(self, resulting_changes=new_changes)


@dataclass(frozen=True)
class DivergencePipeline:
    """
    Pipeline for tracking divergence propagation through mechanisms.
    
    Pipeline flow:
        Reference Event → Intervention → Mechanism Changes → Secondary Effects → Outcome Differences
    
    Every step remains explicitly recorded for traceability and analysis.
    """
    
    # Identity
    pipeline_id: str                          # Unique pipeline identifier
    
    # Root divergence (first point of divergence)
    divergence_root: WorldDivergence          # Initial divergence event
    
    # Propagated changes (secondary effects through mechanisms)
    propagated_changes: Tuple[WorldDivergence, ...] = ()  # All subsequent divergences
    
    # Affected entities
    affected_entities: Tuple[str, ...] = ()   # What was impacted?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        divergence_root: WorldDivergence,
    ) -> DivergencePipeline:
        """Create a new divergence pipeline."""
        return cls(
            pipeline_id=f"divergence_pipeline:{uuid.uuid4().hex[:16]}",
            divergence_root=divergence_root,
            propagated_changes=(),
            affected_entities=(),
        )
    
    def add_propagation(self, divergence: WorldDivergence) -> DivergencePipeline:
        """Return a copy with an additional propagation step."""
        return dataclass_replace(
            self,
            propagated_changes=self.propagated_changes + (divergence,),
        )
    
    def add_affected_entity(self, entity_id: str) -> DivergencePipeline:
        """Return a copy with an affected entity added."""
        new_entities = set(self.affected_entities)
        new_entities.add(entity_id)
        return dataclass_replace(
            self,
            affected_entities=tuple(sorted(new_entities)),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "WorldDivergence",
    "DivergencePipeline",
]