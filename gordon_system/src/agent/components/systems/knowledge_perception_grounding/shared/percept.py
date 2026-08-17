# Knowledge-Perception Grounding - Percept Contract
# ===================================================

"""
Percept: An integrated interpretation produced by the Perception System.

A Percept is not raw observation; it is an interpretation that integrates
multiple observations to form a coherent perceptual hypothesis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import uuid


# =============================================================================
# PERCEPT KINDS - What kind of percept is this?
# =============================================================================


class PerceptKind(Enum):
    """
    Kinds of percepts (describing the perceptual interpretation).
    
    OBJECT: Visual or spatial object detected
    PERSON: Human being identified
    COMMAND: Command execution result
    TEXT: Text content interpreted
    AUDIO_EVENT: Sound event classified
    SENSORY_EVENT: General sensory pattern
    UNKNOWN: Unspecified percept kind
    """
    
    OBJECT = "object"
    PERSON = "person"
    COMMAND = "command"
    TEXT = "text"
    AUDIO_EVENT = "audio_event"
    VISUAL_SCENE = "visual_scene"
    GESTURE = "gesture"
    ACTION = "action"
    UNKNOWN = "unknown"


# =============================================================================
# PERCEPT - Canonical percept structure
# =============================================================================


@dataclass(frozen=True)
class Percept:
    """
    Integrated interpretation produced by the Perception System.
    
    A Percept integrates multiple observations to produce a coherent
    perceptual hypothesis. Percepts remain perceptual - they are not
    Knowledge Artifacts.
    
    Fields:
        percept_identity:      Unique identifier for this percept
        
        observations:          References to supporting observations
        percept_kind:          What kind of percept is this?
        
        feature_summary:       Summary of key features
        spatial_context:       Spatial context (optional)
        temporal_context:      Temporal context (optional)
        
        confidence:            Confidence in this percept (0.0-1.0)
        uncertainty:           Uncertainty about this percept
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    percept_identity: str
    
    # Observation references (required)
    observations: Tuple[str, ...]  # References to supporting observations
    
    # Percept description (required)
    percept_kind: str              # e.g., "object", "person"
    
    # Features
    feature_summary: Dict[str, Any] = field(default_factory=dict)  # Key features
    spatial_context: Optional[Tuple[float, float]] = None          # x,y position
    temporal_context: Tuple[float, float] = (0.0, 0.0)             # start, end timestamps
    
    # Quality metrics (required)
    confidence: float = 1.0        # Confidence in this percept (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about this percept
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate percept."""
        if not self.percept_identity:
            raise ValueError("percept_identity is required")
        if len(self.observations) == 0:
            raise ValueError("Percepts must reference at least one observation")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
    
    @property
    def is_valid(self) -> bool:
        """Check if percept has minimal required data."""
        return (
            len(self.percept_identity) > 0 and
            len(self.observations) > 0 and
            len(self.percept_kind) > 0 and
            0.0 <= self.confidence <= 1.0
        )
    
    @classmethod
    def from_observations(
        cls,
        percept_kind: str,
        observation_ids: List[str],
        feature_summary: Optional[Dict[str, Any]] = None,
        spatial_context: Optional[Tuple[float, float]] = None,
        temporal_context: Optional[Tuple[float, float]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "Percept":
        """
        Create a Percept from supporting observations.
        
        Args:
            percept_kind: Semantic category of the percept
            observation_ids: References to supporting observations
            feature_summary: Key features detected (optional)
            spatial_context: Spatial location if applicable (optional)
            temporal_context: (start, end) timestamps (optional)
            confidence: Confidence in this percept (0.0-1.0)
            uncertainty: Uncertainty about this percept
            provenance: Origin tracking dict
        
        Returns:
            New Percept instance
        """
        return cls(
            percept_identity=f"percept:{uuid.uuid4().hex[:24]}",
            observations=tuple(observation_ids),
            percept_kind=percept_kind,
            feature_summary=feature_summary or {},
            spatial_context=spatial_context,
            temporal_context=temporal_context or (0.0, 0.0),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            provenance=provenance or {"origin": "system"},
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert percept to dictionary for serialization."""
        return {
            "percept_identity": self.percept_identity,
            "observations": list(self.observations),
            "percept_kind": self.percept_kind,
            "feature_summary": dict(self.feature_summary),
            "spatial_context": list(self.spatial_context) if self.spatial_context else None,
            "temporal_context": list(self.temporal_context),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Percept":
        """Create percept from dictionary."""
        spatial = data.get("spatial_context")
        temporal = data.get("temporal_context", [0.0, 0.0])
        
        return cls(
            percept_identity=data.get("percept_identity", str(uuid.uuid4())),
            observations=tuple(data.get("observations", [])),
            percept_kind=data.get("percept_kind", ""),
            feature_summary=dict(data.get("feature_summary", {})),
            spatial_context=tuple(spatial) if spatial else None,
            temporal_context=tuple(temporal),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# PERCEPT GROUP - Multiple percepts forming one semantic candidate
# =============================================================================


@dataclass(frozen=True)
class PerceptGroup:
    """
    Groups multiple percepts that form a single semantic candidate.
    
    Example: window button, cursor → GUI interaction
    
    Fields:
        group_identity:        Unique identifier for this group
        
        member_percepts:       References to the grouped percepts
        grouping_reason:       Why were these grouped together?
        
        temporal_window:       Time span covered by this grouping
        confidence:            Confidence in the grouping (0.0-1.0)
        uncertainty:           Uncertainty about this grouping
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    group_identity: str
    
    # Group members (required)
    member_percepts: Tuple[str, ...]  # Percept IDs
    
    # Grouping description (required)
    grouping_reason: str              # e.g., "GUI_interaction", "temporal_coherence"
    
    # Context
    temporal_window: Tuple[float, float] = (0.0, 0.0)  # start, end timestamps
    
    # Quality metrics (required)
    confidence: float = 1.0           # Grouping confidence (0.0-1.0)
    uncertainty: float = 0.0          # Uncertainty about grouping
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate percept group."""
        if not self.group_identity:
            raise ValueError("group_identity is required")
        if len(self.member_percepts) < 2:
            raise ValueError("PerceptGroup must contain at least 2 percepts")
    
    @property
    def duration_sec(self) -> float:
        """Get grouping time span in seconds."""
        return self.temporal_window[1] - self.temporal_window[0]
    
    @classmethod
    def create(
        cls,
        member_percept_ids: List[str],
        grouping_reason: str,
        temporal_window_start: float = 0.0,
        temporal_window_end: float = 0.0,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "PerceptGroup":
        """Create a new percept group."""
        return cls(
            group_identity=f"percept_group:{uuid.uuid4().hex[:24]}",
            member_percepts=tuple(member_percept_ids),
            grouping_reason=grouping_reason,
            temporal_window=(temporal_window_start, temporal_window_end),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert group to dictionary."""
        return {
            "group_identity": self.group_identity,
            "member_percepts": list(self.member_percepts),
            "grouping_reason": self.grouping_reason,
            "temporal_window": list(self.temporal_window),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# PERCEPT EMBEDDING - Vector representation for correspondence
# =============================================================================


@dataclass(frozen=True)
class PerceptEmbedding:
    """
    Vector representation of a percept for correspondence matching.
    
    Embeddings accelerate correspondence but do not determine semantics.
    
    Fields:
        embedding_identity:    Unique identifier for this embedding
        
        percept_reference:     Reference to the original percept
        embedding_space:       Which vector space (e.g., "clip", "bert")
        embedding_model:       Model used to generate embeddings
        
        vector_reference:      Reference to the actual vector data
        confidence:            Confidence in embedding quality (0.0-1.0)
        uncertainty:           Uncertainty about embedding fidelity
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    embedding_identity: str
    
    # Percept reference (required)
    percept_reference: str              # Reference to the original percept
    
    # Embedding details (required)
    embedding_space: str                # e.g., "clip", "bert", "custom"
    embedding_model: str                # Model name/identifier
    
    # Vector info
    vector_reference: str               # Reference to actual vector data
    dimensions: int = 0                 # Number of dimensions
    
    # Quality metrics (required)
    confidence: float = 1.0             # Embedding quality confidence (0.0-1.0)
    uncertainty: float = 0.0            # Uncertainty about fidelity
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate embedding."""
        if not self.embedding_identity:
            raise ValueError("embedding_identity is required")
        if not self.percept_reference:
            raise ValueError("percept_reference is required")
    
    @classmethod
    def create(
        cls,
        percept_id: str,
        embedding_space: str,
        embedding_model: str,
        vector_ref: str,
        dimensions: int = 0,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "PerceptEmbedding":
        """Create a new percept embedding."""
        return cls(
            embedding_identity=f"embedding:{uuid.uuid4().hex[:24]}",
            percept_reference=percept_id,
            embedding_space=embedding_space,
            embedding_model=embedding_model,
            vector_reference=vector_ref,
            dimensions=dimensions,
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert embedding to dictionary."""
        return {
            "embedding_identity": self.embedding_identity,
            "percept_reference": self.percept_reference,
            "embedding_space": self.embedding_space,
            "embedding_model": self.embedding_model,
            "vector_reference": self.vector_reference,
            "dimensions": self.dimensions,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# PERCEPT CLASSIFICATION - Classification of a percept
# =============================================================================


@dataclass(frozen=True)
class PerceptClassification:
    """
    Classification record for a percept.
    
    Fields:
        classification_identity: Unique identifier
        
        percept_reference:       Reference to the classified percept
        percept_kind:            What kind of percept is this?
        
        classification_model:    Model used for classification
        confidence:              Confidence in classification (0.0-1.0)
        uncertainty:             Uncertainty about classification
        alternatives:            Alternative classifications considered
        
        provenance:              Origin tracking
    """
    
    # Identity (required)
    classification_identity: str
    
    # Percept reference (required)
    percept_reference: str
    
    # Classification result (required)
    percept_kind: str                    # Classified kind
    classification_model: str            # Model used
    
    # Quality metrics (required)
    confidence: float = 1.0              # Classification confidence (0.0-1.0)
    uncertainty: float = 0.0             # Uncertainty about classification
    
    alternatives: Tuple[str, ...] = field(default_factory=tuple)  # Alternative kinds
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate classification."""
        if not self.classification_identity:
            raise ValueError("classification_identity is required")
    
    @classmethod
    def create(
        cls,
        percept_id: str,
        classified_kind: str,
        model_name: str,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
        alternatives: Optional[List[str]] = None,
    ) -> "PerceptClassification":
        """Create a new classification."""
        return cls(
            classification_identity=f"classification:{uuid.uuid4().hex[:24]}",
            percept_reference=percept_id,
            percept_kind=classified_kind,
            classification_model=model_name,
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            alternatives=tuple(alternatives or []),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert classification to dictionary."""
        return {
            "classification_identity": self.classification_identity,
            "percept_reference": self.percept_reference,
            "percept_kind": self.percept_kind,
            "classification_model": self.classification_model,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "alternatives": list(self.alternatives),
        }


# =============================================================================
# PERCEPT REPRESENTATION - Comprehensive representation for grounding
# =============================================================================


@dataclass(frozen=True)
class PerceptRepresentation:
    """
    Comprehensive representation of a percept for correspondence.
    
    Combines symbolic, numerical, and vector features for robust matching.
    
    Fields:
        representation_identity: Unique identifier
        
        percept_reference:       Reference to the original percept
        modality:                Primary modality (vision, audio, etc.)
        
        # Feature types
        symbolic_features:       Symbolic descriptors (e.g., "red", "square")
        numerical_features:      Numerical measurements (e.g., 1.2, 0.5)
        vector_embeddings:       Vector representations for ML matching
        
        latent_features:         Latent space features (optional)
        modality_specific_features: Modality-specific descriptors
        
        confidence:              Confidence in representation (0.0-1.0)
        uncertainty:             Uncertainty about representation
        
        provenance:              Origin tracking
    """
    
    # Identity (required)
    representation_identity: str
    
    # Percept reference (required)
    percept_reference: str
    
    # Modality
    modality: str = "unknown"
    
    # Feature collections
    symbolic_features: Tuple[str, ...] = field(default_factory=tuple)
    numerical_features: Tuple[Tuple[str, float], ...] = field(default_factory=tuple)
    vector_embeddings: Tuple[PerceptEmbedding, ...] = field(default_factory=tuple)
    
    latent_features: Dict[str, Any] = field(default_factory=dict)
    modality_specific_features: Dict[str, Any] = field(default_factory=dict)
    
    # Quality metrics (required)
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate representation."""
        if not self.representation_identity:
            raise ValueError("representation_identity is required")
    
    @classmethod
    def create(
        cls,
        percept_id: str,
        modality: str = "unknown",
        symbolic_features: Optional[List[str]] = None,
        numerical_features: Optional[Dict[str, float]] = None,
        vector_embeddings: Optional[Tuple[PerceptEmbedding, ...]] = None,
        latent_features: Optional[Dict[str, Any]] = None,
    ) -> "PerceptRepresentation":
        """Create a new percept representation."""
        return cls(
            representation_identity=f"representation:{uuid.uuid4().hex[:24]}",
            percept_reference=percept_id,
            modality=modality,
            symbolic_features=tuple(symbolic_features or []),
            numerical_features=tuple((k, v) for k, v in (numerical_features or {}).items()),
            vector_embeddings=vector_embeddings or tuple(),
            latent_features=latent_features or {},
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert representation to dictionary."""
        return {
            "representation_identity": self.representation_identity,
            "percept_reference": self.percept_reference,
            "modality": self.modality,
            "symbolic_features": list(self.symbolic_features),
            "numerical_features": {k: v for k, v in self.numerical_features},
            "vector_embeddings_count": len(self.vector_embeddings),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


__all__ = [
    "PerceptKind",
    "Percept",
    "PerceptGroup",
    "PerceptEmbedding",
    "PerceptClassification",
    "PerceptRepresentation",
]