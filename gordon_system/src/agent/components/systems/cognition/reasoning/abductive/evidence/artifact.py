# Abduction Evidence Artifact - Phase 7.3
# ======================================

"""
Evidence artifacts for abductive reasoning.

Evidence may originate from:
    - Perception (sensory input)
    - Memory (stored observations)
    - Knowledge (learned facts)
    - Reasoning (inferred results)
    - Execution (tool results)
    - External sources (APIs, files)
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class EvidenceSource(Enum):
    """Sources of evidence in abductive reasoning."""
    
    PERCEPTION = "perception"           # Direct sensory input
    MEMORY = "memory"                   # Stored observations
    KNOWLEDGE = "knowledge"             # Learned facts and rules
    REASONING = "reasoning"             # Derived from other reasoning
    EXECUTION = "execution"             # Tool or experiment results
    EXTERNAL = "external"               # External sources (APIs, files)
    EXPERT_OPINION = "expert_opinion"   # Expert assessment


class EvidenceKind(Enum):
    """Kinds of evidence."""
    
    OBSERVATION = "observation"         # Direct observation
    FACTUAL = "factual"                 # Verified fact
    MEASUREMENT = "measurement"         # Quantitative data
    ANECDOTAL = "anecdotal"             # Personal account
    LOGICAL_INFERENCE = "logical_inference"  # Derived logically
    STATISTICAL = "statistical"         # Statistical summary
    MODELED = "modeled"                 # Model prediction


@dataclass(frozen=True)
class AbductionEvidence:
    """
    A single piece of evidence for abductive reasoning.
    
    Evidence remains explicit and traceable through its provenance chain.
    """
    
    # Identity
    evidence_id: str                      # Unique identifier
    semantic_identity: str                # Stable identity across runs
    
    # Content
    evidence_content: Dict[str, Any]      # The actual evidence data
    evidence_description: str             # Human-readable description
    
    # Classification
    evidence_source: EvidenceSource       # Where did this come from?
    evidence_kind: EvidenceKind           # What kind of evidence is it?
    
    # Assessment
    confidence: float = 1.0               # Confidence in the evidence (0.0-1.0)
    quality_score: float = 1.0            # Quality rating (0.0-1.0)
    uncertainty: float = 0.0              # Remaining uncertainty
    
    # Context
    context_tags: Tuple[str, ...] = ()    # Tags for filtering/organization
    temporal_marker: Optional[float] = None  # When was this observed?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)  # Source chain
    
    @property
    def effective_confidence(self) -> float:
        """Calculate effective confidence considering quality and uncertainty."""
        return self.confidence * self.quality_score * (1.0 - self.uncertainty)
    
    @classmethod
    def create(
        cls,
        evidence_content: Dict[str, Any],
        evidence_description: str,
        evidence_source: EvidenceSource = EvidenceSource.PERCEPTION,
        evidence_kind: EvidenceKind = EvidenceKind.OBSERVATION,
        confidence: float = 1.0,
        quality_score: float = 1.0,
        uncertainty: float = 0.0,
        context_tags: Optional[List[str]] = None,
        provenance: Optional[Dict[str, str]] = None,
    ) -> AbductionEvidence:
        """Create a new evidence artifact."""
        return cls(
            evidence_id=f"evidence:{uuid.uuid4().hex[:16]}",
            semantic_identity=cls._generate_semantic_identity(evidence_content),
            evidence_content=evidence_content,
            evidence_description=evidence_description,
            evidence_source=evidence_source,
            evidence_kind=evidence_kind,
            confidence=confidence,
            quality_score=quality_score,
            uncertainty=uncertainty,
            context_tags=tuple(context_tags or []),
            provenance=provenance or {},
        )
    
    @staticmethod
    def _generate_semantic_identity(content: Dict[str, Any]) -> str:
        """Generate a stable semantic identity from content."""
        # Simple hash-based identity generation
        import hashlib
        content_str = str(sorted(content.items()))
        return f"semantic:{hashlib.md5(content_str.encode()).hexdigest()[:16]}"
    
    def with_context(self, context_tags: List[str]) -> "AbductionEvidence":
        """Return a copy with added context tags."""
        return dataclass_replace(
            self,
            context_tags=context_tags if isinstance(context_tags, tuple) else tuple(context_tags),
        )
    
    def update_confidence(self, new_confidence: float, new_quality: Optional[float] = None, new_uncertainty: Optional[float] = None) -> "AbductionEvidence":
        """Return a copy with updated confidence metrics."""
        return dataclass_replace(
            self,
            confidence=new_confidence,
            quality_score=new_quality if new_quality is not None else self.quality_score,
            uncertainty=new_uncertainty if new_uncertainty is not None else 1.0 - new_confidence,
        )


@dataclass(frozen=True)
class EvidenceArtifact:
    """
    A wrapper for evidence artifacts in abductive reasoning.
    
    This provides a consistent interface for different types of evidence
    while preserving their original format and provenance.
    """
    
    # Identity
    artifact_id: str                      # Unique identifier
    
    # Artifact details
    artifact_type: str                    # Type name (e.g., "log_entry", "measurement")
    artifact_data: Dict[str, Any]         # Raw artifact data
    
    # Classification
    source_type: EvidenceSource           # Primary source
    kind_type: EvidenceKind               # What kind of evidence?
    
    # Assessment
    confidence: float = 0.5               # Confidence in the artifact
    completeness: float = 1.0             # How complete is this artifact?
    
    # Context
    timestamp_utc: Optional[float] = None
    
    @property
    def effective_confidence(self) -> float:
        """Calculate effective confidence."""
        return self.confidence * self.completeness
    
    @classmethod
    def from_evidence(cls, evidence: AbductionEvidence) -> "EvidenceArtifact":
        """Create an artifact from abductive evidence."""
        return cls(
            artifact_id=evidence.evidence_id,
            artifact_type="abduction_evidence",
            artifact_data=dict(evidence.evidence_content),
            source_type=evidence.evidence_source,
            kind_type=evidence.evidence_kind,
            confidence=evidence.confidence,
            completeness=evidence.quality_score * (1.0 - evidence.uncertainty),
            timestamp_utc=evidence.created_at_utc,
        )


@dataclass(frozen=True)
class EvidenceQuality:
    """
    Quality assessment for a set of evidence.
    
    This provides overall quality metrics for an evidence set, including:
        - Average confidence
        - Coverage breadth
        - Source reliability distribution
        - Temporal completeness
    """
    
    # Identity
    quality_id: str                       # Unique identifier
    
    # Metrics
    average_confidence: float             # Mean confidence across all evidence
    total_evidence_count: int             # Total number of evidence items
    high_quality_count: int               # Evidence with confidence >= 0.8
    
    # Source reliability
    source_reliability_avg: float = 1.0   # Average source reliability score
    source_diversity: int = 1             # Number of unique sources
    
    # Temporal coverage
    temporal_span_seconds: float = 0.0    # Time span covered
    recent_evidence_ratio: float = 1.0    # Ratio of recent evidence (last hour)
    
    @property
    def overall_quality_score(self) -> float:
        """Calculate overall quality score."""
        return (
            self.average_confidence * 0.4 +
            min(self.high_quality_count / max(self.total_evidence_count, 1), 1.0) * 0.3 +
            self.source_reliability_avg * 0.2 +
            (1.0 if self.recent_evidence_ratio > 0.5 else 0.5) * 0.1
        )
    
    @classmethod
    def calculate(cls, evidences: Tuple[AbductionEvidence, ...]) -> "EvidenceQuality":
        """Calculate quality metrics from a set of evidence."""
        if not evidences:
            return cls(
                quality_id="quality:empty",
                average_confidence=0.5,
                total_evidence_count=0,
                high_quality_count=0,
            )
        
        confidences = [e.confidence for e in evidences]
        avg_confidence = sum(confidences) / len(confidences)
        
        sources = set(e.evidence_source for e in evidences)
        recent_threshold = time.time() - 3600  # Last hour
        
        recent_count = sum(1 for e in evidences if e.created_at_utc > recent_threshold)
        
        return cls(
            quality_id=f"quality:{uuid.uuid4().hex[:16]}",
            average_confidence=avg_confidence,
            total_evidence_count=len(evidences),
            high_quality_count=sum(1 for c in confidences if c >= 0.8),
            source_diversity=len(sources),
            recent_evidence_ratio=recent_count / len(evidences) if evidences else 0.0,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AbductionEvidence",
    "EvidenceSource",
    "EvidenceKind",
    "EvidenceArtifact",
    "EvidenceQuality",
]