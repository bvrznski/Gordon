# Perceptual Repetition Pattern - Phase 5.2.2
# ===========================================

"""
Repetition Pattern: Tracks and analyzes repetitive signal patterns.

A RepetitionPattern captures how signals repeat over time, enabling
habituation assessments to determine processing reduction opportunities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PERCEPTUAL REPETITION PATTERN - Signal repetition analysis
# =============================================================================


@dataclass(frozen=True)
class PerceptualRepetitionPattern:
    """
    Analysis of repetition pattern in a signal stream.
    
    Fields:
        pattern_identity:      Unique identifier for this pattern
        source_artifacts:      Which artifacts show the repetition?
        repeated_structure:    What structure is being repeated?
        repetition_count:      How many times has it been observed?
        repetition_interval:   Average time between repetitions (seconds)
        structural_variance:   How much does each instance vary?
        temporal_variance:     How consistent is the timing?
        stability:             Overall pattern stability (0.0-1.0)
        confidence:            Confidence in this pattern analysis
    """
    
    pattern_identity: str               # Unique ID
    
    source_artifacts: Tuple[str, ...]  # Artifact IDs showing repetition
    
    repeated_structure: str = ""       # Description of the repeated structure
    
    repetition_count: int = 1         # How many times observed?
    
    repetition_interval: float = 0.0  # Average interval in seconds
    structural_variance: float = 0.0  # Variance in structure (lower = more stable)
    temporal_variance: float = 0.0   # Variance in timing
    
    stability: float = 1.0            # Pattern stability (0.0-1.0)
    
    confidence: float = 0.5          # Analysis confidence (0.0-1.0)
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Analysis history
    
    @property
    def is_significant(self) -> bool:
        """Check if this pattern has enough observations to be significant."""
        return self.repetition_count >= 3 and self.stability > 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary."""
        return {
            "pattern_identity": self.pattern_identity,
            "source_artifacts": list(self.source_artifacts),
            "repeated_structure": self.repeated_structure,
            "repetition_count": self.repetition_count,
            "repetition_interval": self.repetition_interval,
            "structural_variance": self.structural_variance,
            "temporal_variance": self.temporal_variance,
            "stability": self.stability,
            "confidence": self.confidence,
        }
    
    @classmethod
    def create(
        cls,
        artifact_ids: List[str],
        structure_description: str = "",
        interval_seconds: float = 0.0,
    ) -> "PerceptualRepetitionPattern":
        """Create a new repetition pattern."""
        return cls(
            pattern_identity=f"repat:{uuid.uuid4().hex[:16]}",
            source_artifacts=tuple(artifact_ids),
            repeated_structure=structure_description,
            repetition_count=len(artifact_ids),
            repetition_interval=interval_seconds,
            stability=min(0.95, 0.5 + len(artifact_ids) * 0.1),
            confidence=min(0.8, 0.3 + len(artifact_ids) * 0.1),
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptualRepetitionPattern":
        """Create pattern from dictionary."""
        return cls(
            pattern_identity=data.get("pattern_identity", str(uuid.uuid4())),
            source_artifacts=tuple(data.get("source_artifacts", [])),
            repeated_structure=data.get("repeated_structure", ""),
            repetition_count=data.get("repetition_count", 1),
            repetition_interval=float(data.get("repetition_interval", 0.0)),
            structural_variance=float(data.get("structural_variance", 0.0)),
            temporal_variance=float(data.get("temporal_variance", 0.0)),
            stability=float(data.get("stability", 1.0)),
            confidence=float(data.get("confidence", 0.5)),
        )