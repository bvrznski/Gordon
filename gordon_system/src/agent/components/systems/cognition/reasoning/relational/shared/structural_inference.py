# Structural Inference Analysis - Phase 7.11
# ===========================================

"""
Canonical Structural Inference.

Structural inference evaluates graph structures to discover patterns.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class InferencePattern(Enum):
    """Patterns that structural inference can discover."""
    
    CLUSTER = "cluster"                   # Group of tightly connected entities
    HIERARCHY = "hierarchy"               # Tree-like structure
    BRIDGE = "bridge"                     # Entity connecting communities
    CENTRAL_ENTITY = "central_entity"     # Highly connected central node
    BOTTLENECK = "bottleneck"             # Critical connection point
    ISOLATED_COMPONENT = "isolated_component"  # Disconnected subgraph


@dataclass(frozen=True)
class StructuralInferenceAnalysis:
    """
    Analysis of structural patterns in a relational graph.
    
    Inference results remain explicit and traceable to supporting relations.
    """
    
    # Identity
    analysis_id: str                      # Unique analysis identifier
    
    # Inferred patterns
    inferred_patterns: Tuple[InferencePattern, ...] = ()  # Discovered patterns
    
    # Supporting relations (which relations support the inference)
    supporting_relations: Tuple[str, ...] = ()  # Relation IDs supporting inferences
    
    # Confidence in each pattern
    confidence_scores: Dict[InferencePattern, float] = field(default_factory=dict)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from graph analysis
    
    @classmethod
    def create(
        cls,
    ) -> StructuralInferenceAnalysis:
        """Create a new structural inference analysis."""
        return cls(
            analysis_id=f"structural_inference:{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
        )
    
    def add_pattern(
        self,
        pattern: InferencePattern,
        confidence: float = 1.0,
        supporting_relation_ids: Optional[List[str]] = None,
    ) -> StructuralInferenceAnalysis:
        """Add an inferred pattern with confidence."""
        new_patterns = tuple(set(self.inferred_patterns) | {pattern})
        new_supporting = tuple(
            set(self.supporting_relations) | set(supporting_relation_ids or [])
        )
        new_confidence = dict(self.confidence_scores)
        new_confidence[pattern] = confidence
        
        return dataclass_replace(
            self,
            inferred_patterns=new_patterns,
            supporting_relations=new_supporting,
            confidence_scores=new_confidence,
        )
    
    @property
    def highest_confidence_pattern(self) -> Optional[Tuple[InferencePattern, float]]:
        """Return the pattern with highest confidence."""
        if not self.confidence_scores:
            return None
        max_pattern = max(self.confidence_scores.items(), key=lambda x: x[1])
        return (max_pattern[0], max_pattern[1])


@dataclass(frozen=True)
class StructuralComposition:
    """
    Composition of structural patterns into higher-order structures.
    
    Examples:
        components → subsystems → systems → ecosystems
    """
    
    # Identity
    composition_id: str                   # Unique composition identifier
    
    # Participating structures (lower level)
    participating_structures: Tuple[str, ...] = ()  # Structure IDs involved
    
    # Resulting structure (higher level)
    resulting_structure: Optional[str] = None   # Composite structure produced
    
    # Composition rules
    composition_rules: Tuple[str, ...] = ()     # Rules applied
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from analysis
    
    @classmethod
    def create(
        cls,
        structure_ids: List[str],
        composition_rules: Optional[List[str]] = None,
    ) -> StructuralComposition:
        """Create a new structural composition."""
        return cls(
            composition_id=f"structural_composition:{uuid.uuid4().hex[:16]}",
            participating_structures=tuple(structure_ids),
            composition_rules=tuple(composition_rules or []),
            created_at_utc=time.time(),
        )
    
    def finalize_with_result(self, result_structure: str) -> StructuralComposition:
        """Finalize the composition with resulting structure."""
        return dataclass_replace(
            self,
            resulting_structure=result_structure,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "StructuralInferenceAnalysis",
    "StructuralComposition",
    "InferencePattern",
]