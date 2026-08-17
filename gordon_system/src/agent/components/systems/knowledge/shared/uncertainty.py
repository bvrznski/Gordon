# Knowledge Uncertainty - Phase 5.4
# ==================================

"""
Knowledge Uncertainty: Semantic ambiguity metrics in Gordon's knowledge system.

Uncertainty measures semantic uncertainty about claims, concepts, relations,
and beliefs. It differs from perception and memory uncertainty by measuring
semantic rather than observational limits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# UNCERTAINTY SOURCES - Origins of semantic uncertainty
# =============================================================================


class UncertaintySource(Enum):
    """
    Sources of semantic uncertainty.
    
    Defines where uncertainty values originate in the knowledge system.
    """
    
    CLASSIFICATION_AMBIGUITY = "classification_ambiguity"  # Concept classification unclear
    RELATION_AMBIGUITY = "relation_ambiguity"            # Relation type uncertain
    MODEL_INCOMPLETENESS = "model_incompleteness"        # Model lacks coverage
    EVIDENCE_GAP = "evidence_gap"                        # Missing supporting evidence
    
    UNKNOWN = "unknown"


# =============================================================================
# UNCERTAINTY METRICS - Semantic uncertainty representation
# =============================================================================


@dataclass(frozen=True)
class KnowledgeUncertainty:
    """
    Uncertainty metrics for knowledge artifacts.
    
    Represents semantic ambiguity about a claim, belief, concept, or relation.
    Uncertainty measures what cannot be known due to incomplete information,
    not observational noise.
    
    Fields:
        uncertainty_identity:  Unique identifier for this uncertainty record
        value:                 Numeric uncertainty (0.0-1.0)
        sources:               Sources contributing to this uncertainty
        context:               Context where this uncertainty applies
        revision:              Revision number for traceability
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity and metadata (required)
    uncertainty_identity: str         # Unique ID for this uncertainty record
    
    # Value (required - 0.0-1.0 range)
    value: float                      # Semantic uncertainty (0.0-1.0)
    
    # Source information
    sources: Tuple[str, ...] = field(default_factory=tuple)  # Source identifiers
    
    # Context
    context: str = "general"          # Context where this applies
    kind: str = "semantic"            # Kind of uncertainty (semantic, evidential, etc.)
    
    # Lifecycle tracking
    revision: int = 1                 # Revision number for traceability
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_valid(self) -> bool:
        """Check if uncertainty has valid data."""
        return 0.0 <= self.value <= 1.0
    
    @classmethod
    def create(
        cls,
        value: float,
        sources: Optional[List[str]] = None,
        context: str = "general",
        kind: str = "semantic",
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeUncertainty":
        """
        Create a new uncertainty record.
        
        Args:
            value: Numeric uncertainty (0.0-1.0)
            sources: Source identifiers (optional)
            context: Context where this applies
            kind: Kind of uncertainty
            provenance: Origin tracking data (optional)
        """
        return cls(
            uncertainty_identity=f"uncertainty:{uuid.uuid4().hex[:16]}",
            value=max(0.0, min(1.0, float(value))),
            sources=tuple(sources or []),
            context=context,
            kind=kind,
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "revision": 1,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert uncertainty to dictionary for serialization."""
        return {
            "uncertainty_identity": self.uncertainty_identity,
            "value": self.value,
            "sources": list(self.sources),
            "context": self.context,
            "kind": self.kind,
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeUncertainty":
        """Create uncertainty record from dictionary."""
        return cls(
            uncertainty_identity=data.get("uncertainty_identity", str(uuid.uuid4())),
            value=float(data.get("value", 0.5)),
            sources=tuple(data.get("sources", [])),
            context=data.get("context", "general"),
            kind=data.get("kind", "semantic"),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )
    
    def update(
        self,
        new_value: float,
        source_update: Optional[List[str]] = None,
    ) -> "KnowledgeUncertainty":
        """
        Create a revised uncertainty record.
        
        Args:
            new_value: New uncertainty value
            source_update: Additional sources to add (optional)
        """
        new_sources = list(self.sources)
        if source_update:
            for s in source_update:
                if s not in new_sources:
                    new_sources.append(s)
        
        return KnowledgeUncertainty(
            uncertainty_identity=self.uncertainty_identity,
            value=max(0.0, min(1.0, float(new_value))),
            sources=tuple(new_sources),
            context=self.context,
            kind=self.kind,
            revision=self.revision + 1,
            provenance={
                **self.provenance,
                "updated_at_utc": time.time(),
                "previous_revision": self.revision,
            },
        )


# =============================================================================
# UNCERTAINTY AGGREGATOR
# =============================================================================


class UncertaintyAggregator:
    """
    Aggregates uncertainty from multiple sources.
    
    Combines uncertainty metrics using weighted averaging based on source quality.
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
        uncertainties: List[Tuple[float, float]],  # (uncertainty_value, source_weight)
    ) -> KnowledgeUncertainty:
        """
        Aggregate uncertainty from multiple sources.
        
        Args:
            uncertainties: List of (value, weight) tuples
            
        Returns:
            Aggregated uncertainty record
        """
        if len(uncertainties) < self._min_sources:
            return KnowledgeUncertainty.create(0.5)
        
        total_weight = sum(w for _, w in uncertainties)
        if total_weight == 0:
            return KnowledgeUncertainty.create(0.5)
        
        weighted_sum = sum(v * w for v, w in uncertainties)
        aggregated_value = weighted_sum / total_weight
        
        sources = [f"source_{i}" for i, _ in enumerate(uncertainties)]
        
        return KnowledgeUncertainty.create(
            value=aggregated_value,
            sources=sources,
        )
    
    def aggregate_knowledge_uncertainty(
        self,
        uncertainties: List[KnowledgeUncertainty],
    ) -> KnowledgeUncertainty:
        """
        Aggregate multiple uncertainty records.
        
        Args:
            uncertainties: List of uncertainty records to aggregate
            
        Returns:
            Aggregated uncertainty record
        """
        if len(uncertainties) < self._min_sources:
            return KnowledgeUncertainty.create(0.5)
        
        values = [u.value for u in uncertainties]
        weights = [1.0] * len(uncertainties)  # Equal weighting by default
        
        total_weight = sum(weights)
        weighted_sum = sum(v * w for v, w in zip(values, weights))
        aggregated_value = weighted_sum / total_weight
        
        sources = [u.uncertainty_identity for u in uncertainties]
        
        return KnowledgeUncertainty.create(
            value=aggregated_value,
            sources=sources,
        )


__all__ = [
    "UncertaintySource",
    "KnowledgeUncertainty",
    "UncertaintyAggregator",
]