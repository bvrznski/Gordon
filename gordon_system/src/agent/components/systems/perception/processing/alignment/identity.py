# Perceptual Identity Alignment - Phase 5.2.2
# ===========================================

"""
Identity Alignment: Evaluates cross-source entity correspondence.

Identity alignment determines whether artifacts from different sources may
refer to the same underlying observed entity, without establishing final
canonical identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PERCEPTUAL IDENTITY ALIGNMENT - Entity correspondence evaluation
# =============================================================================


@dataclass(frozen=True)
class PerceptualIdentityAlignment:
    """
    Evaluation of whether artifacts refer to the same entity.
    
    Fields:
        alignment_identity:      Unique identifier for this alignment
        candidate_artifacts:     Which artifacts are being compared?
        correspondence_kind:     What kind of correspondence is proposed?
        supporting_features:     Features that support this correspondence
        conflicting_features:    Features that conflict with it
        confidence:              Confidence in the correspondence
        uncertainty:             Known limitations of this assessment
    """
    
    alignment_identity: str             # Unique ID
    
    candidate_artifacts: Tuple[str, ...]  # Artifact IDs being compared
    
    correspondence_kind: str = "UNKNOWN"  # e.g., "SAME_OBSERVED_ENTITY"
    
    supporting_features: Tuple[str, ...] = field(default_factory=tuple)  # Supporting evidence
    conflicting_features: Tuple[str, ...] = field(default_factory=tuple)  # Conflicting evidence
    
    temporal_scope: Optional[Tuple[float, float]] = None  # (start, end) time window
    
    confidence: float = 0.5           # Alignment confidence (0.0-1.0)
    uncertainty: float = 0.3          # Alignment uncertainty (0.0-1.0)
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Alignment history
    
    @property
    def is_candidate(self) -> bool:
        """Check if this is a valid correspondence candidate."""
        return len(self.candidate_artifacts) >= 2 and self.confidence > 0.3
    
    @property
    def has_supporting_evidence(self) -> bool:
        """Check if there's supporting evidence for correspondence."""
        return len(self.supporting_features) > 0
    
    @classmethod
    def create(
        cls,
        artifact_ids: List[str],
        correspondence_kind: str = "SAME_OBSERVED_ENTITY",
        temporal_scope: Optional[Tuple[float, float]] = None,
    ) -> "PerceptualIdentityAlignment":
        """Create a new identity alignment."""
        return cls(
            alignment_identity=f"identity:{uuid.uuid4().hex[:16]}",
            candidate_artifacts=tuple(artifact_ids),
            correspondence_kind=correspondence_kind,
            temporal_scope=temporal_scope,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alignment to dictionary."""
        return {
            "alignment_identity": self.alignment_identity,
            "candidate_artifacts": list(self.candidate_artifacts),
            "correspondence_kind": self.correspondence_kind,
            "supporting_features": list(self.supporting_features),
            "conflicting_features": list(self.conflicting_features),
            "temporal_scope": list(self.temporal_scope) if self.temporal_scope else None,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptualIdentityAlignment":
        """Create alignment from dictionary."""
        temporal = data.get("temporal_scope")
        return cls(
            alignment_identity=data.get("alignment_identity", str(uuid.uuid4())),
            candidate_artifacts=tuple(data.get("candidate_artifacts", [])),
            correspondence_kind=data.get("correspondence_kind", "UNKNOWN"),
            supporting_features=tuple(data.get("supporting_features", [])),
            conflicting_features=tuple(data.get("conflicting_features", [])),
            temporal_scope=tuple(temporal) if temporal else None,
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.3)),
        )