# Evidence Eligibility Assessment
# ===============================

"""
Evidence Eligibility: Determines which artifacts may participate in extraction.

This module implements the eligibility assessment that filters retrieved memory
artifacts before they can be used for semantic construction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# ELIGIBILITY KINDS - Why is an artifact eligible or not?
# =============================================================================


class EligibilityKind(Enum):
    """
    Kinds of eligibility decisions for memory artifacts.
    
    Every retrieved artifact shall receive an explicit eligibility assessment.
    """
    
    # Positive eligibility
    ELIGIBLE = "eligible"                     # Fully eligible for extraction
    
    CONDITIONALLY_ELIGIBLE = "conditionally_eligible"  # Eligible with constraints
    
    SUPERSEDED_BUT_RELEVANT = "superseded_but_relevant"  # Historical but relevant
    
    # Negative eligibility
    STALE = "stale"                           # Too old, may be outdated
    DEGRADED = "degraded"                     # Corrupted or incomplete
    RESTRICTED = "restricted"                 # Limited by authorization
    INCOMPATIBLE = "incompatible"             # Format/revision incompatible
    INVALID = "invalid"                       # Invalid content
    UNKNOWN = "unknown"                       # Cannot determine


# =============================================================================
# EVIDENCE ELIGIBILITY ASSESSMENT
# =============================================================================


@dataclass(frozen=True)
class EvidenceEligibility:
    """
    Eligibility assessment for a memory artifact.
    
    Determines whether an artifact may participate in semantic operations.
    The assessment is independent of the artifact's content - it's about
    whether the artifact can be safely used.
    
    Fields:
        eligibility_identity:   Unique ID for this assessment
        memory_artifact_id:     The artifact being assessed
        eligibility_kind:       Why is this eligible or not?
        
        # Validation checks
        source_validity:        Is the source system valid?
        revision_validity:      Are revisions consistent?
        supersession_state:     Is it superseded?
        provenance_integrity:   Can provenance be traced?
        
        # Relevance checks
        temporal_relevance:     Is this in the right time window?
        semantic_relevance:     Does this match the semantic scope?
        authorization_validity: Is access authorized?
        compatibility:          Is this revision compatible?
        
        # Quality metrics
        confidence:             Confidence in eligibility decision
        uncertainty:            Uncertainty about this assessment
        
        # Limitations and provenance
        limitations:            Known issues with this artifact
        provenance:             How was eligibility determined?
    """
    
    # Identity
    eligibility_identity: str                 # Unique ID for this assessment
    
    # Artifact reference
    memory_artifact_id: str                   # The artifact being assessed
    
    # Primary decision
    eligibility_kind: EligibilityKind         # Is it eligible or not?
    
    # Validation flags
    source_validity: bool = True              # Source system is valid
    revision_validity: bool = True            # Revision is consistent
    supersession_state_valid: bool = True     # Supersession state is known
    provenance_integrity: bool = True         # Provenance can be traced
    
    # Relevance flags
    temporal_relevant: bool = True            # In time window
    semantic_relevant: bool = True            # Matches semantic scope
    authorization_valid: bool = True          # Access authorized
    compatibility: bool = True                # Compatible with current revision
    
    # Quality metrics
    confidence: float = 1.0                   # Confidence in decision (0.0-1.0)
    uncertainty: float = 0.0                  # Uncertainty about decision
    
    # Diagnostics
    limitations: Tuple[str, ...] = field(default_factory=tuple)  # Known issues
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    def __post_init__(self):
        """Validate eligibility assessment."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
    
    @classmethod
    def eligible(
        cls,
        artifact_id: str,
        confidence: float = 1.0,
    ) -> "EvidenceEligibility":
        """Create an eligible assessment."""
        return cls(
            eligibility_identity=f"eligibility:{artifact_id}",
            memory_artifact_id=artifact_id,
            eligibility_kind=EligibilityKind.ELIGIBLE,
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def conditionally_eligible(
        cls,
        artifact_id: str,
        conditions: Tuple[str, ...],
        confidence: float = 0.9,
    ) -> "EvidenceEligibility":
        """Create a conditionally eligible assessment."""
        return cls(
            eligibility_identity=f"eligibility:{artifact_id}:conditional",
            memory_artifact_id=artifact_id,
            eligibility_kind=EligibilityKind.CONDITIONALLY_ELIGIBLE,
            limitations=conditions,
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def superseded_but_relevant(
        cls,
        artifact_id: str,
        superseding_artifact_id: str,
        confidence: float = 0.8,
    ) -> "EvidenceEligibility":
        """Create an assessment for superseded but relevant evidence."""
        return cls(
            eligibility_identity=f"eligibility:{artifact_id}:superseded",
            memory_artifact_id=artifact_id,
            eligibility_kind=EligibilityKind.SUPERSEDED_BUT_RELEVANT,
            limitations=(f"Superseded by: {superseding_artifact_id}",),
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def stale(
        cls,
        artifact_id: str,
        reason: str = "temporal_relevance",
        confidence: float = 0.5,
    ) -> "EvidenceEligibility":
        """Create a stale assessment."""
        return cls(
            eligibility_identity=f"eligibility:{artifact_id}:stale",
            memory_artifact_id=artifact_id,
            eligibility_kind=EligibilityKind.STALE,
            limitations=(f"Stale: {reason}",),
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def invalid(
        cls,
        artifact_id: str,
        reason: str = "content_validation_failed",
        confidence: float = 0.0,
    ) -> "EvidenceEligibility":
        """Create an invalid assessment."""
        return cls(
            eligibility_identity=f"eligibility:{artifact_id}:invalid",
            memory_artifact_id=artifact_id,
            eligibility_kind=EligibilityKind.INVALID,
            limitations=(f"Invalid: {reason}",),
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def restricted(
        cls,
        artifact_id: str,
        reason: str = "authorization_denied",
        confidence: float = 0.5,
    ) -> "EvidenceEligibility":
        """Create a restricted assessment."""
        return cls(
            eligibility_identity=f"eligibility:{artifact_id}:restricted",
            memory_artifact_id=artifact_id,
            eligibility_kind=EligibilityKind.RESTRICTED,
            limitations=(f"Restricted: {reason}",),
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @property
    def is_eligible(self) -> bool:
        """Check if the artifact is eligible for semantic operations."""
        return self.eligibility_kind in (
            EligibilityKind.ELIGIBLE,
            EligibilityKind.CONDITIONALLY_ELIGIBLE,
            EligibilityKind.SUPERSEDED_BUT_RELEVANT,
        )
    
    @property
    def can_participate(self) -> bool:
        """Check if the artifact may participate in semantic extraction."""
        return self.is_eligible and (
            self.source_validity and 
            self.revision_validity and 
            self.provenance_integrity
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary for serialization."""
        return {
            "eligibility_identity": self.eligibility_identity,
            "memory_artifact_id": self.memory_artifact_id,
            "eligibility_kind": self.eligibility_kind.value,
            "source_validity": self.source_validity,
            "revision_validity": self.revision_validity,
            "supersession_state_valid": self.supersession_state_valid,
            "provenance_integrity": self.provenance_integrity,
            "temporal_relevant": self.temporal_relevant,
            "semantic_relevant": self.semantic_relevant,
            "authorization_valid": self.authorization_valid,
            "compatibility": self.compatibility,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "limitations": list(self.limitations),
            "diagnostics": list(self.diagnostics),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceEligibility":
        """Create assessment from dictionary."""
        return cls(
            eligibility_identity=data.get("eligibility_identity", str(id(data))),
            memory_artifact_id=data.get("memory_artifact_id", "unknown"),
            eligibility_kind=EligibilityKind(data.get("eligibility_kind", "eligible")),
            source_validity=bool(data.get("source_validity", True)),
            revision_validity=bool(data.get("revision_validity", True)),
            supersession_state_valid=bool(data.get("supersession_state_valid", True)),
            provenance_integrity=bool(data.get("provenance_integrity", True)),
            temporal_relevant=bool(data.get("temporal_relevant", True)),
            semantic_relevant=bool(data.get("semantic_relevant", True)),
            authorization_valid=bool(data.get("authorization_valid", True)),
            compatibility=bool(data.get("compatibility", True)),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            limitations=tuple(data.get("limitations", [])),
            diagnostics=tuple(data.get("diagnostics", [])),
        )


__all__ = [
    "EligibilityKind",
    "EvidenceEligibility",
]