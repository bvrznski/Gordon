# Ambiguous Perception Integration - Phase 5.2.3
# ===============================================

"""
Ambiguous Integration: Integration with multiple materially plausible structures.

An AmbiguousIntegration preserves all plausible alternatives rather than
selecting one arbitrarily.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# AMBIGUOUS INTEGRATION STATE - Integration with multiple interpretations
# =============================================================================


@dataclass(frozen=True)
class AmbiguousPerceptionIntegration:
    """
    State of an ambiguous integration operation.
    
    Fields:
        integration_identity: Unique identifier for this integration attempt
        source_artifacts: Original artifacts involved
        plausible_structures: How many materially plausible structures?
        support_per_structure: Evidence supporting each structure
        conflict_per_structure: Conflicts per structure
        confidence_per_structure: Confidence per structure
        shared_uncertainty: Uncertainty common to all structures
        discriminating_evidence: What evidence could resolve ambiguity?
    """
    
    integration_identity: str              # Unique ID
    
    source_artifacts: Tuple[str, ...]      # Original artifacts
    
    plausible_structures: int = 2          # Number of alternative interpretations
    
    support_per_structure: Dict[int, Tuple[str, ...]] = field(default_factory=dict)  # structure_id -> evidence
    conflict_per_structure: Dict[int, Tuple[str, ...]] = field(default_factory=dict)  # structure_id -> conflicts
    confidence_per_structure: Dict[int, float] = field(default_factory=dict)  # structure_id -> confidence
    
    shared_uncertainty: float = 0.3        # Uncertainty common to all structures
    discriminating_evidence: Tuple[str, ...] = field(default_factory=tuple)  # Resolution evidence
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def get_structure_confidence(self, structure_id: int) -> float:
        """Get confidence for a specific structure."""
        return self.confidence_per_structure.get(structure_id, 0.5)
    
    def has_discriminating_evidence(self) -> bool:
        """Check if there's evidence to resolve the ambiguity."""
        return len(self.discriminating_evidence) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ambiguous integration state to dictionary."""
        return {
            "integration_identity": self.integration_identity,
            "source_artifacts_count": len(self.source_artifacts),
            "source_artifacts": list(self.source_artifacts),
            "plausible_structures": self.plausible_structures,
            "support_per_structure_count": len(self.support_per_structure),
            "conflict_per_structure_count": len(self.conflict_per_structure),
            "confidence_per_structure": dict(self.confidence_per_structure),
            "shared_uncertainty": self.shared_uncertainty,
            "discriminating_evidence_count": len(self.discriminating_evidence),
            "limitations": list(self.limitations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AmbiguousPerceptionIntegration":
        """Create ambiguous integration state from dictionary."""
        return cls(
            integration_identity=data.get("integration_identity", str(uuid.uuid4())),
            source_artifacts=tuple(data.get("source_artifacts", [])),
            plausible_structures=int(data.get("plausible_structures", 2)),
        )


# =============================================================================
# CORRESPONDENCE ALTERNATIVE - Alternative correspondence interpretation
# =============================================================================


@dataclass(frozen=True)
class CorrespondenceAlternative:
    """
    An alternative correspondence interpretation.
    
    Fields:
        alternative_identity: Unique identifier for this alternative
        participating_artifacts: Which artifacts are involved?
        proposed_correspondence_kind: What kind of correspondence?
        supporting_evidence: Evidence for this alternative
        conflicting_evidence: Evidence against this alternative
        confidence: Confidence in this alternative
        evidence_needed: What additional evidence would help?
    """
    
    alternative_identity: str              # Unique ID
    
    participating_artifacts: Tuple[str, ...]  # Artifact IDs involved
    
    proposed_correspondence_kind: str      # e.g., "same_entity_candidate"
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    conflicting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    
    confidence: float = 0.5                # 0.0-1.0
    evidence_needed: Tuple[str, ...] = field(default_factory=tuple)  # Resolution requirements
    
    provenance: Dict[str, Any] = field(default_factory=dict)