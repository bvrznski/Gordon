# Habituation Assessment - Phase 5.2.2
# ====================================

"""
Habituation Assessment: Evaluates repetition patterns and determines processing emphasis.

A HabituationAssessment determines whether a source stream has become repetitive
enough to warrant reduced processing priority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# HABITUATION LEVEL - How much reduction in emphasis?
# =============================================================================


class HabituationLevel(Enum):
    """
    Level of habituation applied to a source.
    
    Levels:
        NONE:           Full processing priority maintained
        LOW:          Slightly reduced emphasis for known patterns
        MODERATE:     Noticeably reduced emphasis
        HIGH:         Significantly reduced processing
        SATURATED:    Maximum reduction, but still monitoring for novelty
        SUSPENDED:    Processing suspended pending novelty detection
        RESET:        Habituation reset, returning to full processing
    """
    
    NONE = "none"           # Full processing
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SATURATED = "saturated"
    SUSPENDED = "suspended"
    RESET = "reset"


# =============================================================================
# HABITUATION ASSESSMENT - Evaluation of habituation needs
# =============================================================================


@dataclass(frozen=True)
class HabituationAssessment:
    """
    Assessment of habituation level for a source stream.
    
    Fields:
        assessment_identity:     Unique identifier for this assessment
        source_stream:           Which source stream is being assessed?
        assessed_artifacts:      Which artifacts were analyzed?
        repetition_pattern:      Observed repetition pattern (optional)
        stability_measure:       How stable has the stream been?
        expectedness_measure:    How expected are these patterns?
        novelty_measure:         Current novelty level
        habituation_level:       Recommended habituation level
        recommended_processing_reduction: What reduction is recommended?
        confidence:              Confidence in this assessment
        uncertainty:             Known limitations of this assessment
        provenance:              Origin tracking with pattern history
    """
    
    assessment_identity: str            # Unique ID
    
    source_stream: str                 # Source identifier being assessed
    
    assessed_artifacts: Tuple[str, ...]  # Artifacts analyzed
    
    repetition_pattern: Optional["PerceptualRepetitionPattern"] = None  # Pattern analysis
    
    stability_measure: float = 0.5     # Stability score (0.0-1.0)
    expectedness_measure: float = 0.5  # Expectedness score
    novelty_measure: float = 0.0       # Novelty level (0.0 = no novelty, high = new patterns)
    
    habituation_level: HabituationLevel = HabituationLevel.NONE
    
    recommended_processing_reduction: str = "none"  # e.g., "50%", "no change"
    
    confidence: float = 0.5           # Assessment confidence (0.0-1.0)
    uncertainty: float = 0.3         # Assessment uncertainty (0.0-1.0)
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Pattern history
    
    @property
    def should_reduce_processing(self) -> bool:
        """Check if processing should be reduced."""
        return self.habituation_level in (
            HabituationLevel.LOW,
            HabituationLevel.MODERATE,
            HabituationLevel.HIGH,
            HabituationLevel.SATURATED,
        )
    
    @classmethod
    def new_source(
        cls,
        source_stream: str,
        artifact_ids: List[str],
    ) -> "HabituationAssessment":
        """
        Create assessment for a new source (no habituation yet).
        
        Args:
            source_stream: Source identifier
            artifact_ids: Initial artifacts analyzed
            
        Returns:
            Assessment with NONE level, full processing recommended
        """
        return cls(
            assessment_identity=f"habit:{uuid.uuid4().hex[:16]}",
            source_stream=source_stream,
            assessed_artifacts=tuple(artifact_ids),
            habituation_level=HabituationLevel.NONE,
            confidence=0.3,
            uncertainty=0.7,
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
                "initial_assessment": True,
            },
        )
    
    @classmethod
    def high_habituation(
        cls,
        source_stream: str,
        artifact_ids: List[str],
        stability: float = 0.95,
        expectedness: float = 0.9,
        novelty: float = 0.05,
        pattern: Optional["PerceptualRepetitionPattern"] = None,  # noqa
    ) -> "HabituationAssessment":
        """
        Create assessment with high habituation level.
        
        Args:
            source_stream: Source identifier
            artifact_ids: Analyzed artifacts
            stability: How stable is the pattern?
            expectedness: How expected are these patterns?
            novelty: Current novelty level (low = less novel)
            pattern: Repetition pattern analysis (optional)
            
        Returns:
            Assessment with high habituation, reduced processing recommended
        """
        return cls(
            assessment_identity=f"habit:{uuid.uuid4().hex[:16]}",
            source_stream=source_stream,
            assessed_artifacts=tuple(artifact_ids),
            repetition_pattern=pattern,
            stability_measure=stability,
            expectedness_measure=expectedness,
            novelty_measure=novelty,
            habituation_level=HabituationLevel.SATURATED,
            recommended_processing_reduction="maximum",
            confidence=min(0.9, 0.5 + stability * 0.3),
            uncertainty=max(0.1, (1.0 - stability) * 0.3 + novelty * 0.2),
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
                "source_stable_for_n_patterns": pattern.repetition_count if pattern else 0,
            },
        )
    
    @classmethod
    def reset_habituation(
        cls,
        source_stream: str,
        artifact_ids: List[str],
        reason: str = "novelty_detected",
    ) -> "HabituationAssessment":
        """
        Reset habituation for a source.
        
        Args:
            source_stream: Source identifier
            artifact_ids: Analyzed artifacts
            reason: Why was habituation reset?
            
        Returns:
            Assessment with RESET level, full processing resumed
        """
        return cls(
            assessment_identity=f"habit:{uuid.uuid4().hex[:16]}",
            source_stream=source_stream,
            assessed_artifacts=tuple(artifact_ids),
            habituation_level=HabituationLevel.RESET,
            confidence=0.5,
            uncertainty=0.3,
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
                "reset_reason": reason,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary."""
        return {
            "assessment_identity": self.assessment_identity,
            "source_stream": self.source_stream,
            "assessed_artifacts": list(self.assessed_artifacts),
            "repetition_pattern": self.repetition_pattern.to_dict() if self.repetition_pattern else None,
            "stability_measure": self.stability_measure,
            "expectedness_measure": self.expectedness_measure,
            "novelty_measure": self.novelty_measure,
            "habituation_level": self.habituation_level.value,
            "recommended_processing_reduction": self.recommended_processing_reduction,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HabituationAssessment":
        """Create assessment from dictionary."""
        return cls(
            assessment_identity=data.get("assessment_identity", str(uuid.uuid4())),
            source_stream=data.get("source_stream", ""),
            assessed_artifacts=tuple(data.get("assessed_artifacts", [])),
            stability_measure=float(data.get("stability_measure", 0.5)),
            expectedness_measure=float(data.get("expectedness_measure", 0.5)),
            novelty_measure=float(data.get("novelty_measure", 0.0)),
            habituation_level=HabituationLevel(data.get("habituation_level", "none")),
            recommended_processing_reduction=data.get("recommended_processing_reduction", "none"),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.3)),
        )