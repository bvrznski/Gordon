# Perception Percept - Phase 5.2 Modality-Independent Representation
# =================================================================

"""
Perception Percept: The first modality-independent representation.

A Percept is the first stable perceptual hypothesis about the environment.
Unlike Features, Percepts possess semantic identity.

Examples: person, keyboard, window, command, speech, vehicle, text

Percept Laws:
    PERCEPT-LAW-001: Every Percept shall reference supporting Features
    PERCEPT-LAW-002: Every Percept shall preserve supporting Observations
    PERCAT-LAW-003: Percepts shall preserve semantic identity
    PERCAT-LAW-004: Percepts shall preserve confidence
    PERCAT-LAW-005: Percepts shall preserve uncertainty
    PERCAT-LAW-006: Percepts shall preserve provenance
    PERCAT-LAW-007: Percepts shall remain revisable
    PERCAT-LAW-008: Percept construction shall remain deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class Percept:
    """
    Stable perceptual hypothesis about the environment.
    
    Unlike Features, Percepts possess semantic identity (e.g., "person", "keyboard").
    
    Percept Properties:
        identity:         Unique identifier
        category:         Semantic category (e.g., "person", "vehicle")
        confidence:       Confidence in this identification 0.0-1.0
        location:         Spatial/temporal location (optional)
        orientation:      Orientation/pose (optional)
        
        supporting_features: References to Features that support this percept
        supporting_observations: References to Observations
        
        revision:         Revision number for this percept
        provenance:       Origin tracking
    """
    
    identity: str                      # Unique identifier
    
    category: str                     # Semantic category (e.g., "person", "vehicle")
    confidence: float = 1.0           # Identification confidence (0.0-1.0)
    uncertainty: float = 0.0          # Known limitations (completely independent)
    
    location: Optional[Tuple[float, float]] = None  # x,y or timestamp
    orientation: Optional[str] = None                # Orientation description
    
    supporting_features: Tuple[str, ...] = field(default_factory=tuple)  # Feature refs
    supporting_observations: Tuple[str, ...] = field(default_factory=tuple)  # Obs refs
    
    revision: int = 1                 # Revision number
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_valid(self) -> bool:
        """Check if percept has minimal required data."""
        return (
            len(self.identity) > 0 and
            len(self.category) > 0 and
            0.0 <= self.confidence <= 1.0
        )
    
    @classmethod
    def from_features(
        cls,
        category: str,
        feature_ids: List[str],
        confidence: float = 1.0,
        uncertainty: float = 0.0,
        location: Optional[Tuple[float, float]] = None,
        orientation: Optional[str] = None,
        observation_ids: Optional[List[str]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "Percept":
        """
        Create a Percept from supporting features.
        
        Args:
            category: Semantic category
            feature_ids: List of supporting Feature IDs
            confidence: Identification confidence 0.0-1.0
            uncertainty: Known limitations (independent measure)
            location: Spatial/temporal location (optional)
            orientation: Orientation description (optional)
            observation_ids: Supporting Observation IDs (optional)
            provenance: Origin tracking dict (optional)
            
        Returns:
            New Percept instance
        """
        return cls(
            identity=f"percept:{uuid.uuid4().hex[:24]}",
            category=category,
            confidence=confidence,
            uncertainty=uncertainty,
            location=location,
            orientation=orientation,
            supporting_features=tuple(feature_ids),
            supporting_observations=tuple(observation_ids or []),
            revision=1,
            provenance=provenance or {"origin": "system"},
        )


class PerceptBuilder:
    """
    Mutable builder for constructing percepts.
    
    Usage:
        percept = (PerceptBuilder()
            .set_category("person")
            .add_feature(feature_id)
            .set_confidence(0.95)
            .build())
    """
    
    def __init__(self):
        self._identity: str = f"percept:{uuid.uuid4().hex[:24]}"
        self._category: str = "unknown"
        self._confidence: float = 1.0
        self._uncertainty: float = 0.0
        self._location: Optional[Tuple[float, float]] = None
        self._orientation: Optional[str] = None
        self._supporting_features: List[str] = []
        self._supporting_observations: List[str] = []
        self._revision: int = 1
        self._provenance: Dict[str, Any] = {"origin": "system"}
    
    def set_identity(self, identity: str) -> "PerceptBuilder":
        """Set the percept ID."""
        self._identity = identity
        return self
    
    def set_category(self, category: str) -> "PerceptBuilder":
        """Set semantic category."""
        self._category = category
        return self
    
    def set_confidence(self, confidence: float) -> "PerceptBuilder":
        """Set identification confidence 0.0-1.0."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        self._confidence = confidence
        return self
    
    def set_uncertainty(self, uncertainty: float) -> "PerceptBuilder":
        """Set known limitations (independent measure)."""
        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {uncertainty}")
        self._uncertainty = uncertainty
        return self
    
    def set_location(self, x: float, y: float) -> "PerceptBuilder":
        """Set spatial/temporal location."""
        self._location = (x, y)
        return self
    
    def set_orientation(self, orientation: str) -> "PerceptBuilder":
        """Set orientation description."""
        self._orientation = orientation
        return self
    
    def add_feature(self, feature_id: str) -> "PerceptBuilder":
        """Add a supporting Feature reference."""
        self._supporting_features.append(feature_id)
        return self
    
    def add_observation(self, observation_id: str) -> "PerceptBuilder":
        """Add a supporting Observation reference."""
        self._supporting_observations.append(observation_id)
        return self
    
    def set_revision(self, revision: int) -> "PerceptBuilder":
        """Set revision number."""
        if revision < 1:
            raise ValueError(f"Revision must be >= 1, got {revision}")
        self._revision = revision
        return self
    
    def set_provenance(self, provenance: Dict[str, Any]) -> "PerceptBuilder":
        """Set provenance tracking data."""
        self._provenance = provenance
        return self
    
    def build(self) -> Percept:
        """Build an immutable Percept."""
        if not self._category:
            raise ValueError("category is required")
        return Percept(
            identity=self._identity,
            category=self._category,
            confidence=self._confidence,
            uncertainty=self._uncertainty,
            location=self._location,
            orientation=self._orientation,
            supporting_features=tuple(self._supporting_features),
            supporting_observations=tuple(self._supporting_observations),
            revision=self._revision,
            provenance=dict(self._provenance),
        )


__all__ = [
    "Percept",
    "PerceptBuilder",
]