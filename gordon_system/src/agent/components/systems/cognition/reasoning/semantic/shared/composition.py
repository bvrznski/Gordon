# Semantic Composition - Phase 7.10
# ==================================

"""
Canonical Semantic Composition contracts.

Concept composition constructs new concepts from existing ones.
Composition evaluates:
    - Component compatibility
    - Constraint consistency
    - Property aggregation
    - Behavior aggregation
    - Semantic coherence

Composition remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ConceptComposition:
    """
    Semantic composition result.
    
    A ConceptComposition contains:
        - Composition identity
        - Source concepts (components)
        - Resulting concept
        - Composition strategy
        - Provenance tracking
    """
    
    # Identity
    composition_id: str                     # Unique identifier
    
    # Reasoning goal
    reasoning_goal: str                     # What was composed?
    
    # Component concepts
    source_concepts: Tuple[str, ...] = ()
    
    # Resulting concept
    resulting_concept: Optional[str] = None
    
    # Composition strategy
    composition_strategy: str = "default"   # e.g., "union", "intersection", "product"
    
    # Composition rules applied
    composition_rules: Tuple[CompositionRule, ...] = ()
    
    # Diagnostics
    diagnostics: Tuple[DiagnosticsRecord, ...] = ()
    
    # State
    state: str = "created"
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def component_count(self) -> int:
        """Count of source concepts."""
        return len(self.source_concepts)
    
    @classmethod
    def create(
        cls,
        reasoning_goal: str,
        components: List[str],
        strategy: str = "default",
    ) -> ConceptComposition:
        """Create a new concept composition record."""
        return cls(
            composition_id=f"composition:{uuid.uuid4().hex[:16]}",
            reasoning_goal=reasoning_goal,
            source_concepts=tuple(components),
            composition_strategy=strategy,
        )
    
    def with_result(self, result: str) -> ConceptComposition:
        """Return a copy with the resulting concept."""
        return dataclass_replace(
            self,
            resulting_concept=result,
        )
    
    def add_rules(self, rules: List[CompositionRule]) -> ConceptComposition:
        """Add composition rules."""
        new_rules = tuple(self.composition_rules) + tuple(rules)
        return dataclass_replace(
            self,
            composition_rules=new_rules,
        )


@dataclass(frozen=True)
class CompositionRule:
    """
    Rule applied during concept composition.
    
    Rules include:
        - Union
        - Intersection
        - Product (Cartesian)
        - Subtraction
        - Projection
    """
    
    rule_id: str                            # Unique identifier
    rule_type: str                          # e.g., "union", "intersection"
    description: str                        # Rule explanation
    
    @classmethod
    def create_union(cls) -> CompositionRule:
        """Create a union composition rule."""
        return cls(
            rule_id=f"rule:{uuid.uuid4().hex[:16]}",
            rule_type="union",
            description="Combine all components into one concept",
        )
    
    @classmethod
    def create_intersection(cls) -> CompositionRule:
        """Create an intersection composition rule."""
        return cls(
            rule_id=f"rule:{uuid.uuid4().hex[:16]}",
            rule_type="intersection",
            description="Keep only common properties across components",
        )


@dataclass(frozen=True)
class SemanticEquivalenceAnalysis:
    """
    Semantic equivalence analysis result.
    
    Equivalence evaluates:
        - Identity
        - Strict equivalence
        - Functional equivalence
        - Partial equivalence
        - Analogy
        - Semantic overlap
    """
    
    # Identity
    analysis_id: str                        # Unique identifier
    
    # Reasoning goal
    reasoning_goal: str                     # What was compared?
    
    # Compared concepts
    compared_concepts: Tuple[str, ...] = ()
    
    # Equivalence metrics
    equivalence_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Supporting relations
    supporting_relations: Tuple[RelationEvidence, ...] = ()
    
    # Diagnostics
    diagnostics: Tuple[DiagnosticsRecord, ...] = ()
    
    # State
    state: str = "created"
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def concept_count(self) -> int:
        """Count of compared concepts."""
        return len(self.compared_concepts)
    
    @classmethod
    def create(
        cls,
        reasoning_goal: str,
        concepts: List[str],
    ) -> SemanticEquivalenceAnalysis:
        """Create a new equivalence analysis record."""
        return cls(
            analysis_id=f"equivalence:{uuid.uuid4().hex[:16]}",
            reasoning_goal=reasoning_goal,
            compared_concepts=tuple(concepts),
        )
    
    def with_metrics(self, metrics: Dict[str, float]) -> SemanticEquivalenceAnalysis:
        """Add equivalence metrics."""
        new_metrics = dict(self.equivalence_metrics)
        new_metrics.update(metrics)
        return dataclass_replace(
            self,
            equivalence_metrics=new_metrics,
        )


@dataclass(frozen=True)
class RelationEvidence:
    """
    Evidence of semantic relation supporting equivalence.
    """
    
    evidence_id: str                        # Unique identifier
    source_concept: str                     # Source concept
    target_concept: str                     # Target concept
    relation_type: str                      # e.g., "is-equivalent-to"
    confidence: float = 1.0                 # Confidence level
    
    @classmethod
    def create_equivalence(cls, a: str, b: str) -> RelationEvidence:
        """Create an equivalence evidence record."""
        return cls(
            evidence_id=f"evidence:{uuid.uuid4().hex[:16]}",
            source_concept=a,
            target_concept=b,
            relation_type="is-equivalent-to",
        )


@dataclass(frozen=True)
class DiagnosticsRecord:
    """
    Diagnostic record from composition analysis.
    """
    
    diagnostic_id: str                      # Unique identifier
    diagnostic_type: str                    # e.g., "incompatible", "missing"
    message: str                            # Diagnostic message
    severity: str = "info"                  # info, warning, error
    
    @classmethod
    def info(cls, message: str) -> DiagnosticsRecord:
        """Create an info diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="info",
            message=message,
        )
    
    @classmethod
    def warning(cls, message: str) -> DiagnosticsRecord:
        """Create a warning diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="warning",
            message=message,
            severity="warning",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ConceptComposition",
    "SemanticEquivalenceAnalysis",
    "CompositionRule",
    "RelationEvidence",
    "DiagnosticsRecord",
]