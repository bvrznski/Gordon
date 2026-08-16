# Perceptual Translation - Phase 5.2.2
# ====================================

"""
Perceptual Translation: Converts source representations into canonical forms.

Translation changes representation without altering observational authority.
It enables common downstream contracts across heterogeneous modality sources.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PERCEPTUAL TRANSLATION - Representation conversion record
# =============================================================================


@dataclass(frozen=True)
class PerceptualTranslation:
    """
    Record of a perceptual representation translation.
    
    Fields:
        translation_identity:    Unique identifier for this translation
        source_artifacts:        Which artifacts were translated?
        source_representation:   Original representation description
        target_representation:   Target canonical representation
        mapping_revision:        Version of the mapping used
        preserved_semantics:     Semantics that survived translation
        omitted_semantics:       Semantics lost during translation
        derived_fields:          New fields created through translation
        confidence_effect:       How did confidence change?
        uncertainty_effect:      How did uncertainty change?
        information_loss:        Declared information loss
    """
    
    translation_identity: str           # Unique ID
    
    source_artifacts: Tuple[str, ...]  # Artifact IDs being translated
    
    source_representation: str         # e.g., "linux_process", "waveform_features"
    target_representation: str = ""    # e.g., "canonical_process", "auditory_percept"
    
    mapping_revision: int = 1          # Mapping version used
    
    preserved_semantics: Tuple[str, ...] = field(default_factory=tuple)
    omitted_semantics: Tuple[str, ...] = field(default_factory=tuple)
    derived_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    confidence_effect: str = "preserved"  # preserved, recalibrated, reduced
    uncertainty_effect: str = "unknown"   # unknown, increased, preserved
    
    information_loss: Optional["ProcessingInformationLoss"] = None  # noqa (from shared module)
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Translation history
    
    @property
    def is_valid(self) -> bool:
        """Check if translation has required fields."""
        return len(self.source_representation) > 0 and len(self.target_representation) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert translation to dictionary."""
        return {
            "translation_identity": self.translation_identity,
            "source_artifacts": list(self.source_artifacts),
            "source_representation": self.source_representation,
            "target_representation": self.target_representation,
            "mapping_revision": self.mapping_revision,
            "preserved_semantics": list(self.preserved_semantics),
            "omitted_semantics": list(self.omitted_semantics),
            "derived_fields": list(self.derived_fields),
            "confidence_effect": self.confidence_effect,
            "uncertainty_effect": self.uncertainty_effect,
        }
    
    @classmethod
    def create(
        cls,
        artifact_ids: List[str],
        source_repr: str,
        target_repr: str = "",
        mapping_revision: int = 1,
    ) -> "PerceptualTranslation":
        """Create a new translation record."""
        return cls(
            translation_identity=f"translate:{uuid.uuid4().hex[:16]}",
            source_artifacts=tuple(artifact_ids),
            source_representation=source_repr,
            target_representation=target_repr or f"canonical_{source_repr}",
            mapping_revision=mapping_revision,
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptualTranslation":
        """Create translation from dictionary."""
        return cls(
            translation_identity=data.get("translation_identity", str(uuid.uuid4())),
            source_artifacts=tuple(data.get("source_artifacts", [])),
            source_representation=data.get("source_representation", ""),
            target_representation=data.get("target_representation", ""),
            mapping_revision=int(data.get("mapping_revision", 1)),
            preserved_semantics=tuple(data.get("preserved_semantics", [])),
            omitted_semantics=tuple(data.get("omitted_semantics", [])),
            derived_fields=tuple(data.get("derived_fields", [])),
            confidence_effect=data.get("confidence_effect", "preserved"),
            uncertainty_effect=data.get("uncertainty_effect", "unknown"),
        )