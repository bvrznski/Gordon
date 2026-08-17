# Structural Alignment - Phase 7.4
# ===============================

"""
Canonical Structural Alignment Contract.

Alignment identifies relational correspondences between source and target.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class StructuralMapping:
    """
    A structural mapping between source and target structures.
    
    Mapping evaluates:
        - Entities (what corresponds?)
        - Relations (how are they related?)
        - Constraints (what must hold?)
        - Hierarchies (what is nested in what?)
        - Causal structure (what causes what?)
        - Functional roles (what does each part do?)
    
    Mapping remains explicit; all correspondences are documented.
    """
    
    # Identity
    mapping_id: str                           # Unique identifier
    
    # Source and target structures being mapped
    source_case_id: str                       # ID of source case
    target_problem_id: str                    # ID of target problem
    
    # Structural elements
    source_structure: Dict[str, Any] = field(default_factory=dict)
    target_structure: Dict[str, Any] = field(default_factory=dict)
    
    # Correspondences (mappings between elements)
    correspondences: Tuple[Tuple[str, str], ...] = ()  # (source_element, target_element)
    
    # Mapping confidence
    structural_score: float = 0.0             # Overall alignment quality
    coverage_ratio: float = 0.0               # What % of target is covered?
    
    # Constraints that must hold for the mapping to be valid
    constraint_satisfaction: Dict[str, bool] = field(default_factory=dict)
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def correspondence_count(self) -> int:
        """Number of correspondences in mapping."""
        return len(self.correspondences)
    
    @classmethod
    def create(
        cls,
        source_case_id: str,
        target_problem_id: str,
        correspondences: Optional[List[Tuple[str, str]]] = None,
        structural_score: float = 0.0,
    ) -> StructuralMapping:
        """Create a new structural mapping."""
        return cls(
            mapping_id=f"structural_mapping:{uuid.uuid4().hex[:16]}",
            source_case_id=source_case_id,
            target_problem_id=target_problem_id,
            correspondences=tuple(correspondences or []),
            structural_score=structural_score,
        )
    
    def add_correspondence(self, source_elem: str, target_elem: str) -> StructuralMapping:
        """Return a new mapping with the correspondence added."""
        return dataclass_replace(
            self,
            correspondences=self.correspondences + ((source_elem, target_elem),),
        )


@dataclass(frozen=True)
class AlignmentEvaluation:
    """
    Evaluation of how well two structures align.
    
    Alignment evaluates:
        - Entity alignment (do objects match?)
        - Relation alignment (do relationships match?)
        - Constraint alignment (do constraints match?)
        - Hierarchical alignment (is nesting preserved?)
        - Causal alignment (are causal structures similar?)
        - Functional alignment (do roles match?)
    """
    
    # Identity
    evaluation_id: str                        # Unique identifier
    
    # Alignment components
    entity_alignment_score: float = 0.0       # How well do entities match?
    relation_alignment_score: float = 0.0     # How well do relations match?
    constraint_alignment_score: float = 0.0   # How well do constraints match?
    
    # Overall evaluation
    overall_alignment_score: float = 0.0      # Combined score
    
    # Diagnostics
    alignment_details: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        entity_score: float = 0.0,
        relation_score: float = 0.0,
        constraint_score: float = 0.0,
    ) -> AlignmentEvaluation:
        """Create a new alignment evaluation."""
        overall = (entity_score + relation_score + constraint_score) / 3
        return cls(
            evaluation_id=f"alignment_eval:{uuid.uuid4().hex[:16]}",
            entity_alignment_score=entity_score,
            relation_alignment_score=relation_score,
            constraint_alignment_score=constraint_score,
            overall_alignment_score=overall,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "StructuralMapping",
    "AlignmentEvaluation",
]