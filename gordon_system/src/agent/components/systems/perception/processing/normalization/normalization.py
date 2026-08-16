# Perceptual Normalization - Phase 5.2.2
# =======================================

"""
Perceptual Normalization: Converts heterogeneous values to canonical forms.

Normalization improves comparability by converting different conventions,
units, and formats to shared canonical representations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PERCEPTUAL NORMALIZATION - Value conversion record
# =============================================================================


@dataclass(frozen=True)
class PerceptualNormalization:
    """
    Record of a perceptual value normalization.
    
    Fields:
        normalization_identity:  Unique identifier for this normalization
        source_artifacts:        Which artifacts were normalized?
        normalization_kind:      What kind of normalization was applied?
        source_convention:       Original convention used
        target_convention:       Target canonical convention
        original_values:         Original values before normalization
        normalized_values:       Normalized values after conversion
        precision_effect:        How did precision change?
        confidence_effect:       How did confidence change?
        uncertainty_effect:      How did uncertainty change?
    """
    
    normalization_identity: str         # Unique ID
    
    source_artifacts: Tuple[str, ...]  # Artifact IDs being normalized
    
    normalization_kind: str = ""       # e.g., "unit", "range", "coordinate", "time"
    source_convention: str = ""        # Original convention (e.g., "bytes")
    target_convention: str = ""        # Target convention (e.g., "kibibytes")
    
    original_values: Tuple[float, ...] = field(default_factory=tuple)
    normalized_values: Tuple[float, ...] = field(default_factory=tuple)
    
    precision_effect: str = "unknown"  # unknown, preserved, reduced
    confidence_effect: str = "preserved"
    uncertainty_effect: str = "unknown"
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Normalization history
    
    @property
    def is_valid(self) -> bool:
        """Check if normalization has required fields."""
        return (
            len(self.normalization_kind) > 0 and
            len(self.source_convention) > 0 and
            len(self.target_convention) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert normalization to dictionary."""
        return {
            "normalization_identity": self.normalization_identity,
            "source_artifacts": list(self.source_artifacts),
            "normalization_kind": self.normalization_kind,
            "source_convention": self.source_convention,
            "target_convention": self.target_convention,
            "original_values": list(self.original_values),
            "normalized_values": list(self.normalized_values),
            "precision_effect": self.precision_effect,
            "confidence_effect": self.confidence_effect,
            "uncertainty_effect": self.uncertainty_effect,
        }
    
    @classmethod
    def create(
        cls,
        artifact_ids: List[str],
        normalization_kind: str = "",
        source_convention: str = "",
        target_convention: str = "",
        original_values: Optional[List[float]] = None,
        normalized_values: Optional[List[float]] = None,
    ) -> "PerceptualNormalization":
        """Create a new normalization record."""
        return cls(
            normalization_identity=f"normalize:{uuid.uuid4().hex[:16]}",
            source_artifacts=tuple(artifact_ids),
            normalization_kind=normalization_kind or "unit",
            source_convention=source_convention,
            target_convention=target_convention,
            original_values=tuple(original_values or []),
            normalized_values=tuple(normalized_values or []),
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptualNormalization":
        """Create normalization from dictionary."""
        return cls(
            normalization_identity=data.get("normalization_identity", str(uuid.uuid4())),
            source_artifacts=tuple(data.get("source_artifacts", [])),
            normalization_kind=data.get("normalization_kind", ""),
            source_convention=data.get("source_convention", ""),
            target_convention=data.get("target_convention", ""),
            original_values=tuple(data.get("original_values", [])),
            normalized_values=tuple(data.get("normalized_values", [])),
            precision_effect=data.get("precision_effect", "unknown"),
            confidence_effect=data.get("confidence_effect", "preserved"),
            uncertainty_effect=data.get("uncertainty_effect", "unknown"),
        )