# Perceptual Novelty Assessment - Phase 5.2.2
# ===========================================

"""
Novelty Assessment: Evaluates whether new patterns override habituation.

A novelty assessment determines if a change in a previously stable source
should trigger renewed processing emphasis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# NOVELTY KIND - What type of novelty was detected?
# =============================================================================


class NoveltyKind(Enum):
    """
    Kind of novelty detected.
    
    Kinds:
        STRUCTURAL:       Structure changed (pattern format different)
        TEMPORAL:         Timing changed significantly
        SPATIAL:          Spatial properties changed
        INTENSITY:        Intensity or magnitude changed
        SOURCE:           Source identity changed
        SCHEMA:           Schema structure changed
        SEMANTIC_CATEGORY: Category classification changed
        CONFIDENCE:       Confidence dropped unexpectedly
        QUALITY:          Quality degraded significantly
        PERMISSION_SCOPE: Permission or access scope changed
        SANDBOX_SCOPE:    Sandbox environment changed
    """
    
    STRUCTURAL = "structural"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    INTENSITY = "intensity"
    SOURCE = "source"
    SCHEMA = "schema"
    SEMANTIC_CATEGORY = "semantic_category"
    CONFIDENCE = "confidence"
    QUALITY = "quality"
    PERMISSION_SCOPE = "permission_scope"
    SANDBOX_SCOPE = "sandbox_scope"


# =============================================================================
# PERCEPTUAL NOVELTY ASSESSMENT - Novelty detection result
# =============================================================================


@dataclass(frozen=True)
class PerceptualNoveltyAssessment:
    """
    Assessment of novelty in a perceptual stream.
    
    Fields:
        assessment_identity:     Unique identifier for this assessment
        assessed_artifact:       Which artifact is being assessed?
        reference_pattern:       What was the expected pattern?
        deviation_kind:          What kind of deviation occurred?
        deviation_magnitude:     How large is the deviation?
        novelty_level:           Current novelty level (0.0-1.0)
        habituation_override:    Should this override habituation?
        confidence:              Confidence in novelty assessment
        uncertainty:             Known limitations of this assessment
    """
    
    assessment_identity: str            # Unique ID
    
    assessed_artifact: str              # Artifact being analyzed
    
    reference_pattern: Optional[str] = None  # Expected pattern description
    
    deviation_kind: Optional[NoveltyKind] = None  # What kind of change?
    deviation_magnitude: float = 0.0   # How much changed?
    
    novelty_level: float = 0.0         # Novelty level (0.0-1.0)
    
    habituation_override: bool = False  # Should override habituation?
    
    confidence: float = 0.5           # Assessment confidence
    uncertainty: float = 0.3         # Assessment uncertainty
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # History
    
    @property
    def is_significant_novelty(self) -> bool:
        """Check if this represents significant novelty."""
        return self.novelty_level > 0.5 and self.habituation_override
    
    @classmethod
    def no_novelty(
        cls,
        artifact_id: str,
        expected_pattern: Optional[str] = None,
    ) -> "PerceptualNoveltyAssessment":
        """
        Create assessment indicating no novelty detected.
        
        Args:
            artifact_id: Artifact analyzed
            expected_pattern: Expected pattern (optional)
            
        Returns:
            Assessment with zero novelty level
        """
        return cls(
            assessment_identity=f"novelty:{uuid.uuid4().hex[:16]}",
            assessed_artifact=artifact_id,
            reference_pattern=expected_pattern,
            novelty_level=0.0,
            confidence=0.8,
            uncertainty=0.2,
        )
    
    @classmethod
    def detected_novelty(
        cls,
        artifact_id: str,
        expected_pattern: Optional[str],
        deviation_kind: NoveltyKind,
        magnitude: float = 1.0,
        override_habituation: bool = True,
    ) -> "PerceptualNoveltyAssessment":
        """
        Create assessment indicating novelty was detected.
        
        Args:
            artifact_id: Artifact analyzed
            expected_pattern: What was expected?
            deviation_kind: What kind of change occurred?
            magnitude: How large is the deviation? (0.0-1.0)
            override_habituation: Should this reset habituation?
            
        Returns:
            Assessment with novelty level and override flag
        """
        return cls(
            assessment_identity=f"novelty:{uuid.uuid4().hex[:16]}",
            assessed_artifact=artifact_id,
            reference_pattern=expected_pattern,
            deviation_kind=deviation_kind,
            deviation_magnitude=magnitude,
            novelty_level=min(1.0, magnitude * 1.2),
            habituation_override=override_habituation,
            confidence=max(0.5, 0.8 - magnitude * 0.2),
            uncertainty=min(0.5, 0.3 + magnitude * 0.2),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary."""
        return {
            "assessment_identity": self.assessment_identity,
            "assessed_artifact": self.assessed_artifact,
            "reference_pattern": self.reference_pattern,
            "deviation_kind": self.deviation_kind.value if self.deviation_kind else None,
            "deviation_magnitude": self.deviation_magnitude,
            "novelty_level": self.novelty_level,
            "habituation_override": self.habituation_override,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptualNoveltyAssessment":
        """Create assessment from dictionary."""
        return cls(
            assessment_identity=data.get("assessment_identity", str(uuid.uuid4())),
            assessed_artifact=data.get("assessed_artifact", ""),
            reference_pattern=data.get("reference_pattern"),
            deviation_kind=NoveltyKind(data.get("deviation_kind")) if data.get("deviation_kind") else None,
            deviation_magnitude=float(data.get("deviation_magnitude", 0.0)),
            novelty_level=float(data.get("novelty_level", 0.0)),
            habituation_override=data.get("habituation_override", False),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.3)),
        )