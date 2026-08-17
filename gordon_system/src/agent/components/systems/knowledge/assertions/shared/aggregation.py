# Knowledge Assertions - Evidence Aggregation Contract - Phase 6.4
# =================================================================

"""
Evidence Aggregation: Combining multiple evidence sources for assertions.

Aggregation preserves all evidence while computing overall support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# EVIDENCE SUPPORT KINDS
# =============================================================================


class EvidenceSupportKind(Enum):
    """Kinds of evidence support."""
    
    DIRECTLY_SUPPORTING = "directly_supporting"
    INDIRECTLY_SUPPORTING = "indirectly_supporting"
    CONTRADICTING = "contradicting"
    NEUTRAL = "neutral"


# =============================================================================
# EVIDENCE AGGREGATION
# =============================================================================


@dataclass(frozen=True)
class EvidenceAggregation:
    """
    Aggregated evidence for an assertion.
    
    Multiple evidence sources are aggregated while preserving all sources.
    
    Fields:
        aggregation_identity:  Unique identifier for this aggregation
        supporting_sources:    All supporting evidence source references
        contradicting_sources: All contradicting evidence source references
        weighting_strategy:    How to weight different sources
        aggregation_result:    Computed net support value (-1.0 to 1.0)
        provenance:            Origin tracking information
    
    CONTRACT REQUIREMENTS:
        EVIDENCE-LAW-001: Every Assertion supports zero or more Evidence references.
        EVIDENCE-LAW-002: Supporting and contradicting evidence remain distinguishable.
        EVIDENCE-LAW-003: Evidence preserves provenance.
        EVIDENCE-LAW-004: Evidence aggregation preserves contributing sources.
        EVIDENCE-LAW-005: Evidence revisions preserve history.
        EVIDENCE-LAW-006: Evidence remains independently inspectable.
        EVIDENCE-LAW-007: Missing evidence remains explicitly representable.
        EVIDENCE-LAW-008: Equivalent evidence aggregates deterministically.
    """
    
    aggregation_identity: str
    supporting_sources: Tuple[str, ...] = field(default_factory=tuple)
    contradicting_sources: Tuple[str, ...] = field(default_factory=tuple)
    weighting_strategy: str = "uniform"  # uniform, weighted, expert, bayesian
    aggregation_result: float = 0.0      # Net support (-1.0 to 1.0)
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_supporting(self) -> int:
        """Count of supporting sources."""
        return len(self.supporting_sources)

    @property
    def total_contradicting(self) -> int:
        """Count of contradicting sources."""
        return len(self.contradicting_sources)

    @property
    def is_supported(self) -> bool:
        """Check if aggregation shows net support."""
        return self.aggregation_result > 0.1

    @property
    def is_contradicted(self) -> bool:
        """Check if aggregation shows contradiction."""
        return self.aggregation_result < -0.1

    @property
    def is_neutral(self) -> bool:
        """Check if aggregation is neutral."""
        return abs(self.aggregation_result) <= 0.1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "aggregation_identity": self.aggregation_identity,
            "supporting_sources": list(self.supporting_sources),
            "contradicting_sources": list(self.contradicting_sources),
            "weighting_strategy": self.weighting_strategy,
            "aggregation_result": self.aggregation_result,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EvidenceAggregation:
        """Create from dictionary (deterministic)."""
        return cls(
            aggregation_identity=data.get("aggregation_identity", ""),
            supporting_sources=tuple(data.get("supporting_sources", [])),
            contradicting_sources=tuple(data.get("contradicting_sources", [])),
            weighting_strategy=data.get("weighting_strategy", "uniform"),
            aggregation_result=float(data.get("aggregation_result", 0.0)),
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def create(
        cls,
        supporting: Tuple[str, ...] = (),
        contradicting: Tuple[str, ...] = (),
        strategy: str = "uniform",
    ) -> EvidenceAggregation:
        """Create new evidence aggregation."""
        return cls(
            aggregation_identity=f"aggregation:{uuid.uuid4().hex[:16]}",
            supporting_sources=supporting,
            contradicting_sources=contradicting,
            weighting_strategy=strategy,
            provenance={
                "created_at_utc": time.time(),
                "supporting_count": len(supporting),
                "contradicting_count": len(contradicting),
            },
        )

    def add_supporting(self, source: str) -> EvidenceAggregation:
        """Add a supporting evidence source."""
        return EvidenceAggregation(
            aggregation_identity=self.aggregation_identity,
            supporting_sources=self.supporting_sources + (source,),
            contradicting_sources=self.contradicting_sources,
            weighting_strategy=self.weighting_strategy,
            provenance={
                **self.provenance,
                "support_added_at_utc": time.time(),
                "new_supporting_source": source,
            },
        )

    def add_contradicting(self, source: str) -> EvidenceAggregation:
        """Add a contradicting evidence source."""
        return EvidenceAggregation(
            aggregation_identity=self.aggregation_identity,
            supporting_sources=self.supporting_sources,
            contradicting_sources=self.contradicting_sources + (source,),
            weighting_strategy=self.weighting_strategy,
            provenance={
                **self.provenance,
                "contradiction_added_at_utc": time.time(),
                "new_contradicting_source": source,
            },
        )

    def merge(self, other: EvidenceAggregation) -> EvidenceAggregation:
        """Merge two evidence aggregations."""
        # If strategies differ, use the more specific one or default
        strategy = self.weighting_strategy if self.weighting_strategy != "uniform" else other.weighting_strategy

        return EvidenceAggregation(
            aggregation_identity=f"aggregation:{uuid.uuid4().hex[:16]}",
            supporting_sources=self.supporting_sources + other.supporting_sources,
            contradicting_sources=self.contradicting_sources + other.contradicting_sources,
            weighting_strategy=strategy,
            provenance={
                **self.provenance,
                **other.provenance,
                "merged_at_utc": time.time(),
                "merged_from": [self.aggregation_identity, other.aggregation_identity],
            },
        )

    def weight(self, weights: Dict[str, float]) -> EvidenceAggregation:
        """
        Apply explicit weights to sources.
        
        Returns a new aggregation with weighted result.
        """
        # Simplified weighting: compute weighted sum
        support_sum = sum(weights.get(s, 1.0) for s in self.supporting_sources)
        contradict_sum = sum(weights.get(c, 1.0) for c in self.contradicting_sources)

        total_weight = support_sum + contradict_sum
        if total_weight == 0:
            result = 0.0
        else:
            result = (support_sum - contradict_sum) / total_weight

        return EvidenceAggregation(
            aggregation_identity=self.aggregation_identity,
            supporting_sources=self.supporting_sources,
            contradicting_sources=self.contradicting_sources,
            weighting_strategy="weighted",
            aggregation_result=result,
            provenance={
                **self.provenance,
                "weighted_at_utc": time.time(),
                "weighting_applied": list(weights.keys()),
            },
        )