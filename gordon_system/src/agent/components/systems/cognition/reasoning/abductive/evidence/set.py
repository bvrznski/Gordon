# Abduction Evidence Set - Phase 7.3
# ==================================

"""
Evidence sets for abductive reasoning.

An EvidenceSet defines:
    - Available evidence
    - Missing evidence
    - Source reliability
    - Quality constraints
    - Temporal scope

Evidence Sets remain immutable during evaluation.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class EvidenceSetIdentity:
    """
    Immutable identity for an evidence set.
    
    Allows replay and verification of abductive analysis.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Set context
    set_number: int = 1                       # For repeated evaluations
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, set_number: int = 1) -> EvidenceSetIdentity:
        """Create a new evidence set identity."""
        return cls(
            semantic_identity=semantic_identity,
            set_number=set_number,
        )


@dataclass(frozen=True)
class MissingEvidence:
    """
    Information about missing evidence in abductive reasoning.
    
    Helps identify gaps in the evidence base that would improve explanations.
    """
    
    # Identity
    missing_id: str                           # Unique identifier
    
    # Description
    required_information: str                 # What information is missing?
    expected_value_format: str                # What format should it be in?
    impact: str                               # How does this affect reasoning?
    
    # Assessment
    priority: float = 1.0                     # Priority for acquisition (0.0-1.0)
    uncertainty_reduction_potential: float = 0.5  # Expected reduction in uncertainty
    
    # Context
    context_tags: Tuple[str, ...] = ()        # Tags for organization
    temporal_requirement: Optional[float] = None  # When should this be available?
    
    @property
    def normalized_priority(self) -> float:
        """Calculate normalized priority considering impact."""
        return self.priority * self.uncertainty_reduction_potential
    
    @classmethod
    def create(
        cls,
        required_information: str,
        expected_value_format: str = "unknown",
        impact: str = "reduces explanation confidence",
        priority: float = 1.0,
        uncertainty_reduction_potential: float = 0.5,
        context_tags: Optional[List[str]] = None,
    ) -> MissingEvidence:
        """Create a new missing evidence record."""
        return cls(
            missing_id=f"missing:{uuid.uuid4().hex[:16]}",
            required_information=required_information,
            expected_value_format=expected_value_format,
            impact=impact,
            priority=priority,
            uncertainty_reduction_potential=uncertainty_reduction_potential,
            context_tags=tuple(context_tags or []),
        )


@dataclass(frozen=True)
class EvidenceSet:
    """
    A complete set of evidence for abductive reasoning.
    
    An evidence set contains all available and missing evidence with
    quality metrics, source information, and provenance tracking.
    """
    
    # Identity
    evidence_set_id: str                      # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Evidence
    participating_evidence: Tuple[Dict[str, Any], ...]  # Available evidence items
    missing_evidence_items: Tuple[MissingEvidence, ...] = ()  # Missing pieces
    
    # Quality metrics
    total_count: int = 0                      # Total evidence count
    high_quality_count: int = 0               # High confidence evidence
    
    # Source analysis
    source_diversity: int = 1                 # Number of unique sources
    average_confidence: float = 0.5           # Average confidence across all evidence
    
    # Temporal scope
    earliest_timestamp_utc: Optional[float] = None
    latest_timestamp_utc: Optional[float] = None
    
    @property
    def uncertainty(self) -> float:
        """Calculate overall uncertainty in the set."""
        if self.total_count == 0:
            return 1.0
        return max(0.0, 1.0 - self.average_confidence)
    
    @property
    def quality_score(self) -> float:
        """Calculate overall quality score."""
        return (
            self.average_confidence * 0.6 +
            (self.high_quality_count / max(self.total_count, 1)) * 0.3 +
            min(1.0, self.source_diversity / 3.0) * 0.1
        )
    
    def has_missing_evidence(self) -> bool:
        """Check if there is missing evidence."""
        return len(self.missing_evidence_items) > 0
    
    def get_priority_missing(self) -> Tuple[MissingEvidence, ...]:
        """Get missing evidence sorted by priority."""
        return tuple(sorted(
            self.missing_evidence_items,
            key=lambda m: -m.normalized_priority
        ))
    
    @classmethod
    def create(
        cls,
        participating_evidence: List[Dict[str, Any]],
        semantic_identity: str,
        missing_evidence: Optional[List[MissingEvidence]] = None,
        source_diversity: int = 1,
        average_confidence: float = 0.5,
    ) -> EvidenceSet:
        """Create a new evidence set."""
        evidences = tuple(participating_evidence)
        
        # Calculate quality metrics
        high_count = sum(1 for e in evidences if e.get("confidence", 0.5) >= 0.8)
        
        timestamps = [e.get("temporal_marker") for e in evidences if e.get("temporal_marker")]
        
        return cls(
            evidence_set_id=f"evidence_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_evidence=evidences,
            missing_evidence_items=tuple(missing_evidence or []),
            total_count=len(evidences),
            high_quality_count=high_count,
            source_diversity=source_diversity,
            average_confidence=average_confidence,
            earliest_timestamp_utc=min(timestamps) if timestamps else None,
            latest_timestamp_utc=max(timestamps) if timestamps else None,
        )
    
    def filter_by_source(self, source: str) -> "EvidenceSet":
        """Return a filtered set containing only evidence from specified source."""
        filtered = tuple(
            e for e in self.participating_evidence
            if e.get("source", "") == source
        )
        return dataclass_replace(
            self,
            participating_evidence=filtered,
            total_count=len(filtered),
            high_quality_count=sum(1 for e in filtered if e.get("confidence", 0.5) >= 0.8),
        )
    
    def filter_by_confidence(self, min_confidence: float = 0.5) -> "EvidenceSet":
        """Return a filtered set containing only evidence with confidence >= threshold."""
        filtered = tuple(
            e for e in self.participating_evidence
            if e.get("confidence", 0.0) >= min_confidence
        )
        return dataclass_replace(
            self,
            participating_evidence=filtered,
            total_count=len(filtered),
            high_quality_count=sum(1 for e in filtered if e.get("confidence", 0.5) >= 0.8),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "EvidenceSetIdentity",
    "MissingEvidence",
    "EvidenceSet",
]