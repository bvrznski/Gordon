# Knowledge-Perception Grounding - Novelty Detection Contract
# ============================================================

"""
Novelty: Detection of perceptual patterns that don't match existing knowledge.

Novelty indicates insufficient correspondence without creating concepts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import uuid


# =============================================================================
# NOVELTY KINDS - What kind of novelty is this?
# =============================================================================


class NoveltyKind(Enum):
    """
    Kinds of novelty that can be detected.
    
    NEW_OBJECT: An object type not seen before
    NEW_EVENT: A new event pattern or sequence
    NEW_RELATION: A relationship between entities not previously observed
    NEW_BEHAVIOR: Behavior patterns from existing entities in new contexts
    NEW_STRUCTURE: Structural arrangement not encountered before
    NEW_PATTERN: Temporal or spatial pattern recognition novelty
    UNKNOWN: Undetermined novelty type
    """
    
    NEW_OBJECT = "new_object"
    NEW_EVENT = "new_event"
    NEW_RELATION = "new_relation"
    NEW_BEHAVIOR = "new_behavior"
    NEW_STRUCTURE = "new_structure"
    NEW_PATTERN = "new_pattern"
    UNKNOWN = "unknown"


# =============================================================================
# NOVELTY ASSESSMENT - Evaluation of perceptual novelty
# =============================================================================


@dataclass(frozen=True)
class NoveltyAssessment:
    """
    Assessment of whether a percept represents novel knowledge.
    
    Fields:
        novelty_identity:      Unique identifier for this assessment
        
        percept:               Reference to the assessed percept
        nearest_concepts:      References to semantically closest concepts
        
        novelty_kind:          What kind of novelty is detected?
        
        novelty_score:         Novelty score (0.0-1.0, higher = more novel)
        
        supporting_features:   Features suggesting novelty
        confidence:            Confidence in novelty assessment (0.0-1.0)
        uncertainty:           Uncertainty about this assessment
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    novelty_identity: str
    
    # Percept reference (required)
    percept: str                   # Reference to the assessed percept
    
    # Nearest known concepts
    nearest_concepts: Tuple[str, ...]  # Concept IDs with highest similarity
    
    # Novelty assessment (required)
    novelty_kind: str              # e.g., "new_object", "new_event"
    
    # Quality metrics (required)
    novelty_score: float = 0.5     # Novelty score (0.0-1.0, higher = more novel)
    
    supporting_features: Tuple[str, ...] = field(default_factory=tuple)   # Evidence of novelty
    confidence: float = 1.0        # Assessment confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about assessment
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate novelty assessment."""
        if not self.novelty_identity:
            raise ValueError("novelty_identity is required")
        if not 0.0 <= self.novelty_score <= 1.0:
            raise ValueError(f"Novelty score must be 0.0-1.0, got {self.novelty_score}")
    
    @property
    def is_significant_novelty(self) -> bool:
        """Check if this represents significant novelty (potential new concept)."""
        return self.novelty_score >= 0.7 and self.confidence >= 0.5
    
    @classmethod
    def create(
        cls,
        percept_id: str,
        nearest_concept_ids: List[str],
        novelty_kind: NoveltyKind = NoveltyKind.UNKNOWN,
        novelty_score: float = 0.5,
        supporting_features: Optional[List[str]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "NoveltyAssessment":
        """Create a new novelty assessment."""
        return cls(
            novelty_identity=f"novelty:{uuid.uuid4().hex[:24]}",
            percept=percept_id,
            nearest_concepts=tuple(nearest_concept_ids),
            novelty_kind=novelty_kind.value if isinstance(novelty_kind, Enum) else novelty_kind,
            novelty_score=max(0.0, min(1.0, float(novelty_score))),
            supporting_features=tuple(supporting_features or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary."""
        return {
            "novelty_identity": self.novelty_identity,
            "percept": self.percept,
            "nearest_concepts": list(self.nearest_concepts),
            "novelty_kind": self.novelty_kind,
            "novelty_score": self.novelty_score,
            "supporting_features": list(self.supporting_features),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# NOVELTY DETECTION - Detection pipeline results
# =============================================================================


@dataclass(frozen=True)
class NoveltyDetection:
    """
    Result of novelty detection for a percept.
    
    Fields:
        novelty_identity:      Unique identifier
        
        percept:               Reference to the detected percept
        nearest_known_concepts: References to closest concepts in knowledge base
        
        novelty_measure:       Numerical measure of novelty (0.0-1.0)
        novelty_kind:          Type of novelty detected
        
        supporting_features:   Features indicating novelty
        confidence:            Confidence in novelty detection (0.0-1.0)
        uncertainty:           Uncertainty about this result
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    novelty_identity: str
    
    # Percept reference (required)
    percept: str                   # Reference to the detected percept
    
    # Nearest known concepts
    nearest_known_concepts: Tuple[str, ...]  # Concept IDs with highest similarity
    
    # Novelty metrics (required)
    novelty_measure: float = 0.5   # Numerical novelty measure (0.0-1.0)
    novelty_kind: str = "unknown"  # Kind of novelty detected
    
    supporting_features: Tuple[str, ...] = field(default_factory=tuple)   # Evidence
    confidence: float = 1.0        # Detection confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about result
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate novelty detection."""
        if not self.novelty_identity:
            raise ValueError("novelty_identity is required")
    
    @property
    def is_novel(self) -> bool:
        """Check if this percept appears to be novel (not well-matched)."""
        return self.novelty_measure >= 0.6 and self.confidence >= 0.5
    
    @classmethod
    def create(
        cls,
        percept_id: str,
        nearest_concept_ids: List[str],
        novelty_measure: float = 0.5,
        novelty_kind: str = "unknown",
        supporting_features: Optional[List[str]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "NoveltyDetection":
        """Create a new novelty detection result."""
        return cls(
            novelty_identity=f"novelty_detection:{uuid.uuid4().hex[:24]}",
            percept=percept_id,
            nearest_known_concepts=tuple(nearest_concept_ids),
            novelty_measure=max(0.0, min(1.0, float(novelty_measure))),
            novelty_kind=novelty_kind,
            supporting_features=tuple(supporting_features or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert detection result to dictionary."""
        return {
            "novelty_identity": self.novelty_identity,
            "percept": self.percept,
            "nearest_known_concepts": list(self.nearest_known_concepts),
            "novelty_measure": self.novelty_measure,
            "novelty_kind": self.novelty_kind,
            "confidence": self.confidence,
        }


# =============================================================================
# NOVELTY DETECTION ENGINE - High-level detection results
# =============================================================================


@dataclass(frozen=True)
class NoveltyDetectionEngineResult:
    """
    Result from the novelty detection engine.
    
    Fields:
        result_identity:       Unique identifier
        
        assessment:            Detailed novelty assessment
        percept_embedding:     Embedding used for detection (optional)
        
        detected_novelty_count: Number of novel percepts in this batch
        total_processed_count:  Total percepts processed
        
        confidence:            Confidence in the overall detection result (0.0-1.0)
        uncertainty:           Uncertainty about results
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    result_identity: str
    
    # Assessment reference (required)
    assessment: NoveltyAssessment  # The detailed assessment
    
    # Processing stats
    percept_embedding: Optional[str] = None  # Reference to embedding used
    detected_novelty_count: int = 0          # Number of novel percepts found
    total_processed_count: int = 1           # Total percepts in batch
    
    confidence: float = 1.0        # Detection result confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about results
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def detection_rate(self) -> float:
        """Get the rate of novelty detection in this batch."""
        if self.total_processed_count == 0:
            return 0.0
        return self.detected_novelty_count / self.total_processed_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "result_identity": self.result_identity,
            "assessment": self.assessment.to_dict(),
            "percept_embedding": self.percept_embedding,
            "detected_novelty_count": self.detected_novelty_count,
            "total_processed_count": self.total_processed_count,
            "detection_rate": self.detection_rate,
        }


__all__ = [
    "NoveltyKind",
    "NoveltyAssessment",
    "NoveltyDetection",
    "NoveltyDetectionEngineResult",
]