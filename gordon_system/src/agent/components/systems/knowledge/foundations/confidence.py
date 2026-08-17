# Knowledge Confidence - Phase 6.1
# ===============================

"""
Knowledge Confidence: Semantic certainty metrics in Gordon's knowledge system.

Confidence measures the semantic certainty about claims, concepts, relations,
and beliefs. It represents how strongly Gordon holds a belief based on evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# CONFIDENCE SOURCES - Where confidence values originate
# =============================================================================


class ConfidenceSource(Enum):
    """
    Sources of semantic confidence metrics.
    
    Defines the origin mechanisms for confidence assessments in the knowledge system.
    """
    
    EVIDENCE_SUPPORT = "evidence_support"         # Based on supporting evidence
    REASONING_VALIDITY = "reasoning_validity"     # Based on reasoning quality
    CONSISTENCY = "consistency"                   # Based on consistency with known beliefs
    CONSENSUS = "consensus"                       # Based on agreement with other sources
    
    UNKNOWN = "unknown"


# =============================================================================
# SEMANTIC CONFIDENCE - Core representation
# =============================================================================


@dataclass(frozen=True)
class SemanticConfidence:
    """
    Confidence metrics for knowledge artifacts.
    
    Represents semantic certainty about a claim, belief, concept, or relation.
    
    Fields:
        confidence_identity:  Unique identifier for this confidence record
        value:                Numeric confidence (0.0-1.0)
        sources:              Sources contributing to this confidence
        context:              Context where this confidence applies
        kind:                 Kind of confidence (semantic, evidential, etc.)
        revision:             Revision number for traceability
    """
    
    # Identity and metadata (required)
    confidence_identity: str            # Unique ID for this confidence record
    
    # Value (required - 0.0-1.0 range)
    value: float                        # Semantic confidence (0.0-1.0)
    
    # Source information
    sources: Tuple[str, ...] = field(default_factory=tuple)  # Source identifiers
    
    # Context
    context: str = "general"            # Context where this applies
    kind: str = "semantic"              # Kind of confidence (semantic, evidential, etc.)
    
    # Lifecycle tracking
    revision: int = 1                   # Revision number for traceability
    
    @property
    def is_valid(self) -> bool:
        """Check if confidence has valid data."""
        return 0.0 <= self.value <= 1.0
    
    @classmethod
    def create(
        cls,
        value: float,
        sources: Optional[List[str]] = None,
        context: str = "general",
        kind: str = "semantic",
    ) -> "SemanticConfidence":
        """
        Create a new confidence record.
        
        Args:
            value: Numeric confidence (0.0-1.0)
            sources: Source identifiers (optional)
            context: Context where this applies
            kind: Kind of confidence
            
        Returns:
            New SemanticConfidence instance
        """
        return cls(
            confidence_identity=f"confidence:{uuid.uuid4().hex[:16]}",
            value=max(0.0, min(1.0, float(value))),
            sources=tuple(sources or []),
            context=context,
            kind=kind,
        )
    
    def update(
        self,
        new_value: float,
        source_update: Optional[List[str]] = None,
    ) -> "SemanticConfidence":
        """
        Create a revised confidence record.
        
        Args:
            new_value: New confidence value
            source_update: Additional sources to add (optional)
            
        Returns:
            Updated SemanticConfidence instance
        """
        new_sources = list(self.sources)
        if source_update:
            for s in source_update:
                if s not in new_sources:
                    new_sources.append(s)
        
        return SemanticConfidence(
            confidence_identity=self.confidence_identity,
            value=max(0.0, min(1.0, float(new_value))),
            sources=tuple(new_sources),
            context=self.context,
            kind=self.kind,
            revision=self.revision + 1,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert confidence to dictionary for serialization."""
        return {
            "confidence_identity": self.confidence_identity,
            "value": self.value,
            "sources": list(self.sources),
            "context": self.context,
            "kind": self.kind,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticConfidence":
        """Create confidence record from dictionary."""
        return cls(
            confidence_identity=data.get("confidence_identity", str(uuid.uuid4())),
            value=float(data.get("value", 0.5)),
            sources=tuple(data.get("sources", [])),
            context=data.get("context", "general"),
            kind=data.get("kind", "semantic"),
            revision=int(data.get("revision", 1)),
        )


# =============================================================================
# CONFIDENCE AGGREGATOR - Combine multiple confidence metrics
# =============================================================================


class ConfidenceAggregator:
    """
    Aggregates confidence from multiple sources.
    
    Combines confidence metrics using weighted averaging based on source quality.
    """
    
    def __init__(
        self,
        weight_by_evidence_count: bool = True,
        minimum_sources: int = 1,
    ):
        """
        Initialize the aggregator.
        
        Args:
            weight_by_evidence_count: Weight sources by their evidence count
            minimum_sources: Minimum number of sources required
        """
        self._weight_by_evidence = weight_by_evidence_count
        self._min_sources = minimum_sources
    
    def aggregate(
        self,
        confidences: List[Tuple[float, float]],  # (confidence_value, source_weight)
    ) -> SemanticConfidence:
        """
        Aggregate confidence from multiple sources.
        
        Args:
            confidences: List of (value, weight) tuples
            
        Returns:
            Aggregated SemanticConfidence record
        """
        if len(confidences) < self._min_sources:
            return SemanticConfidence.create(0.5)
        
        total_weight = sum(w for _, w in confidences)
        if total_weight == 0:
            return SemanticConfidence.create(0.5)
        
        weighted_sum = sum(v * w for v, w in confidences)
        aggregated_value = weighted_sum / total_weight
        
        sources = [f"source_{i}" for i, _ in enumerate(confidences)]
        
        return SemanticConfidence.create(
            value=aggregated_value,
            sources=sources,
        )
    
    def aggregate_confidence_records(
        self,
        confidences: List[SemanticConfidence],
    ) -> SemanticConfidence:
        """
        Aggregate multiple confidence records.
        
        Args:
            confidences: List of confidence records to aggregate
            
        Returns:
            Aggregated SemanticConfidence record
        """
        if len(confidences) < self._min_sources:
            return SemanticConfidence.create(0.5)
        
        values = [c.value for c in confidences]
        weights = [1.0] * len(confidences)
        
        total_weight = sum(weights)
        weighted_sum = sum(v * w for v, w in zip(values, weights))
        aggregated_value = weighted_sum / total_weight
        
        sources = [c.confidence_identity for c in confidences]
        
        return SemanticConfidence.create(
            value=aggregated_value,
            sources=sources,
        )


__all__ = [
    "ConfidenceSource",
    "SemanticConfidence",
    "ConfidenceAggregator",
]