# Perception Feature - Phase 5.2 Structured Properties
# =====================================================

"""
Perception Feature: Structured properties computed from signals.

Features are structured descriptions computed from signals that reduce
signal complexity without yet identifying objects.

Feature Laws:
    FEATURE-LAW-001: Features shall be computed exclusively from Signals
    FEATURE-LAW-002: Features shall preserve supporting Signal references
    FEATURE-LAW-003: Features shall preserve provenance
    FEATURE-LAW-004: Features shall preserve confidence
    FEATURE-LAW-005: Features shall remain modality-local
    FEATURE-LAW-006: Features shall never become semantic objects automatically
    FEATURE-LAW-007: Feature revisions shall remain inspectable
    FEATURE-LAW-008: Feature extraction shall remain deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class Feature:
    """
    Structured property computed from a signal.
    
    Features reduce signal complexity. They do not yet identify objects.
    
    Examples: edges, corners, spectra, phonemes, embeddings, motion vectors
    
    Feature Properties:
        identity:         Unique identifier
        modality:         Modality of the source signal
        scale:            Scale/level at which feature was computed
        location:         Spatial/temporal location (optional)
        confidence:       Confidence in feature detection 0.0-1.0
        descriptor:       Feature descriptor vector or string
        supporting_signal: Reference to source Signal
    """
    
    identity: str                     # Unique identifier
    
    modality: str                     # vision, audio, speech, etc.
    scale: float = 1.0               # Scale at which computed (e.g., pixel density)
    
    location: Optional[Tuple[float, float]] = None  # x,y or timestamp
    confidence: float = 1.0          # Detection confidence
    
    descriptor: str = ""             # Feature descriptor (vector as string)
    supporting_signal_id: Optional[str] = None       # Source Signal reference
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_valid(self) -> bool:
        """Check if feature has minimal required data."""
        return (
            len(self.identity) > 0 and
            len(self.modality) > 0 and
            0.0 <= self.confidence <= 1.0
        )
    
    @classmethod
    def from_signal(
        cls,
        descriptor: str,
        modality: str,
        signal_id: Optional[str] = None,
        scale: float = 1.0,
        location: Optional[Tuple[float, float]] = None,
        confidence: float = 1.0,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "Feature":
        """
        Create a Feature from signal data.
        
        Args:
            descriptor: Feature descriptor (vector or string)
            modality: Modality of source signal
            signal_id: Source Signal reference (optional)
            scale: Scale at which computed
            location: Spatial/temporal location (optional)
            confidence: Detection confidence 0.0-1.0
            provenance: Origin tracking dict
            
        Returns:
            New Feature instance
        """
        return cls(
            identity=f"feat:{uuid.uuid4().hex[:24]}",
            modality=modality,
            scale=scale,
            location=location,
            confidence=confidence,
            descriptor=descriptor,
            supporting_signal_id=signal_id,
            provenance=provenance or {"origin": "system"},
        )


class FeatureBuilder:
    """
    Mutable builder for constructing features.
    
    Usage:
        feat = (FeatureBuilder()
            .set_modality("vision")
            .set_descriptor(descriptor_data)
            .build())
    """
    
    def __init__(self):
        self._identity: str = f"feat:{uuid.uuid4().hex[:24]}"
        self._modality: str = "unknown"
        self._scale: float = 1.0
        self._location: Optional[Tuple[float, float]] = None
        self._confidence: float = 1.0
        self._descriptor: str = ""
        self._supporting_signal_id: Optional[str] = None
        self._provenance: Dict[str, Any] = {"origin": "system"}
    
    def set_identity(self, identity: str) -> "FeatureBuilder":
        """Set the feature ID."""
        self._identity = identity
        return self
    
    def set_modality(self, modality: str) -> "FeatureBuilder":
        """Set source signal modality."""
        self._modality = modality
        return self
    
    def set_scale(self, scale: float) -> "FeatureBuilder":
        """Set computation scale."""
        if scale <= 0:
            raise ValueError(f"Scale must be > 0, got {scale}")
        self._scale = scale
        return self
    
    def set_location(self, x: float, y: float) -> "FeatureBuilder":
        """Set spatial/temporal location."""
        self._location = (x, y)
        return self
    
    def set_confidence(self, confidence: float) -> "FeatureBuilder":
        """Set detection confidence 0.0-1.0."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        self._confidence = confidence
        return self
    
    def set_descriptor(self, descriptor: str) -> "FeatureBuilder":
        """Set feature descriptor."""
        self._descriptor = descriptor
        return self
    
    def set_supporting_signal_id(self, signal_id: str) -> "FeatureBuilder":
        """Set source Signal reference."""
        self._supporting_signal_id = signal_id
        return self
    
    def set_provenance(self, provenance: Dict[str, Any]) -> "FeatureBuilder":
        """Set provenance tracking data."""
        self._provenance = provenance
        return self
    
    def build(self) -> Feature:
        """Build an immutable Feature."""
        if not self._descriptor and len(self._modality) == 0:
            raise ValueError("descriptor or modality is required")
        return Feature(
            identity=self._identity,
            modality=self._modality,
            scale=self._scale,
            location=self._location,
            confidence=self._confidence,
            descriptor=self._descriptor,
            supporting_signal_id=self._supporting_signal_id,
            provenance=dict(self._provenance),
        )