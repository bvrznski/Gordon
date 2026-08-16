# Perception Conflict - Phase 5.2.3
# =================================

"""
Perceptual Conflict: Preserved disagreement between evidence sources.

Integration preserves conflicts as first-class artifacts rather than
resolving them silently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import time
import uuid


# =============================================================================
# CONFLICT KIND - What type of conflict is this?
# =============================================================================


class ConflictKind(Enum):
    """
    Category of perceptual conflict.
    
    Kinds:
        CATEGORY_CONFLICT:      Different categorical assignments
        IDENTITY_CONFLICT:      Different identity assignments
        TEMPORAL_CONFLICT:      Different timing estimates
        SPATIAL_CONFLICT:       Different location/geometry
        STATE_CONFLICT:         Different state descriptions
        SOURCE_CONFLICT:        Disagreement about source origin
        SCHEMA_CONFLICT:        Incompatible structural schemas
        CONFIDENCE_CONFLICT:    Conflicting confidence assessments
        COMPLETENESS_CONFLICT:  Disagreeing on what's complete
    """
    
    CATEGORY = "category"
    IDENTITY = "identity"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    STATE = "state"
    SOURCE = "source"
    SCHEMA = "schema"
    CONFIDENCE = "confidence"
    COMPLETENESS = "completeness"


# =============================================================================
# PERCEPTUAL CONFLICT - Preserved disagreement
# =============================================================================


@dataclass(frozen=True)
class PerceptualConflict:
    """
    A conflict preserved from integration.
    
    Fields:
        conflict_identity: Unique identifier for this conflict
        participating_artifacts: Which artifacts disagree?
        conflicting_fields: Which fields are in conflict?
        conflicting_claims: Specific claims that differ
        supporting_evidence: Evidence for each claim
        alternatives: Alternative interpretations
        possible_causes: Potential causes of the conflict
        severity: How severe is this conflict? (0.0-1.0)
    """
    
    conflict_identity: str                 # Unique ID
    
    participating_artifacts: Tuple[str, ...]  # Artifact IDs involved
    
    conflicting_fields: Tuple[str, ...] = field(default_factory=tuple)  # Field names in conflict
    conflicting_claims: Tuple[str, ...] = field(default_factory=tuple)  # What differs?
    
    supporting_evidence: Dict[str, List[str]] = field(default_factory=dict)  # artifact_id -> evidence
    alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Alternative interpretations
    
    possible_causes: Tuple[str, ...] = field(default_factory=tuple)  # Hypothesized causes
    
    severity: float = 0.0                  # 0.0-1.0
    confidence: float = 1.0                # Confidence in conflict assessment
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def is_severe(self) -> bool:
        """Check if this conflict is severe."""
        return self.severity >= 0.7
    
    def has_alternatives(self) -> bool:
        """Check if alternative interpretations exist."""
        return len(self.alternatives) > 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conflict to dictionary."""
        return {
            "conflict_identity": self.conflict_identity,
            "participating_artifacts_count": len(self.participating_artifacts),
            "participating_artifacts": list(self.participating_artifacts),
            "conflicting_fields": list(self.conflicting_fields),
            "conflicting_claims": list(self.conflicting_claims),
            "supporting_evidence_count": len(self.supporting_evidence),
            "alternatives_count": len(self.alternatives),
            "possible_causes": list(self.possible_causes),
            "severity": self.severity,
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptualConflict":
        """Create conflict from dictionary."""
        return cls(
            conflict_identity=data.get("conflict_identity", str(uuid.uuid4())),
            participating_artifacts=tuple(data.get("participating_artifacts", [])),
            conflicting_fields=tuple(data.get("conflicting_fields", [])),
            conflicting_claims=tuple(data.get("conflicting_claims", [])),
        )


# =============================================================================
# CONFLICT ASSESSMENT - Evaluate conflicts
# =============================================================================


@dataclass(frozen=True)
class PerceptualConflictAssessment:
    """
    Assessment of a conflict's characteristics.
    
    Fields:
        assessment_identity: Unique identifier
        participating_artifacts: Artifacts involved
        compared_fields: Which fields were compared?
        conflict_kind: What type of conflict?
        conflict_magnitude: How large is the disagreement? (0.0-1.0)
        possible_source_causes: Source-related causes
        possible_processing_causes: Processing-related causes
    """
    
    assessment_identity: str
    
    participating_artifacts: Tuple[str, ...]
    
    compared_fields: Tuple[str, ...] = field(default_factory=tuple)
    conflict_kind: ConflictKind = ConflictKind.CATEGORY
    
    conflict_magnitude: float = 0.0        # 0.0-1.0
    possible_source_causes: Tuple[str, ...] = field(default_factory=tuple)
    possible_processing_causes: Tuple[str, ...] = field(default_factory=tuple)
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    provenance: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# PRESERVED CONFLICT - Conflict in result
# =============================================================================


@dataclass(frozen=True)
class PreservedPerceptualConflict:
    """
    A conflict that remains unresolved after integration.
    
    Fields:
        conflict_identity: Unique identifier
        source_artifacts: Original artifacts involved
        conflicting_claims: What differs?
        conflicting_fields: Fields in conflict
        supporting_evidence: Evidence per artifact
        alternatives: Alternative interpretations
        unresolved_questions: What still needs resolution?
        evidence_requirements: Additional evidence needed
    """
    
    conflict_identity: str
    
    source_artifacts: Tuple[str, ...]
    
    conflicting_claims: Tuple[str, ...] = field(default_factory=tuple)
    conflicting_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    supporting_evidence: Dict[str, List[str]] = field(default_factory=dict)  # artifact -> evidence
    alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    unresolved_questions: Tuple[str, ...] = field(default_factory=tuple)
    evidence_requirements: Tuple[str, ...] = field(default_factory=tuple)  # What's needed
    
    severity: float = 0.0
    confidence: float = 1.0
    uncertainty: float = 0.5
    
    provenance: Dict[str, Any] = field(default_factory=dict)